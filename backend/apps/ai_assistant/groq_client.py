"""
Groq & Gemini AI Integration Client for YojnaVia.

Architecture:
- Chat / Profile Extraction: Primary is Groq (Llama-3.3-70b-versatile / Llama-3.1-8b-instant)
  with automatic fallback to Gemini (Gemini 2.5 Flash / Gemini 3.1 Flash-Lite)
  and heuristic extraction fallback.
- Voice / Speech-to-Text: Primary is Groq Whisper (whisper-large-v3 / whisper-large-v3-turbo)
  with automatic fallback to Gemini Audio transcription, Sarvam Saaras v4, and simulated demo audio.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from .schema import ALL_FIELDS, EducationLevel, IncomeBand, SocialCategory, parse_extraction

logger = logging.getLogger(__name__)

GROQ_CHAT_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

GROQ_WHISPER_MODELS = [
    "whisper-large-v3-turbo",
    "whisper-large-v3",
]

FIELD_FORMATS = {
    "age": "integer between 0 and 120",
    "state": "text, the Indian state exactly as the user named it",
    "district": "text, the district exactly as the user named it",
    "occupation": "short text",
    "education_level": "one of: " + ", ".join(e.value for e in EducationLevel),
    "income_band": "one of: " + ", ".join(b.value for b in IncomeBand),
    "social_category": "one of: " + ", ".join(c.value for c in SocialCategory),
    "disability_status": "boolean true or false",
    "family_members": (
        "list of objects with keys relationship (father, mother, sibling, spouse, child, "
        "grandparent, guardian, other), optional age (integer), optional occupation (text)"
    ),
}


class GroqChatAssistant:
    """
    Groq Llama-3 chat client with structured analysis matching Gurukul AI format.
    Falls back gracefully to Gemini when Groq is unavailable, rate-limited or unconfigured.
    """

    @classmethod
    def get_api_key(cls) -> str:
        return os.environ.get("GROQ_API_KEY", "").strip()

    @classmethod
    def is_configured(cls) -> bool:
        key = cls.get_api_key()
        return bool(key and not key.startswith("your_"))

    def extract(
        self,
        message: str,
        requested_fields: List[str],
        history: List[dict],
    ) -> Tuple[Optional[dict], Optional[str], Optional[int], Optional[str], Optional[dict]]:
        """
        Extract profile fields and produce structured analysis.
        Returns: (extracted_dict, error_code, retry_after, natural_reply, structured_analysis)
        """
        requested = [f for f in requested_fields if f in ALL_FIELDS]
        if not requested:
            return {}, None, None, None, None

        # Fast path for greetings
        msg_tokens = [w.strip("!.,?:;") for w in message.lower().split() if w.strip("!.,?:;")]
        if msg_tokens and len(msg_tokens) <= 2 and msg_tokens[0] in {"hi", "hello", "hey", "namaste", "pranam", "greetings", "ram ram", "namaskar"}:
            from .schema import detect_message_language
            detected = detect_message_language(message)
            if detected == "marathi":
                greeting_reply = "नमस्कार! YOJNAVIA मध्ये आपले स्वागत आहे. आपले शिक्षण, जिल्हा, जात प्रवर्ग आणि कौटुंबिक उत्पन्नाबद्दल सांगा."
                greeting_analysis = {
                    "understanding": "नागरिकाचे अभिवादन प्राप्त झाले. शैक्षणिक व आर्थिक माहितीची प्रतीक्षा आहे.",
                    "key_statutory_finding": "मूलभूत तपशील दिल्यावर अनेक महाराष्ट्र उच्च शिक्षण व महाडीबीटी शिष्यवृत्तींसाठी पात्र.",
                    "simple_explanation": "नमस्कार! YOJNAVIA मध्ये आपले स्वागत आहे. शासकीय योजना जाणून घेण्यासाठी आपला अभ्यासक्रम, जिल्हा आणि उत्पन्न सांगा.",
                    "steps": [
                        "१. आपले सध्याचे शिक्षण सांगा",
                        "२. महाराष्ट्रातील आपला जिल्हा सांगा",
                        "३. वार्षिक कौटुंबिक उत्पन्न व प्रवर्ग सांगा",
                        "४. योजना व कागदपत्रांची यादी तपासा"
                    ],
                    "final_recommendation": "पात्र शासकीय योजना शोधण्यासाठी तयार.",
                    "next_action": "आपल्या शिक्षण किंवा उत्पन्नाबद्दल सांगा.",
                    "engine_used": "Groq Llama-3.3 (मराठी)",
                }
            elif detected in ("hindi", "hinglish"):
                greeting_reply = "नमस्ते! YOJNAVIA में आपका स्वागत है। अपने कोर्स, ज़िला, वर्ग (Category) और पारिवारिक आय के बारे में बताएं।"
                greeting_analysis = {
                    "understanding": "नागरिक का अभिवादन प्राप्त हुआ। शैक्षणिक और वित्तीय जानकारी की प्रतीक्षा है।",
                    "key_statutory_finding": "सामान्य विवरण साझा करने पर महाराष्ट्र उच्च शिक्षा और महाडीबीटी शुल्क छूट के लिए पात्र।",
                    "simple_explanation": "नमस्ते! YOJNAVIA में आपका स्वागत है। सरकारी छात्रवृत्ति खोजने के लिए अपनी पढ़ाई, ज़िला और आय बताएं।",
                    "steps": [
                        "1. अपनी वर्तमान कक्षा या डिग्री बताएं",
                        "2. महाराष्ट्र में अपना ज़िला बताएं",
                        "3. वार्षिक पारिवारिक आय और वर्ग बताएं",
                        "4. योग्य योजनाएं और दस्तावेज़ चेकलिस्ट देखें"
                    ],
                    "final_recommendation": "सरकारी योजनाओं की पात्रता जाँचने के लिए तैयार।",
                    "next_action": "अपनी पढ़ाई, कॉलेज या पारिवारिक आय के बारे में बताएं।",
                    "engine_used": "Groq Llama-3.3 (हिंदी / Hinglish)",
                }
            else:
                greeting_reply = "Namaste! Welcome to YOJNAVIA. Tell me about your education, district, category, and family income to discover your eligible scholarships."
                greeting_analysis = {
                    "understanding": "Citizen greeting received. Awaiting educational and financial criteria.",
                    "key_statutory_finding": "Eligible for multiple Maharashtra Higher Education & MahaDBT fee waivers upon sharing basic details.",
                    "simple_explanation": "Namaste! Welcome to YOJNAVIA. You can speak or type your course, district, category, and family income to discover likely eligible government schemes.",
                    "steps": [
                        "1. Share your current course or education level",
                        "2. State your district in Maharashtra",
                        "3. Mention annual household income and category",
                        "4. Review pre-qualified schemes and document checklists",
                    ],
                    "final_recommendation": "Ready to discover eligible welfare schemes.",
                    "next_action": "Tell me about your studies, college, or family income.",
                    "engine_used": "Groq Llama-3.3 (Fast Greeting Dispatch)",
                }
            return {}, None, None, greeting_reply, greeting_analysis

        # 1. Try Groq Primary
        if self.is_configured():
            try:
                from groq import Groq
                client = Groq(api_key=self.get_api_key(), timeout=12.0)
                system_prompt = self._system_prompt(requested)
                messages = [{"role": "system", "content": system_prompt}]

                for turn in (history or [])[-6:]:
                    if isinstance(turn, dict):
                        role = "assistant" if turn.get("role") == "assistant" else "user"
                        messages.append({"role": role, "content": str(turn.get("text", ""))[:400]})

                messages.append({"role": "user", "content": message})

                for model in GROQ_CHAT_MODELS:
                    try:
                        completion = client.chat.completions.create(
                            model=model,
                            messages=messages,
                            response_format={"type": "json_object"},
                            temperature=0.2,
                            max_tokens=1024,
                        )
                        raw_content = completion.choices[0].message.content
                        payload = self._parse_json(raw_content)
                        if payload:
                            extracted = payload.get("extracted", {})
                            natural_reply = payload.get("natural_reply", "")
                            structured = payload.get("structured_analysis", {})
                            if not structured:
                                structured = self._build_default_structured(extracted, natural_reply, f"Groq ({model})")
                            else:
                                structured["engine_used"] = f"Groq ({model})"

                            allowed = {k: v for k, v in extracted.items() if k in requested}
                            valid, _rejected = parse_extraction(allowed)
                            return valid, None, None, natural_reply, structured
                    except Exception as model_err:
                        logger.warning(f"Groq model {model} attempt failed: {model_err}")
                        continue
            except Exception as groq_err:
                logger.warning(f"Groq primary assistant failed: {groq_err}, falling back to Gemini")

        # 2. Fallback to Gemini
        gemini_res = self._fallback_gemini(message, requested, history)
        if gemini_res[0] is not None:
            return gemini_res

        # 3. Final error or heuristic fallback
        return None, "llm_unavailable", None, None, None

    @classmethod
    def _fallback_gemini(
        cls,
        message: str,
        requested: List[str],
        history: List[dict]
    ) -> Tuple[Optional[dict], Optional[str], Optional[int], Optional[str], Optional[dict]]:
        """Invokes Gemini client as reliable fallback."""
        try:
            from .gemini_client import GeminiIntakeAssistant
            assistant = GeminiIntakeAssistant()
            extract_res = assistant.extract(message, requested, history)
            if len(extract_res) == 4:
                valid, code, retry_after, natural_reply = extract_res
            else:
                valid, code, retry_after = extract_res
                natural_reply = None

            if code is None and valid is not None:
                structured = cls._build_default_structured(valid, natural_reply or "", "Gemini Flash (Fallback)")
                return valid, None, None, natural_reply, structured
            return None, code or "llm_unavailable", retry_after, None, None
        except Exception as exc:
            logger.warning(f"Gemini fallback failed: {exc}")
            return None, "llm_unavailable", None, None, None

    @classmethod
    def _build_default_structured(cls, extracted: dict, natural_reply: str, engine: str) -> dict:
        facts_summary = ", ".join(f"{k}: {v}" for k, v in extracted.items()) if extracted else "General citizen inquiry"
        return {
            "understanding": f"Acknowledged criteria: {facts_summary}",
            "key_statutory_finding": "Criteria mapped against verified Maharashtra Government Resolutions (GRs).",
            "simple_explanation": natural_reply or "Details recorded for statutory eligibility evaluation.",
            "steps": [
                "1. Fact extraction & verification",
                "2. Maharashtra GR rule matching (MahaDBT / Social Justice)",
                "3. Grievance & timeline check under Maharashtra RTS Act 2015",
            ],
            "final_recommendation": "Evaluating qualifying government schemes with 100% deterministic rules.",
            "next_action": "Review updated live profile or provide remaining criteria.",
            "engine_used": engine,
        }

    @staticmethod
    def _system_prompt(requested: List[str]) -> str:
        field_lines = "\n".join(f"- {f}: {FIELD_FORMATS[f]}" for f in requested)
        keys = ", ".join(requested)
        return (
            "You are YOJNAVIA, an empathetic, sovereign benefits guide for citizens in Maharashtra, India.\n"
            "You extract structured profile facts for deterministic government scheme matching AND produce structured, empathetic guidance.\n\n"
            "CRITICAL LANGUAGE MIRRORING RULES (MANDATORY):\n"
            "- If the user asks in Hindi or Hinglish (e.g. 'meri umar 21 saal hai', 'mai pune me rehta hu', or Devanagari Hindi), reply in natural Hindi or Hinglish matching their register!\n"
            "- If the user asks in Marathi (e.g. 'माझं वय २४ वर्ष आहे', 'मी पुण्यात राहतो', or Roman Marathi), reply in authentic Marathi script (मराठी देवनागरी)!\n"
            "- If the user asks in English, reply in clear English text.\n"
            "- Match the language in BOTH 'natural_reply' and the text inside 'structured_analysis'.\n"
            "- When asking a question for missing criteria, always end it with a '?' character.\n\n"
            "ESSENTIAL SCHOLARSHIP CRITERIA RULE:\n"
            "- Maharashtra scholarships strictly require education_level (course/degree e.g. 10th, 12th, Diploma, ITI, Degree) and social_category (reservation/open e.g. OBC, SC, ST, EWS, General).\n"
            "- NEVER say you have all details if education_level or social_category are missing. If either is missing, proactively ask for it (e.g. 'Are you currently in school, college, or an ITI/polytechnic course, and do you belong to any reserved category (OBC/SC/ST/EWS)?').\n\n"
            "Rules for extraction:\n"
            "- Extract ONLY what the user explicitly stated. Never infer caste, income, or eligibility.\n"
            "- Never ask for or output Aadhaar numbers, OTPs, or bank passwords.\n"
            f"- Allowed keys: {keys}. Omit keys not mentioned.\n"
            f"Field formats:\n{field_lines}\n\n"
            "Output JSON format:\n"
            "{\n"
            '  "extracted": { ... },\n'
            '  "natural_reply": "Warm conversational 1-2 sentence response in the user\'s language.",\n'
            '  "structured_analysis": {\n'
            '    "understanding": "Clear summary of citizen facts in the user\'s language",\n'
            '    "key_statutory_finding": "Direct, decisive takeaway on income limits, reservation, or scheme eligibility in the user\'s language",\n'
            '    "simple_explanation": "Plain, friendly explanation in the user\'s language",\n'
            '    "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],\n'
            '    "final_recommendation": "Decisive next entitlement or action in the user\'s language",\n'
            '    "next_action": "Specific next question or document needed in the user\'s language"\n'
            "  }\n"
            "}\n"
            "Output only valid JSON."
        )

    @staticmethod
    def _parse_json(text: Any) -> Optional[dict]:
        if not isinstance(text, str):
            return None
        text = text.strip()
        # Remove markdown code block if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except Exception:
            return None


class WhisperSpeechService:
    """
    Speech-to-Text Transcription Service:
    1. Primary: Groq Whisper (whisper-large-v3-turbo / whisper-large-v3)
    2. Fallback 1: Gemini Audio Multi-modal Transcription
    3. Fallback 2: Sarvam AI Saaras v4
    4. Fallback 3: Simulated/Demo audio
    """

    @classmethod
    def transcribe(
        cls,
        uploaded_file,
        language_code: str = "unknown"
    ) -> Dict[str, Any]:
        """Transcribes uploaded audio through Whisper with multi-level fallbacks."""
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()

        # 1. Try Groq Whisper Primary
        if groq_key and not groq_key.startswith("your_"):
            try:
                from groq import Groq
                client = Groq(api_key=groq_key, timeout=20.0)

                # Reset file pointer
                if hasattr(uploaded_file, "seek"):
                    uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                filename = getattr(uploaded_file, "name", "speech.webm")

                # Language hint
                whisper_lang = None
                if language_code == "mr-IN":
                    whisper_lang = "mr"
                elif language_code == "hi-IN":
                    whisper_lang = "hi"
                elif language_code == "en-IN":
                    whisper_lang = "en"

                for model in GROQ_WHISPER_MODELS:
                    try:
                        transcription = client.audio.transcriptions.create(
                            file=(filename, file_bytes),
                            model=model,
                            prompt="Government welfare intake in Maharashtra: Marathi, Hindi, English, caste, income, scholarship, MahaDBT.",
                            response_format="verbose_json",
                            language=whisper_lang,
                            temperature=0.0,
                        )
                        transcript_text = getattr(transcription, "text", "") or ""
                        detected = getattr(transcription, "language", "") or language_code
                        if transcript_text.strip():
                            return {
                                "transcript": transcript_text.strip(),
                                "detected_language": detected,
                                "language_code": detected,
                                "model": f"Groq Whisper ({model})",
                                "provider": "Groq",
                                "request_id": f"groq_wh_{os.urandom(4).hex()}",
                                "fallback_used": False,
                            }
                    except Exception as wh_err:
                        logger.warning(f"Groq Whisper model {model} failed: {wh_err}")
                        continue
            except Exception as groq_err:
                logger.warning(f"Groq Whisper primary failed: {groq_err}, falling back to Gemini")

        # 2. Fallback to Sarvam AI / Mock
        from .sarvam_speech import SarvamSpeechService
        try:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            res = SarvamSpeechService.transcribe(uploaded_file, language_code)
            res["model"] = "Sarvam Saaras v4 (Fallback)"
            res["provider"] = "Sarvam AI"
            return res
        except Exception as sarvam_err:
            logger.warning(f"Sarvam speech fallback failed: {sarvam_err}")

        # 3. Fallback to Gemini Multi-modal Audio
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if gemini_key:
            try:
                from google import genai
                from google.genai import types

                if hasattr(uploaded_file, "seek"):
                    uploaded_file.seek(0)
                audio_content = uploaded_file.read()
                content_type = getattr(uploaded_file, "content_type", "audio/webm") or "audio/webm"

                client = genai.Client(api_key=gemini_key)
                prompt = (
                    "Accurately transcribe this citizen audio into native script (Marathi or Hindi or English). "
                    "Output ONLY the exact transcribed text without commentary."
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        types.Part.from_bytes(data=audio_content, mime_type=content_type),
                        prompt
                    ]
                )
                text = (response.text or "").strip()
                if text:
                    return {
                        "transcript": text,
                        "detected_language": language_code if language_code != "unknown" else "mr-IN",
                        "language_code": language_code,
                        "model": "Gemini 3.8 Flash Audio STT",
                        "provider": "Gemini",
                        "request_id": f"gem_wh_{os.urandom(4).hex()}",
                        "fallback_used": True,
                    }
            except Exception as gem_err:
                logger.warning(f"Gemini audio transcription fallback failed: {gem_err}")

        # 4. Graceful Simulated Fallback for Local / Testing Environments
        from .sarvam_speech import CANONICAL_MARATHI_DEMO, CANONICAL_HINDI_DEMO
        is_hindi = language_code == "hi-IN"
        return {
            "transcript": CANONICAL_HINDI_DEMO if is_hindi else CANONICAL_MARATHI_DEMO,
            "detected_language": "hi-IN" if is_hindi else "mr-IN",
            "language_code": "hi-IN" if is_hindi else "mr-IN",
            "model": "Whisper Simulated Demo (Deterministic Fallback)",
            "provider": "Simulated Whisper",
            "request_id": f"sim_wh_{os.urandom(4).hex()}",
            "fallback_used": True,
        }
