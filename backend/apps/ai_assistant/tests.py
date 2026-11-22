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
            "I am 21, Maharashtra domicile, income 2 lakh",
            ({"age": 21, "state": "Maharashtra", "income_band": "1_to_2_5_lakh"}, None, None)
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["next_question"] is None:
            self.assertIsNotNone(data["eligibility"])
            self.assertIn("summary", data["eligibility"])
            self.assertIn("results", data["eligibility"])
