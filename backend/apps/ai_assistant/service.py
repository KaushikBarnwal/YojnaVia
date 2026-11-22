"""
Phase 3 intake service: conversation state, relevance, and the hand-off to the
deterministic eligibility engine.

Gemini (or the heuristic fallback) only proposes values. Values are stored in
IntakeConversation.fields and are only written to StudentProfile when a matching
profile already exists for the session. Eligibility is always computed by
eligibility.views.evaluate_profile_data().
"""

import re
from typing import Any, Optional

from apps.eligibility.views import evaluate_profile_data
from apps.profiles.models import StudentProfile
from apps.schemes.models import EligibilityRule

from .models import IntakeConversation
from .schema import ALL_FIELDS, SENSITIVE_FIELDS, parse_extraction, validate_field_value

QUESTIONS = {
    "age": {
        "text": "How old are you?",
        "suggestions": [],
    },
    "state": {
        "text": "Which state do you live in?",
        "suggestions": ["Maharashtra"],
    },
    "district": {
        "text": "Which district do you live in?",
        "suggestions": [],
    },
    "occupation": {
        "text": "What do you currently do? For example, are you a student, a farmer or employed?",
        "suggestions": ["Student", "Farmer", "Employed", "Self-employed", "Unemployed"],
    },
    "education_level": {
        "text": "What is your highest or current education level?",
        "suggestions": [
            "Below 10th",
            "10th pass",
            "12th pass",
            "Diploma",
            "Undergraduate",
            "Postgraduate",
            "Doctorate",
            "Other",
        ],
    },
    "income_band": {
        "text": "Roughly what is your family's total annual income?",
        "suggestions": [
            "Below ₹1 lakh",
            "₹1–2.5 lakh",
            "₹2.5–5 lakh",
            "₹5–8 lakh",
            "Above ₹8 lakh",
        ],
    },
}

# Design decision: each income band maps to its UPPER bound so that income-ceiling
# checks are never understated. A family in the "₹1–2.5 lakh" band is treated as
# earning ₹2.5 lakh, which can only make a student look less eligible for a
# ceiling-based scheme, never more. The "above_8_lakh" value is one rupee above
# the 8-lakh band top, so it fails an upper-limit check of 8 lakh.
INCOME_BAND_TO_ANNUAL_INR = {
    "below_1_lakh": 100000,
    "1_to_2_5_lakh": 250000,
    "2_5_to_5_lakh": 500000,
    "5_to_8_lakh": 800000,
    "above_8_lakh": 800001,
}

# Schema field -> StudentProfile attribute. Other fields live only in conversation state.
PROFILE_KEY_MAP = {
    "age": "age",
    "state": "state",
    "district": "district",
    "income_band": "annual_family_income",
}

# Rule field names that mean the same schema field.
RULE_FIELD_ALIASES = {
    "annual_family_income": "income_band",
    "annual_household_income_inr": "income_band",
    "age_years": "age",
    "is_maharashtra_domicile": "state",
}

FALLBACK_RELEVANT_FIELDS = ("age", "state", "income_band", "education_level")

INDIAN_STATES = (
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Puducherry", "Chandigarh",
)

_AGE_PATTERNS = (
    re.compile(r"\b(\d{1,3})\s*(?:years?|yrs?|y/o|year[- ]old)\b", re.IGNORECASE),
    re.compile(r"\bI\s*(?:am|'m)\s*(\d{1,3})\b", re.IGNORECASE),
)
_LAKH_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?)\b", re.IGNORECASE)
_THOUSAND_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*k\b", re.IGNORECASE)
_PLAIN_AMOUNT_RE = re.compile(
    r"(?:₹|\brs\.?|\binr\b|\bincome\b|\bsalary\b)\s*:?\s*(\d{4,7})\b"
    r"|\b(\d{4,7})\s*(?:per\s+(?:year|annum)|a\s+year|annually|yearly)\b",
    re.IGNORECASE,
)
_EDUCATION_RULES = (
    (re.compile(r"\bmca\b|\bm\.?\s?tech\b|\bmba\b|\bm\.?\s?sc\b|\bpost-?graduate\b|\bmaster'?s\b", re.IGNORECASE), "postgraduate"),
    (re.compile(r"\bb\.?\s?tech\b|\bb\.?\s?sc\b|\bb\.?\s?com\b|\bbachelor'?s?\b|\bundergraduate\b|\bgraduate\b", re.IGNORECASE), "undergraduate"),
    (re.compile(r"\bdiploma\b|\bpolytechnic\b", re.IGNORECASE), "diploma"),
    (re.compile(r"\b12th\b|\bhsc\b|\bjunior college\b", re.IGNORECASE), "12th_pass"),
    (re.compile(r"\b10th\b|\bssc\b", re.IGNORECASE), "10th_pass"),
)


# ----------------------------------------------------------------- conversation

def get_or_create_conversation(token: str) -> IntakeConversation:
    conv, _ = IntakeConversation.objects.get_or_create(session_token=token)
    return conv


def relevant_fields() -> tuple:
    """Schema fields the active schemes need, in ALL_FIELDS order. Never sensitive fields."""
    rule_fields = EligibilityRule.objects.filter(scheme__is_active=True).values_list("field", flat=True).distinct()
    wanted = set()
    for name in rule_fields:
        mapped = RULE_FIELD_ALIASES.get(name, name)
        # Only fields we can ask about are relevant; others would stall the flow.
        if mapped in ALL_FIELDS and mapped not in SENSITIVE_FIELDS and mapped in QUESTIONS:
            wanted.add(mapped)
    if not wanted:
        return FALLBACK_RELEVANT_FIELDS
    return tuple(f for f in ALL_FIELDS if f in wanted)


def snapshot(conv: IntakeConversation, relevant: tuple) -> dict:
    fields = {}
    for name in ALL_FIELDS:
        entry = (conv.fields or {}).get(name) or {}
        status = "known" if entry.get("status") == "known" else "unknown"
        fields[name] = {
            "value": entry.get("value") if status == "known" else None,
            "status": status,
            "confidence": entry.get("confidence"),
            "user_confirmed": entry.get("user_confirmed") is True,
            "source": entry.get("source"),
        }
    known_count = sum(1 for f in relevant if fields[f]["status"] == "known")
    return {"fields": fields, "known_count": known_count, "total_count": len(relevant)}


def _store(conv: IntakeConversation, field: str, value: Any, source: str, confidence: Optional[float], confirmed: bool) -> None:
    new_fields = dict(conv.fields or {})
    new_fields[field] = {
        "value": value,
        "status": "known",
        "confidence": confidence,
        "user_confirmed": confirmed,
        "source": source,
    }
    conv.fields = new_fields


def apply_extraction(conv: IntakeConversation, values: dict, source: str, confidence: float) -> None:
    """Store proposed values. Never overwrites a value the user has confirmed."""
    for field, value in values.items():
        if field not in ALL_FIELDS:
            continue
        existing = (conv.fields or {}).get(field) or {}
        if existing.get("user_confirmed") is True:
            continue
        _store(conv, field, value, source, confidence, confirmed=False)
    conv.save()


def correct_field(conv: IntakeConversation, field: str, raw_value: Any) -> None:
    """Apply an explicit user edit. Raises ValueError if the field or value is invalid."""
    if field not in ALL_FIELDS:
        raise ValueError(f"unknown field {field!r}")
    value = validate_field_value(field, raw_value)
    _store(conv, field, value, "user_edit", 1.0, confirmed=True)
    conv.save()


def confirm_field(conv: IntakeConversation, field: str, value: Any) -> None:
    """Record a value the user gave in reply to a pending question. Raises ValueError if invalid."""
    if field not in ALL_FIELDS:
        raise ValueError(f"unknown field {field!r}")
    checked = validate_field_value(field, value)
    _store(conv, field, checked, "user_confirmed", 1.0, confirmed=True)
    conv.save()


def sync_profile(token: str, conv: IntakeConversation, relevant: Optional[tuple] = None) -> None:
    """Copy known mapped fields to an existing StudentProfile or create one if absent."""
    profile, _ = StudentProfile.objects.get_or_create(session_token=token, defaults={"name": "Student"})
    for field, attr in PROFILE_KEY_MAP.items():
        entry = (conv.fields or {}).get(field) or {}
        if entry.get("status") != "known":
            continue
        value = entry.get("value")
        if field == "income_band":
            value = INCOME_BAND_TO_ANNUAL_INR.get(value, 250000)
        setattr(profile, attr, value)

    # Sync state and domicile
    state_entry = (conv.fields or {}).get("state") or {}
    if state_entry.get("status") == "known" and state_entry.get("value"):
        profile.state = state_entry.get("value")
        if str(state_entry.get("value")).strip().lower() == "maharashtra":
            profile.is_maharashtra_domicile = True

    # Sync caste if voluntarily provided (map GENERAL to OPEN)
    social_entry = (conv.fields or {}).get("social_category") or {}
    if social_entry.get("status") == "known":
        caste_val = str(social_entry.get("value", "")).upper()
        if caste_val in ("GENERAL", "OPEN"):
            caste_val = "OPEN"
        if caste_val in dict(StudentProfile.CASTE_CHOICES):
            profile.caste_category = caste_val

    # Sync course level from education level if known
    edu_entry = (conv.fields or {}).get("education_level") or {}
    if edu_entry.get("status") == "known":
        edu_val = edu_entry.get("value")
        if edu_val == "postgraduate":
            profile.current_course_level = "POSTGRADUATE"
        elif edu_val == "undergraduate":
            profile.current_course_level = "UNDERGRADUATE"
        elif edu_val == "diploma":
            profile.current_course_level = "DIPLOMA"
        elif edu_val in ("12th_pass", "10th_pass", "below_10th"):
            profile.current_course_level = "11TH_12TH"

    profile.save()


def next_question(conv: IntakeConversation, relevant: tuple) -> Optional[dict]:
    for field in relevant:
        if field not in QUESTIONS:
            continue
        entry = (conv.fields or {}).get(field) or {}
        if entry.get("status") != "known":
            return {
                "field": field,
                "text": QUESTIONS[field]["text"],
                "suggested_answers": QUESTIONS[field]["suggestions"],
            }
    return None


def _profile_dict(conv: IntakeConversation) -> dict:
    profile = {}
    for field, attr in PROFILE_KEY_MAP.items():
        entry = (conv.fields or {}).get(field) or {}
        if entry.get("status") != "known":
            continue
        value = entry.get("value")
        if field == "income_band":
            value = INCOME_BAND_TO_ANNUAL_INR[value]
        profile[attr] = value
    state_entry = (conv.fields or {}).get("state") or {}
    if state_entry.get("status") == "known" and state_entry.get("value"):
        profile["state"] = state_entry.get("value")
        if str(state_entry.get("value")).strip().lower() == "maharashtra":
            profile["is_maharashtra_domicile"] = True

    social_entry = (conv.fields or {}).get("social_category") or {}
    if social_entry.get("status") == "known":
        caste_val = str(social_entry.get("value", "")).upper()
        if caste_val in ("GENERAL", "OPEN"):
            caste_val = "OPEN"
        if caste_val in dict(StudentProfile.CASTE_CHOICES):
            profile["caste_category"] = caste_val

    edu_entry = (conv.fields or {}).get("education_level") or {}
    if edu_entry.get("status") == "known":
        edu_val = edu_entry.get("value")
        if edu_val == "postgraduate":
            profile["current_course_level"] = "POSTGRADUATE"
        elif edu_val == "undergraduate":
            profile["current_course_level"] = "UNDERGRADUATE"
        elif edu_val == "diploma":
            profile["current_course_level"] = "DIPLOMA"
        elif edu_val in ("12th_pass", "10th_pass", "below_10th"):
            profile["current_course_level"] = "11TH_12TH"

    return profile


def evaluate(conv: IntakeConversation, relevant: tuple) -> Optional[dict]:
    """Run the deterministic eligibility check once no relevant question is pending."""
    if next_question(conv, relevant) is not None:
        return None
    profile = _profile_dict(conv)
    if not profile:
        return None
    return evaluate_profile_data(profile)


def restart(conv: IntakeConversation) -> None:
    conv.fields = {}
    conv.history = []
    conv.save()


# ----------------------------------------------------------------- heuristics

def _band_for_lakh(lakh: float) -> str:
    if lakh < 1:
        return "below_1_lakh"
    if lakh <= 2.5:
        return "1_to_2_5_lakh"
    if lakh <= 5:
        return "2_5_to_5_lakh"
    if lakh <= 8:
        return "5_to_8_lakh"
    return "above_8_lakh"


def _income_band_from_text(text: str) -> Optional[str]:
    match = _LAKH_RE.search(text)
    if match:
        return _band_for_lakh(float(match.group(1)))
    match = _THOUSAND_RE.search(text)
    if match:
        return _band_for_lakh(float(match.group(1)) * 1000 / 100000)
    match = _PLAIN_AMOUNT_RE.search(text)
    if match:
        rupees = int(match.group(1) or match.group(2))
        return _band_for_lakh(rupees / 100000)
    return None


def heuristic_extract(message: str) -> dict:
    """Regex-only extraction of literally stated values. Returns schema-validated fields only."""
    text = message or ""
    raw: dict = {}

    for pattern in _AGE_PATTERNS:
        match = pattern.search(text)
        if match:
            raw["age"] = int(match.group(1))
            break

    best = None
    for name in INDIAN_STATES:
        match = re.search(r"\b" + re.escape(name) + r"\b", text, re.IGNORECASE)
        if match and (best is None or match.start() < best[0]):
            best = (match.start(), name)
    if best:
        raw["state"] = best[1]

    band = _income_band_from_text(text)
    if band:
        raw["income_band"] = band

    for pattern, level in _EDUCATION_RULES:
        if pattern.search(text):
            raw["education_level"] = level
            break

    return parse_extraction(raw)[0]
