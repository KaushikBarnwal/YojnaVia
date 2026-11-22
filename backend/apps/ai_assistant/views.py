import logging
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .gemini_client import GeminiIntakeAssistant
from .models import IntakeConversation
from .schema import ALL_FIELDS, looks_like_sensitive_identifier
from .service import (
    apply_extraction,
    evaluate,
    get_or_create_conversation,
    heuristic_extract,
    next_question,
    relevant_fields,
    restart,
    snapshot,
    sync_profile,
    correct_field,
)

logger = logging.getLogger(__name__)

SENSITIVE_REFUSAL = (
    "Please don't share or enter your Aadhaar number or upload sensitive identity documents into this prototype. "
    "We use sample profiles only. Official requirements may differ by scheme and official government portals "
    "(such as MahaDBT) may require Aadhaar verification during formal submission, but here I only need general details "
    "like your age, course, and family income."
)
FALLBACK_CODES = ("llm_unavailable", "llm_timeout", "llm_malformed_output")
ERROR_MESSAGES = {
    "llm_unavailable": "The AI assistant is unavailable right now. I used simple matching for this message.",
    "llm_timeout": "The AI assistant took too long to respond. I used simple matching for this message.",
    "llm_malformed_output": "I could not read that reply properly. I used simple matching for this message.",
    "llm_rate_limited": "The AI assistant is busy. Please try again shortly.",
}
DONE_REPLY = (
    "Great, I have all the key details! Based on your profile, I have evaluated your eligibility "
    "against official Maharashtra government schemes below."
)
HISTORY_LIMIT = 20
LLM_HISTORY_TURNS = 6


def _error(code, message, http_status, retry_after=None):
    return Response(
        {"error": {"code": code, "message": message, "retry_after": retry_after}},
        status=http_status,
    )


def _server_error():
    return Response({"error": {"code": "server_error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


class IntakeChatView(APIView):
    throttle_scope = 'ai_intake'

    def post(self, request):
        try:
            message = _clean(request.data.get("message"))
            token = _clean(request.data.get("session_token"))
            if not message or not token:
                return _error("invalid_request", "message and session_token are required", status.HTTP_400_BAD_REQUEST)

            conv = get_or_create_conversation(token)
            relevant = relevant_fields()

            if looks_like_sensitive_identifier(message):
                return Response({
                    "reply": SENSITIVE_REFUSAL,
                    "session_token": token,
                    "state": snapshot(conv, relevant),
                    "next_question": next_question(conv, relevant),
                    "eligibility": None,
                    "error": None,
                })

            requested = [f for f in ALL_FIELDS if (conv.fields or {}).get(f, {}).get("status") != "known"]
            error = None
            llm_values = {}
            heuristic_values = {}
            natural_reply = None

            if requested:
                history = list(conv.history or [])[-LLM_HISTORY_TURNS:]
                extract_res = GeminiIntakeAssistant().extract(message, requested, history)
                if len(extract_res) == 4:
                    values, code, retry_after, natural_reply = extract_res
                else:
                    values, code, retry_after = extract_res
                    natural_reply = None

                if code is None:
                    llm_values = values or {}
                else:
                    error = {
                        "code": code,
                        "message": ERROR_MESSAGES.get(code, ERROR_MESSAGES["llm_unavailable"]),
                        "retry_after": retry_after,
                    }
                    if code in FALLBACK_CODES:
                        heuristic_values = heuristic_extract(message)

            if llm_values:
                apply_extraction(conv, llm_values, "user_message", 0.8)
            if heuristic_values:
                apply_extraction(conv, heuristic_values, "heuristic", 0.6)

            nq = next_question(conv, relevant)
            eligibility = evaluate(conv, relevant) if nq is None else None

            GREETING_WORDS = {"hi", "hello", "hey", "namaste", "pranam", "greetings"}
            msg_clean = message.strip().lower()
            is_pure_greeting = (
                msg_clean in GREETING_WORDS 
                or any(msg_clean == f"{w}!" or msg_clean == f"{w}." for w in GREETING_WORDS)
                or (len(msg_clean.split()) <= 2 and any(msg_clean.startswith(w) for w in GREETING_WORDS))
            )

            if nq is None:
                reply = DONE_REPLY
            elif natural_reply and not natural_reply.lower().startswith("thanks."):
                reply = natural_reply
            elif is_pure_greeting and not llm_values and not heuristic_values:
                reply = (
                    "Namaste! Welcome to YOJNAVIA. To help you discover the right scholarships and government schemes in Maharashtra, "
                    f"could you tell me a little about yourself—to start with, {nq['text'].lower()}"
                )
            else:
                FRIENDLY_PROMPTS = {
                    "age": "could you tell me how old you are?",
                    "state": "which state do you currently live in?",
                    "district": "which district in Maharashtra do you reside in?",
                    "occupation": "what do you currently do (e.g. student, farmer, employed)?",
                    "education_level": "what is your current or highest education level?",
                    "income_band": "roughly what is your family's annual household income?",
                }
                q_text = FRIENDLY_PROMPTS.get(nq["field"], nq["text"].lower() if nq["text"][0].isupper() else nq["text"])
                if llm_values or heuristic_values:
                    reply = f"Got it, recorded! To check your scheme eligibility, {q_text}"
                else:
                    reply = f"To check what scholarships apply to you, {q_text}"

            conv.history = (list(conv.history or []) + [
                {"role": "user", "text": message},
                {"role": "assistant", "text": reply},
            ])[-HISTORY_LIMIT:]
            conv.save()
            sync_profile(token, conv, relevant)

            return Response({
                "reply": reply,
                "session_token": token,
                "state": snapshot(conv, relevant),
                "next_question": nq,
                "eligibility": eligibility,
                "error": error,
            })
        except Exception:
            logger.exception("Intake chat failed")
            return _server_error()


class IntakeStateView(APIView):
    def get(self, request):
        try:
            token = _clean(request.query_params.get("session_token"))
            if not token:
                return _error("invalid_request", "session_token is required", status.HTTP_400_BAD_REQUEST)
            conv = IntakeConversation.objects.filter(session_token=token).first()
            if conv is None:
                return _error("not_found", "No intake session found for this token", status.HTTP_404_NOT_FOUND)
            relevant = relevant_fields()
            return Response({
                "session_token": token,
                "state": snapshot(conv, relevant),
                "next_question": next_question(conv, relevant),
            })
        except Exception:
            logger.exception("Intake state failed")
            return _server_error()


class IntakeCorrectView(APIView):
    def post(self, request):
        try:
            token = _clean(request.data.get("session_token"))
            field = _clean(request.data.get("field"))
            if not token or not field or "value" not in request.data:
                return _error("invalid_request", "session_token, field and value are required", status.HTTP_400_BAD_REQUEST)
            conv = IntakeConversation.objects.filter(session_token=token).first()
            if conv is None:
                return _error("not_found", "No intake session found for this token", status.HTTP_404_NOT_FOUND)
            try:
                correct_field(conv, field, request.data.get("value"))
            except ValueError as exc:
                return _error("invalid_value", str(exc), status.HTTP_400_BAD_REQUEST)
            relevant = relevant_fields()
            sync_profile(token, conv, relevant)
            return Response({
                "session_token": token,
                "state": snapshot(conv, relevant),
                "next_question": next_question(conv, relevant),
            })
        except Exception:
            logger.exception("Intake correct failed")
            return _server_error()


class IntakeRestartView(APIView):
    def post(self, request):
        try:
            token = _clean(request.data.get("session_token"))
            if not token:
                return _error("invalid_request", "session_token is required", status.HTTP_400_BAD_REQUEST)
            conv = get_or_create_conversation(token)
            restart(conv)
            relevant = relevant_fields()
            return Response({
                "session_token": token,
                "state": snapshot(conv, relevant),
                "next_question": next_question(conv, relevant),
            })
        except Exception:
            logger.exception("Intake restart failed")
            return _server_error()
