import logging
import uuid
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
    validate_field_value,
)
from .sarvam_speech import SarvamSpeechService, CANONICAL_MARATHI_DEMO, CANONICAL_HINDI_DEMO

HIGH_RISK_FIELDS = (
    "income_band",
    "age",
    "social_category",
    "disability_status",
    "education_level",
    "state",
    "district",
    "occupation",
    "family_members",
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
                raw_text = nq.get("text", "")
                q_text = FRIENDLY_PROMPTS.get(nq.get("field"), raw_text.lower() if raw_text and raw_text[0].isupper() else raw_text)
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


class GrSamplesListView(APIView):
    """
    Returns authentic Maharashtra Government Resolutions for 1-click test exploration.
    GET /api/v1/assistant/gr_samples/
    """
    def get(self, request):
        from .gr_interpreter import GovernmentResolutionInterpreterService
        samples = GovernmentResolutionInterpreterService.get_sample_grs()
        return Response({"samples": samples})


class InterpretGrView(APIView):
    """
    Converts complex Marathi / English Government Resolution text into an actionable blueprint.
    POST /api/v1/assistant/interpret_gr/
    """
    def post(self, request):
        from .gr_interpreter import GovernmentResolutionInterpreterService
        source_text = request.data.get("source_text")
        user_notes = request.data.get("user_notes")
        lang = request.data.get("preferred_language", "en")

        if not source_text or not source_text.strip():
            return Response({"error": "source_text is required"}, status=status.HTTP_400_BAD_REQUEST)

        result = GovernmentResolutionInterpreterService.interpret_gr(
            source_text=source_text,
            user_notes=user_notes,
            preferred_language=lang
        )
        return Response(result)


class VoiceIntakeView(APIView):
    """
    Voice-Based Citizen Intake using Sarvam AI Saaras v4 STT.
    POST /api/v1/intake/voice/ or /api/v1/assistant/voice_intake/
    
    Pipeline:
    Citizen audio -> Validated upload -> Sarvam Saaras v4 -> Native-script transcript
    -> Gemini / Heuristic extraction -> Structured profile (unconfirmed)
    -> Citizen review & confirmation safeguards -> Deterministic eligibility engine.
    """

    def post(self, request):
        try:
            token = _clean(request.data.get("session_token") or request.query_params.get("session_token"))
            if not token:
                return _error("invalid_request", "session_token is required", status.HTTP_400_BAD_REQUEST)

            uploaded_audio = request.FILES.get("audio") or request.FILES.get("file")
            language_code = request.data.get("language_code", "unknown")
            is_demo = str(request.data.get("is_demo", "")).lower() in ("true", "1")
            demo_scenario = request.data.get("demo_scenario", "marathi")

            # 1. Speech-to-Text Transcription via Sarvam AI
            if is_demo or not uploaded_audio:
                if not uploaded_audio and not is_demo:
                    return _error("missing_audio", "No audio file provided. Please record or upload your voice note.", status.HTTP_400_BAD_REQUEST)

                # 1-Click Demo Voice Simulation
                if demo_scenario == "hindi":
                    transcript = CANONICAL_HINDI_DEMO
                    detected_lang = "hi-IN"
                else:
                    transcript = CANONICAL_MARATHI_DEMO
                    detected_lang = "mr-IN"

                stt_result = {
                    "transcript": transcript,
                    "language_code": detected_lang,
                    "request_id": f"sim_sarvam_{uuid.uuid4().hex[:8]}",
                    "model": "saaras:v4",
                    "is_simulated": True,
                    "pilot_mode": True,
                    "pilot_notice": "Pilot Mode: Simulated Sarvam Saaras v4 speech recognition."
                }
            else:
                try:
                    stt_result = SarvamSpeechService.transcribe(
                        uploaded_file=uploaded_audio,
                        language_code=language_code
                    )
                except ValueError as val_err:
                    return _error("invalid_audio", str(val_err), status.HTTP_400_BAD_REQUEST)
                except TimeoutError as t_err:
                    return _error("stt_timeout", str(t_err), status.HTTP_504_GATEWAY_TIMEOUT)
                except RuntimeError as r_err:
                    return _error("stt_error", str(r_err), status.HTTP_502_BAD_GATEWAY)

            transcript = stt_result.get("transcript", "").strip()
            if not transcript:
                return Response({
                    "success": False,
                    "error": "No speech detected in audio. Please speak clearly into the microphone.",
                    "stt": stt_result
                }, status=status.HTTP_400_BAD_REQUEST)

            # 2. Check for sensitive identifiers (Aadhaar rejection)
            if looks_like_sensitive_identifier(transcript):
                return Response({
                    "success": False,
                    "reply": SENSITIVE_REFUSAL,
                    "session_token": token,
                    "transcript": transcript,
                    "stt": stt_result,
                    "is_sensitive_refusal": True
                })

            # 3. Feed Transcript into Extraction Pipeline (Gemini with Heuristic Fallback)
            conv = get_or_create_conversation(token)
            relevant = relevant_fields()
            requested = [f for f in ALL_FIELDS if (conv.fields or {}).get(f, {}).get("status") != "known"]

            llm_values = {}
            heuristic_values = {}
            natural_reply = None

            if requested:
                history = list(conv.history or [])[-LLM_HISTORY_TURNS:]
                extract_res = GeminiIntakeAssistant().extract(transcript, requested, history)
                if len(extract_res) == 4:
                    values, code, retry_after, natural_reply = extract_res
                else:
                    values, code, retry_after = extract_res
                    natural_reply = None

                if code is None:
                    llm_values = values or {}
                elif code in FALLBACK_CODES:
                    heuristic_values = heuristic_extract(transcript)
            else:
                heuristic_values = heuristic_extract(transcript)

            # Combine extracted candidates (never overwrite confirmed fields)
            extracted_candidates = {}
            if llm_values:
                extracted_candidates.update(llm_values)
            if heuristic_values:
                extracted_candidates.update(heuristic_values)

            # Store in conversation as proposed values (user_confirmed=False)
            if extracted_candidates:
                apply_extraction(conv, extracted_candidates, "voice_sarvam", 0.85)

            # 4. Confirmation Safeguards: Highlight High-Risk Fields
            # High-risk fields must be explicitly confirmed by citizen before permanent profile save
            high_risk_detected = []
            for field, val in extracted_candidates.items():
                if field in HIGH_RISK_FIELDS:
                    high_risk_detected.append({
                        "field": field,
                        "value": val,
                        "display_name": field.replace("_", " ").title(),
                        "user_confirmed": False,
                        "requires_confirmation": True
                    })

            # Add to conversation history
            conv.history = (list(conv.history or []) + [
                {"role": "user", "text": transcript, "source": "voice_sarvam"},
            ])[-HISTORY_LIMIT:]
            conv.save()

            nq = next_question(conv, relevant)
            current_snapshot = snapshot(conv, relevant)

            return Response({
                "success": True,
                "transcript": transcript,
                "detected_language": stt_result.get("language_code", "mr-IN"),
                "stt_metadata": stt_result,
                "extracted_fields": extracted_candidates,
                "high_risk_fields": high_risk_detected,
                "requires_confirmation": len(high_risk_detected) > 0,
                "natural_reply": natural_reply,
                "session_token": token,
                "state": current_snapshot,
                "next_question": nq,
                "pilot_notice": "Pilot Feature: Marathi & Hindi Voice Intake powered by Sarvam AI Saaras v4."
            })

        except Exception:
            logger.exception("Voice intake processing failed")
            return _server_error()


class ConfirmVoiceIntakeView(APIView):
    """
    Explicit Citizen Confirmation Step.
    POST /api/v1/intake/confirm_voice/
    
    Ensures that high-risk voice-extracted fields (income, age, caste, district)
    are verified by the citizen before writing to StudentProfile and running eligibility.
    """

    def post(self, request):
        try:
            token = _clean(request.data.get("session_token"))
            confirmed_fields = request.data.get("confirmed_fields", {})
            if not token or not isinstance(confirmed_fields, dict):
                return _error("invalid_request", "session_token and confirmed_fields dict are required", status.HTTP_400_BAD_REQUEST)

            conv = get_or_create_conversation(token)
            relevant = relevant_fields()

            # Validate and mark confirmed
            for field, val in confirmed_fields.items():
                if field not in ALL_FIELDS:
                    continue
                try:
                    checked = validate_field_value(field, val)
                    new_fields = dict(conv.fields or {})
                    new_fields[field] = {
                        "value": checked,
                        "status": "known",
                        "confidence": 1.0,
                        "user_confirmed": True,
                        "source": "user_confirmed"
                    }
                    conv.fields = new_fields
                except (ValueError, Exception) as exc:
                    return _error("invalid_field", f"Invalid value for {field}: {str(exc)}", status.HTTP_400_BAD_REQUEST)

            conv.save()
            # Synchronize confirmed attributes to StudentProfile
            sync_profile(token, conv, relevant)

            # Deterministic eligibility evaluation on confirmed profile
            nq = next_question(conv, relevant)
            eligibility = evaluate(conv, relevant)

            return Response({
                "success": True,
                "session_token": token,
                "state": snapshot(conv, relevant),
                "next_question": nq,
                "eligibility": eligibility,
                "message": "Profile fields confirmed successfully. Deterministic scheme matching updated."
            })

        except Exception:
            logger.exception("Confirm voice intake failed")
            return _server_error()


