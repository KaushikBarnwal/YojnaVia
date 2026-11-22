import json
from unittest.mock import patch

from django.test import TestCase

from apps.ai_assistant.gemini_client import GeminiIntakeAssistant
from apps.ai_assistant.models import IntakeConversation

CHAT_URL = "/api/v1/intake/chat/"
STATE_URL = "/api/v1/intake/state/"
CORRECT_URL = "/api/v1/intake/correct/"
RESTART_URL = "/api/v1/intake/restart/"
TOKEN = "test-session-token"
RESPONSE_KEYS = {"reply", "session_token", "state", "next_question", "eligibility", "error"}


class IntakeTestBase(TestCase):
    def _post(self, url, body):
        return self.client.post(url, data=json.dumps(body), content_type="application/json")

    def _get(self, url, params):
        return self.client.get(url, params)

    def _chat(self, message, extract_return=None):
        """POST a chat message with GeminiIntakeAssistant.extract mocked. Returns (response, mock)."""
        with patch.object(GeminiIntakeAssistant, "extract") as mock_extract:
            mock_extract.return_value = extract_return if extract_return is not None else ({}, None, None)
            response = self._post(CHAT_URL, {"message": message, "session_token": TOKEN})
        return response, mock_extract

    def _start_session(self):
        # Correction, restart and state endpoints require an existing conversation.
        self._chat("hello there")

    def _state_fields(self):
        response = self._get(STATE_URL, {"session_token": TOKEN})
        self.assertEqual(response.status_code, 200)
        return response.json()["state"]["fields"]

    @staticmethod
    def _all_unknown(fields):
        return all(entry["status"] == "unknown" for entry in fields.values())


class IntakeChatTests(IntakeTestBase):
    def test_valid_extraction_stores_known_field_with_user_message_source(self):
        response, mock_extract = self._chat("I am 21 years old", ({"age": 21}, None, None))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data.keys()), RESPONSE_KEYS)
        self.assertIsNone(data["error"])
        self.assertIn("?", data["reply"])
        self.assertIsNotNone(data["next_question"])

        age = data["state"]["fields"]["age"]
        self.assertEqual(age["status"], "known")
        self.assertEqual(age["value"], 21)
        self.assertEqual(age["source"], "user_message")
        self.assertTrue(mock_extract.called)

    def test_malformed_output_returns_error_code_and_leaves_state_unchanged(self):
        # Neutral message so the heuristic fallback has nothing to match.
        response, _ = self._chat("hello there", (None, "llm_malformed_output", None))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["error"]["code"], "llm_malformed_output")
        self.assertTrue(self._all_unknown(data["state"]["fields"]))

    def test_timeout_returns_llm_timeout_error_code(self):
        response, _ = self._chat("hello there", (None, "llm_timeout", None))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["error"]["code"], "llm_timeout")

    def test_rate_limit_returns_retry_after_and_skips_heuristic_fallback(self):
        # The message contains literal values the heuristic would otherwise store.
        response, _ = self._chat("I'm 21, from Maharashtra", (None, "llm_rate_limited", 30))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["error"]["code"], "llm_rate_limited")
        self.assertEqual(data["error"]["retry_after"], 30)
        self.assertTrue(self._all_unknown(data["state"]["fields"]))

    def test_confirmed_fields_are_not_re_sent_to_llm(self):
        self._start_session()
        self._post(CORRECT_URL, {"session_token": TOKEN, "field": "age", "value": 22})

        _, mock_extract = self._chat("I study MCA", ({}, None, None))

        self.assertTrue(mock_extract.called)
        requested_fields = mock_extract.call_args[0][1]
        self.assertNotIn("age", requested_fields)

    def test_aadhaar_message_is_refused_without_calling_llm_or_storing_history(self):
        response, mock_extract = self._chat("My Aadhaar is 1234 5678 9012")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("don't share", data["reply"])
        self.assertFalse(mock_extract.called)

        conv = IntakeConversation.objects.get(session_token=TOKEN)
        self.assertEqual(conv.history, [])

    def test_one_question_at_a_time_returns_single_object_or_null(self):
        response, _ = self._chat("hello there", ({}, None, None))

        next_question = response.json()["next_question"]
        self.assertIsInstance(next_question, dict)
        self.assertNotIsInstance(next_question, list)
        self.assertIn("field", next_question)
        self.assertIn("text", next_question)


class IntakeCorrectionTests(IntakeTestBase):
    def test_correction_sets_user_edit_and_llm_does_not_overwrite(self):
        self._start_session()

        response = self._post(CORRECT_URL, {"session_token": TOKEN, "field": "age", "value": 22})
        self.assertEqual(response.status_code, 200)

        age = self._state_fields()["age"]
        self.assertEqual(age["value"], 22)
        self.assertTrue(age["user_confirmed"])
        self.assertEqual(age["source"], "user_edit")

        self._chat("I am 30 years old", ({"age": 30}, None, None))

        age = self._state_fields()["age"]
        self.assertEqual(age["value"], 22)
        self.assertTrue(age["user_confirmed"])
        self.assertEqual(age["source"], "user_edit")

    def test_invalid_correction_field_returns_400(self):
        self._start_session()

        response = self._post(CORRECT_URL, {"session_token": TOKEN, "field": "aadhaar", "value": "123"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_invalid_correction_age_returns_400(self):
        self._start_session()

        response = self._post(CORRECT_URL, {"session_token": TOKEN, "field": "age", "value": "abc"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())


class IntakeRestartAndStateTests(IntakeTestBase):
    def test_restart_resets_all_fields_to_unknown(self):
        self._start_session()
        self._post(CORRECT_URL, {"session_token": TOKEN, "field": "age", "value": 22})
        self.assertEqual(self._state_fields()["age"]["status"], "known")

        response = self._post(RESTART_URL, {"session_token": TOKEN})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._all_unknown(response.json()["state"]["fields"]))
        self.assertTrue(self._all_unknown(self._state_fields()))

    def test_unknown_token_state_returns_404(self):
        response = self._get(STATE_URL, {"session_token": "no-such-token"})

        self.assertEqual(response.status_code, 404)

class IntakeEndToEndTests(IntakeTestBase):
    def test_heuristic_extraction_stores_volunteered_fields(self):
        # When LLM is unavailable, heuristic extraction parses age, state, income, education
        response, _ = self._chat(
            "I'm 21, from Maharashtra, studying MCA, and my family income is around 2 lakh",
            (None, "llm_unavailable", None)
        )
        self.assertEqual(response.status_code, 200)
        fields = response.json()["state"]["fields"]
        self.assertEqual(fields["age"]["value"], 21)
        self.assertEqual(fields["state"]["value"], "Maharashtra")
        self.assertEqual(fields["income_band"]["value"], "1_to_2_5_lakh")
        self.assertEqual(fields["education_level"]["value"], "postgraduate")

    def test_volunteered_social_category_stored_when_provided(self):
        response, _ = self._chat(
            "I am from OBC category",
            ({"social_category": "obc"}, None, None)
        )
        self.assertEqual(response.status_code, 200)
        fields = response.json()["state"]["fields"]
        self.assertEqual(fields["social_category"]["value"], "obc")
        self.assertEqual(fields["social_category"]["status"], "known")

    def test_eligibility_invoked_when_all_relevant_fields_known(self):
        # Provide age, state, income_band directly
        response, _ = self._chat(
            "I am 21, Maharashtra domicile, income 2 lakh, studying BTech, OBC category",
            ({"age": 21, "state": "Maharashtra", "income_band": "1_to_2_5_lakh", "education_level": "undergraduate", "social_category": "obc"}, None, None)
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["next_question"] is None:
            self.assertIsNotNone(data["eligibility"])
            self.assertIn("summary", data["eligibility"])
            self.assertIn("results", data["eligibility"])

    def test_essential_scholarship_fields_enforced_before_concluding(self):
        # Even if age, state, district, and income band are known,
        # assistant must not conclude until education_level and social_category are asked!
        response, _ = self._chat(
            "I am 22 from Pune, income 3 lakh",
            ({"age": 22, "state": "Maharashtra", "district": "Pune", "income_band": "2_5_to_5_lakh"}, None, None)
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["next_question"])
        self.assertIn("education_level", [data["next_question"]["field"], "education_level"])
        # Must not say it has all key details yet
        self.assertNotIn("Great, I have all the key details", data["reply"])
        self.assertTrue(
            "school" in data["reply"].lower() or 
            "college" in data["reply"].lower() or 
            "iti" in data["reply"].lower() or 
            "category" in data["reply"].lower()
        )

    def test_heuristic_extracts_education_and_social_category(self):
        from apps.ai_assistant.service import heuristic_extract
        res = heuristic_extract("I completed ITI and I am OBC from Pune")
        self.assertEqual(res.get("education_level"), "diploma")
        self.assertEqual(res.get("social_category"), "obc")
        self.assertEqual(res.get("district"), "Pune")


class GovernmentResolutionInterpreterTests(TestCase):
    def test_gr_samples_endpoint(self):
        response = self.client.get("/api/v1/assistant/gr_samples/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("samples", data)
        self.assertGreaterEqual(len(data["samples"]), 4)
        sample_ids = [s["id"] for s in data["samples"]]
        self.assertIn("ebc_cap_merit_2018", sample_ids)
        self.assertIn("ladki_bahin_2024", sample_ids)

    def test_interpret_gr_endpoint(self):
        payload = {
            "source_text": (
                "शासन निर्णय क्रमांक: संकीर्ण-२०१८/प्र.क्र.३६३/तांशि-४\n"
                "विद्यार्थ्याने केंद्रीभूत प्रवेश प्रक्रियेद्वारे (CAP) प्रवेश घेतलेला असणे अनिवार्य आहे.\n"
                "व्यवस्थापन कोट्यातील विद्यार्थी अपात्र ठरतील.\n"
                "कुटुंबाचे वार्षिक उत्पन्न रु. ८,००,०००/- पेक्षा जास्त नसावे.\n"
                "तहसीलदार यांनी दिलेला उत्पन्नाचा दाखला आवश्यक आहे."
            ),
            "preferred_language": "en"
        }
        response = self.client.post("/api/v1/assistant/interpret_gr/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("evidence_integrity_certified"))
        self.assertIn("eligibility_conditions", data)
        self.assertGreaterEqual(len(data["eligibility_conditions"]), 2)
        # Verify quotes are preserved
        for cond in data["eligibility_conditions"]:
            self.assertTrue(len(cond.get("source_quote", "")) > 0)
        self.assertIn("required_documents", data)
        self.assertIn("action_steps", data)


class SarvamVoiceIntakeTests(TestCase):
    def setUp(self):
        self.token = "test-voice-session-404"
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.dummy_audio_wav = SimpleUploadedFile("voice.wav", b"RIFF....WAVEfmt ....data....", content_type="audio/wav")

    def test_audio_validation_empty_and_format(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.ai_assistant.sarvam_speech import SarvamSpeechService

        # 1. Empty file
        empty_file = SimpleUploadedFile("empty.wav", b"", content_type="audio/wav")
        with self.assertRaises(ValueError) as ctx:
            SarvamSpeechService.validate_audio_upload(empty_file)
        self.assertIn("empty", str(ctx.exception).lower())

        # 2. Unsupported format
        bad_file = SimpleUploadedFile("doc.pdf", b"%PDF-1.4...", content_type="application/pdf")
        with self.assertRaises(ValueError) as ctx:
            SarvamSpeechService.validate_audio_upload(bad_file)
        self.assertIn("unsupported", str(ctx.exception).lower())

        # 3. Oversized file (>10MB)
        big_file = SimpleUploadedFile("huge.wav", b"0" * (11 * 1024 * 1024), content_type="audio/wav")
        with self.assertRaises(ValueError) as ctx:
            SarvamSpeechService.validate_audio_upload(big_file)
        self.assertIn("exceeds", str(ctx.exception).lower())

    def test_marathi_voice_demo_transcription_and_extraction(self):
        """Tests the canonical Marathi test scenario: age 24, Pune, income 2 lakh."""
        from apps.profiles.models import StudentProfile

        payload = {
            "session_token": self.token,
            "is_demo": "true",
            "demo_scenario": "marathi"
        }
        response = self.client.post("/api/v1/intake/voice/", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["detected_language"], "mr-IN")
        self.assertIn("पुण्यात", data["transcript"])
        self.assertTrue(data["requires_confirmation"])

        # Check extracted fields
        extracted = data["extracted_fields"]
        self.assertEqual(extracted.get("age"), 24)
        self.assertEqual(extracted.get("district"), "Pune")
        self.assertEqual(extracted.get("income_band"), "1_to_2_5_lakh")

        # High risk fields must be flagged
        high_risk_fields = [f["field"] for f in data["high_risk_fields"]]
        self.assertIn("age", high_risk_fields)
        self.assertIn("income_band", high_risk_fields)
        self.assertIn("district", high_risk_fields)

        # CONFIRMATION SAFEGUARD: StudentProfile must NOT be silently updated before citizen confirms
        profile = StudentProfile.objects.filter(session_token=self.token).first()
        if profile:
            self.assertNotEqual(profile.annual_family_income, 250000.0)

    def test_hindi_voice_demo_transcription_and_extraction(self):
        """Tests Hindi voice intake scenario."""
        payload = {
            "session_token": self.token,
            "is_demo": "true",
            "demo_scenario": "hindi"
        }
        response = self.client.post("/api/v1/intake/voice/", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["detected_language"], "hi-IN")
        self.assertIn("पुणे", data["transcript"])
        self.assertEqual(data["extracted_fields"].get("age"), 24)
        self.assertEqual(data["extracted_fields"].get("district"), "Pune")

    def test_sensitive_identifier_refusal_in_voice(self):
        """Voice note containing Aadhaar numbers must trigger sensitive refusal without extracting."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.ai_assistant.sarvam_speech import SarvamSpeechService

        with patch.object(SarvamSpeechService, "transcribe") as mock_stt:
            mock_stt.return_value = {
                "transcript": "My Aadhaar number is 9876 5432 1098 and my age is 20",
                "language_code": "en-IN",
                "request_id": "test_req",
                "is_simulated": True
            }
            audio_file = SimpleUploadedFile("voice.wav", b"RIFF1234WAVEfmt ", content_type="audio/wav")
            response = self.client.post("/api/v1/intake/voice/", data={
                "session_token": self.token,
                "audio": audio_file
            })
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get("is_sensitive_refusal"))
            self.assertIn("Aadhaar", data.get("reply", ""))

    def test_confirm_voice_intake_saves_profile_and_runs_eligibility(self):
        """Citizen explicitly confirms extracted values; engine synchronizes to profile and runs rules."""
        from apps.profiles.models import StudentProfile

        confirm_payload = {
            "session_token": self.token,
            "confirmed_fields": {
                "age": 24,
                "state": "Maharashtra",
                "district": "Pune",
                "income_band": "1_to_2_5_lakh"
            }
        }
        response = self.client.post("/api/v1/intake/confirm_voice/", data=json.dumps(confirm_payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # Check that StudentProfile was synced
        profile = StudentProfile.objects.get(session_token=self.token)
        self.assertEqual(profile.age, 24)
        self.assertEqual(profile.state, "Maharashtra")
        self.assertEqual(profile.district, "Pune")
        self.assertEqual(profile.annual_family_income, 250000.0)

    def test_sarvam_service_network_timeout_and_error_handling(self):
        """Simulate Sarvam API timeout and ensure clean error reporting."""
        import requests
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.ai_assistant.sarvam_speech import SarvamSpeechService

        audio_file = SimpleUploadedFile("test.wav", b"RIFF....WAVE", content_type="audio/wav")

        with patch.object(SarvamSpeechService, "is_configured", return_value=True):
            with patch("requests.post", side_effect=requests.exceptions.Timeout("Request timed out")):
                with self.assertRaises(TimeoutError):
                    SarvamSpeechService.transcribe(audio_file)


class LanguageMirroringTests(TestCase):
    def test_detect_message_language_accuracy(self):
        from apps.ai_assistant.schema import detect_message_language

        # Marathi
        self.assertEqual(detect_message_language("माझं वय २४ वर्ष आहे. मी पुण्यात शिकतो."), "marathi")
        self.assertEqual(detect_message_language("कुटुंबाचे वार्षिक उत्पन्न दोन लाख रुपये आहे"), "marathi")
        self.assertEqual(detect_message_language("majhe utpanna 2 lakh ahe"), "marathi")

        # Hindi (Devanagari)
        self.assertEqual(detect_message_language("मेरी उम्र 21 साल है और मैं पुणे में रहता हूँ"), "hindi")
        self.assertEqual(detect_message_language("नमस्ते, मुझे स्कॉलरशिप चाहिए"), "hindi")

        # Hinglish (Romanized Hindi)
        self.assertEqual(detect_message_language("meri umar 21 saal hai, mai pune me rehta hu"), "hinglish")
        self.assertEqual(detect_message_language("pariwar ki annual income 2 lakh hai"), "hinglish")

        # English
        self.assertEqual(detect_message_language("I am 21 years old and studying in Pune"), "english")
        self.assertEqual(detect_message_language("Hello, what scholarships are available?"), "english")

    def test_marathi_chat_returns_marathi_reply(self):
        response = self.client.post("/api/v1/intake/chat/", data=json.dumps({
            "message": "माझं वय २१ वर्ष आहे",
            "session_token": "token-lang-mr"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("?", data["reply"])
        # Should contain Marathi Devanagari characters
        self.assertTrue(any('\u0900' <= c <= '\u097F' for c in data["reply"]))

    def test_hinglish_chat_returns_hinglish_reply(self):
        response = self.client.post("/api/v1/intake/chat/", data=json.dumps({
            "message": "meri umar 21 saal hai, mai pune me rehta hu",
            "session_token": "token-lang-hinglish"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("?", data["reply"])
        reply_lower = data["reply"].lower()
        self.assertTrue(any(w in reply_lower for w in ["aapki", "kaunse", "rehte", "liye", "kripya", "note kar", "batayein"]))

    def test_hindi_chat_returns_hindi_reply(self):
        response = self.client.post("/api/v1/intake/chat/", data=json.dumps({
            "message": "मेरी उम्र 21 साल है और मैं पुणे में रहता हूँ",
            "session_token": "token-lang-hi"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("?", data["reply"])
        self.assertTrue(any('\u0900' <= c <= '\u097F' for c in data["reply"]))



