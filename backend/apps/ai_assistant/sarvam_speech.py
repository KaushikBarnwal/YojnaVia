"""
Sarvam AI Speech-to-Text Integration Service.
Model: saaras:v4
Supported Languages: Marathi (mr-IN), Hindi (hi-IN), Code-mixed, and Auto-detection (unknown).

Architecture & Privacy Guarantees:
- Audio uploads are processed entirely in memory/temporary streams; NEVER permanently persisted.
- API keys reside solely on the Django backend (never exposed to Vue client).
- Enforces strict file-size limits (max 10 MB) and audio format validation.
- Provides seamless demo/simulated fallback for testing without external API credentials.
- Transcripts feed into existing Gemini extraction & deterministic eligibility engines.
"""

import logging
import os
import re
import time
import uuid
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Constants
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/webm",
    "audio/ogg",
    "audio/opus",
    "audio/mpeg",
    "audio/mp3",
    "audio/m4a",
    "audio/x-m4a",
    "audio/mp4",
    "audio/aac",
    "application/octet-stream",  # Fallback for some browser MediaRecorder uploads
}
ALLOWED_EXTENSIONS = {".wav", ".webm", ".ogg", ".mp3", ".m4a", ".aac", ".opus", ".mp4"}
SUPPORTED_LANGUAGES = {"mr-IN", "hi-IN", "en-IN", "unknown"}

# Canonical Demo Audio Phrases
CANONICAL_MARATHI_DEMO = "माझं वय २४ वर्ष आहे. मी पुण्यात राहतो. माझ्या कुटुंबाचं वार्षिक उत्पन्न दोन लाख रुपये आहे."
CANONICAL_HINDI_DEMO = "मेरी उम्र 24 वर्ष है। मैं पुणे में रहता हूँ। मेरी वार्षिक पारिवारिक आय दो लाख रुपये है।"


class SarvamSpeechService:
    @classmethod
    def get_api_key(cls) -> str:
        return os.getenv("SARVAM_API_KEY", "").strip()

    @classmethod
    def is_configured(cls) -> bool:
        key = cls.get_api_key()
        return bool(key and not key.startswith("your_"))

    @classmethod
    def validate_audio_upload(cls, uploaded_file) -> None:
        """
        Validates presence, size, and MIME/extension format of uploaded citizen audio.
        Raises ValueError with descriptive message on validation failure.
        """
        if not uploaded_file:
            raise ValueError("No audio file provided. Please record or upload an audio message.")

        file_size = getattr(uploaded_file, "size", 0)
        if file_size == 0:
            raise ValueError("The uploaded audio recording is empty (0 bytes).")

        if file_size > MAX_AUDIO_SIZE_BYTES:
            raise ValueError(f"Audio file exceeds the 10 MB size limit ({file_size / (1024 * 1024):.1f} MB uploaded).")

        filename = getattr(uploaded_file, "name", "").lower()
        content_type = getattr(uploaded_file, "content_type", "").lower()

        ext_match = any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)
        type_match = content_type in ALLOWED_CONTENT_TYPES or any(content_type.startswith(t) for t in ("audio/", "video/webm"))

        if not (ext_match or type_match):
            raise ValueError(
                f"Unsupported audio format '{content_type}'. Please use WebM, WAV, MP3, OGG, or M4A."
            )

    @classmethod
    def transcribe(
        cls,
        uploaded_file,
        language_code: str = "unknown",
        model: str = "saaras:v4"
    ) -> Dict[str, Any]:
        """
        Transcribes audio using Sarvam AI Saaras v4 or graceful simulated demo fallback.
        Audio is processed in memory and never written to permanent disk storage.
        """
        cls.validate_audio_upload(uploaded_file)

        lang = language_code if language_code in SUPPORTED_LANGUAGES else "unknown"
        api_key = cls.get_api_key()

        if cls.is_configured():
            return cls._transcribe_live(uploaded_file, lang, model, api_key)
        else:
            return cls._transcribe_simulated(uploaded_file, lang, model)

    @classmethod
    def _transcribe_live(
        cls,
        uploaded_file,
        language_code: str,
        model: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Dispatches audio payload to Sarvam AI STT API."""
        import requests

        endpoint = os.getenv("SARVAM_STT_ENDPOINT", "https://api.sarvam.ai/speech-to-text")
        headers = {
            "api-subscription-key": api_key,
        }

        # Read file into memory buffer
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        filename = getattr(uploaded_file, "name", "citizen_voice.webm")
        content_type = getattr(uploaded_file, "content_type", "audio/webm")

        files = {
            "file": (filename, file_bytes, content_type)
        }
        data = {
            "model": model,
            "language_code": language_code,
            "with_diarization": "false",
        }

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                files=files,
                data=data,
                timeout=18  # 18s network timeout
            )

            if response.status_code == 200:
                resp_json = response.json()
                transcript = resp_json.get("transcript", "").strip()
                detected_lang = resp_json.get("language_code", language_code)
                req_id = resp_json.get("request_id", f"sarvam_{int(time.time())}")

                return {
                    "transcript": transcript,
                    "language_code": detected_lang,
                    "request_id": req_id,
                    "model": model,
                    "is_simulated": False,
                    "pilot_mode": False
                }
            elif response.status_code == 429:
                logger.warning("Sarvam AI STT rate limited (HTTP 429)")
                raise RuntimeError("Sarvam AI speech recognition service is temporarily busy. Please try speaking again shortly.")
            else:
                error_detail = response.text[:200]
                logger.error("Sarvam AI STT error (HTTP %d): %s", response.status_code, error_detail)
                raise RuntimeError(f"Sarvam speech recognition failed (HTTP {response.status_code}).")

        except requests.exceptions.Timeout:
            logger.error("Sarvam AI STT request timed out")
            raise TimeoutError("Speech recognition request timed out. Please try speaking again.")
        except requests.exceptions.RequestException as e:
            logger.error("Sarvam AI STT network exception: %s", str(e))
            raise RuntimeError("Unable to reach Sarvam speech recognition service. Please check your connection.")

    @classmethod
    def _transcribe_simulated(
        cls,
        uploaded_file,
        language_code: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Simulated prototype fallback for offline development, automated testing, and demos.
        Returns authentic Marathi / Hindi transcript corresponding to standard test scenarios.
        """
        filename = getattr(uploaded_file, "name", "").lower()

        # If audio is marked as Hindi or requested in Hindi
        if language_code == "hi-IN" or "hindi" in filename or "hi" in filename:
            transcript = CANONICAL_HINDI_DEMO
            detected_lang = "hi-IN"
        else:
            # Default to canonical Marathi citizen scenario
            transcript = CANONICAL_MARATHI_DEMO
            detected_lang = "mr-IN"

        req_id = f"sim_sarvam_{int(time.time())}_{uuid.uuid4().hex[:6]}"

        return {
            "transcript": transcript,
            "language_code": detected_lang,
            "request_id": req_id,
            "model": model,
            "is_simulated": True,
            "pilot_mode": True,
            "pilot_notice": "Pilot Mode: Simulated Sarvam Saaras v4 transcription. Configure SARVAM_API_KEY in backend/.env for production API."
        }
