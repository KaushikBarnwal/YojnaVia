"""
Profile field schema for Phase 3 conversational intake.

Defines the structured fields Gemini may extract from a natural-language
message, the enums they must use, and the validation applied to every
candidate value. Extraction output is only a proposal: parse_extraction()
keeps a value only when validate_field_value() accepts it. This module has
no Django imports so it can be used and tested on its own.
"""

import re
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class IncomeBand(str, Enum):
    """Annual household income bands (INR)."""

    BELOW_1_LAKH = "below_1_lakh"
    ONE_TO_2_5_LAKH = "1_to_2_5_lakh"
    TWO_5_TO_5_LAKH = "2_5_to_5_lakh"
    FIVE_TO_8_LAKH = "5_to_8_lakh"
    ABOVE_8_LAKH = "above_8_lakh"


class EducationLevel(str, Enum):
    """Highest or current education level of the student."""

    BELOW_10TH = "below_10th"
    TENTH_PASS = "10th_pass"
    TWELFTH_PASS = "12th_pass"
    DIPLOMA = "diploma"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"
    OTHER = "other"


class SocialCategory(str, Enum):
    """Social category. Only stored when the user volunteers it."""

    GENERAL = "general"
    OBC = "obc"
    SC = "sc"
    ST = "st"
    EWS = "ews"
    VJNT = "vjnt"
    SBC = "sbc"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Relationship(str, Enum):
    """Relationship of a family member to the student."""

    FATHER = "father"
    MOTHER = "mother"
    SIBLING = "sibling"
    SPOUSE = "spouse"
    CHILD = "child"
    GRANDPARENT = "grandparent"
    GUARDIAN = "guardian"
    OTHER = "other"


class FamilyMember(BaseModel):
    """One household member mentioned by the user."""

    model_config = ConfigDict(extra="forbid")

    relationship: Relationship
    age: Optional[int] = Field(default=None, ge=0, le=120)
    occupation: Optional[str] = Field(default=None, max_length=100)


ALL_FIELDS = (
    "age",
    "state",
    "district",
    "occupation",
    "education_level",
    "income_band",
    "social_category",
    "disability_status",
    "family_members",
)

# Only ever stored when the user volunteers them.
SENSITIVE_FIELDS = ("social_category", "disability_status")

ALLOWED_SOURCES = ("user_message", "user_confirmed", "user_edit", "heuristic")

MAX_FAMILY_MEMBERS = 10

_SENSITIVE_NUMBER_RE = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
_SENSITIVE_WORD_RE = re.compile(
    r"\b(otp|one[- ]time password|password|passcode|pin|bank account|account number|ifsc|aadhaar|aadhar)\b",
    re.IGNORECASE,
)


def _clean_text(raw: Any, field_name: str, max_length: int, allow_empty: bool) -> str:
    """Return a stripped string, or raise ValueError."""
    if not isinstance(raw, str):
        raise ValueError(f"{field_name} must be a string")
    text = raw.strip()
    if not allow_empty and not text:
        raise ValueError(f"{field_name} must not be empty")
    if len(text) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters")
    return text


DISTRICT_INDIC_TO_ENGLISH = {
    "पुणे": "Pune", "पुण्यात": "Pune",
    "सांगली": "Sangli", "सांगलीत": "Sangli",
    "नाशिक": "Nashik", "नाशिकमध्ये": "Nashik",
    "सोलापूर": "Solapur", "सोलापुरात": "Solapur",
    "कोल्हापूर": "Kolhapur", "कोल्हापुरात": "Kolhapur",
    "मुंबई": "Mumbai", "मुंबईत": "Mumbai",
    "नागपूर": "Nagpur", "नागपुरात": "Nagpur",
    "ठाणे": "Thane", "ठाण्यात": "Thane",
    "छत्रपती संभाजीनगर": "Chhatrapati Sambhajinagar",
    "संभाजीनगर": "Chhatrapati Sambhajinagar",
    "औरंगाबाद": "Chhatrapati Sambhajinagar",
    "अमरावती": "Amravati",
    "नांदेड": "Nanded",
    "जळगाव": "Jalgaon",
    "सातारा": "Satara",
    "रत्नागिरी": "Ratnagiri",
    "सिंधुदुर्ग": "Sindhudurg",
    "अहमदनगर": "Ahmednagar",
    "अहिल्यानगर": "Ahilyanagar",
    "लातूर": "Latur",
    "बीड": "Beed",
    "उस्मानाबाद": "Dharashiv",
    "धाराशिव": "Dharashiv",
    "धुळे": "Dhule",
    "नंदुरबार": "Nandurbar",
    "चंद्रपूर": "Chandrapur",
    "गोंदिया": "Gondia",
    "भंडारा": "Bhandara",
    "गडचिरोली": "Gadchiroli",
    "वर्धा": "Wardha",
    "यवतमाळ": "Yavatmal",
    "वाशिम": "Washim",
    "अकोला": "Akola",
    "हिंगोली": "Hingoli",
    "परभणी": "Parbhani",
    "जालना": "Jalna",
    "रायगड": "Raigad",
    "पालघर": "Palghar",
}

STATE_INDIC_TO_ENGLISH = {
    "महाराष्ट्र": "Maharashtra",
    "महाराष्ट्रात": "Maharashtra",
}


def validate_field_value(field: str, raw: Any) -> Any:
    """Return the normalised value for `field`, or raise ValueError."""
    if field == "age":
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise ValueError("age must be an integer")
        if not 0 <= raw <= 120:
            raise ValueError("age must be between 0 and 120")
        return raw

    if field == "state":
        cleaned = _clean_text(raw, field, 100, allow_empty=False)
        return STATE_INDIC_TO_ENGLISH.get(cleaned, cleaned)

    if field == "district":
        cleaned = _clean_text(raw, field, 100, allow_empty=False)
        return DISTRICT_INDIC_TO_ENGLISH.get(cleaned, cleaned)

    if field == "occupation":
        return _clean_text(raw, field, 100, allow_empty=True)

    if field == "education_level":
        return EducationLevel(raw).value

    if field == "income_band":
        return IncomeBand(raw).value

    if field == "social_category":
        return SocialCategory(raw).value

    if field == "disability_status":
        if not isinstance(raw, bool):
            raise ValueError("disability_status must be a boolean")
        return raw

    if field == "family_members":
        if not isinstance(raw, list) or len(raw) > MAX_FAMILY_MEMBERS:
            raise ValueError(f"family_members must be a list of at most {MAX_FAMILY_MEMBERS} entries")
        members = []
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError("each family member must be an object")
            members.append(FamilyMember.model_validate(item).model_dump(mode="json"))
        return members

    raise ValueError(f"unknown field {field!r}")


class ExtractedProfile(BaseModel):
    """Structured profile fields extracted from one user message. All optional."""

    model_config = ConfigDict(extra="forbid")

    age: Optional[int] = Field(default=None, ge=0, le=120)
    state: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    occupation: Optional[str] = Field(default=None, max_length=100)
    education_level: Optional[EducationLevel] = None
    income_band: Optional[IncomeBand] = None
    social_category: Optional[SocialCategory] = None
    disability_status: Optional[bool] = None
    family_members: Optional[list[FamilyMember]] = Field(default=None, max_length=MAX_FAMILY_MEMBERS)


def parse_extraction(payload: Any) -> tuple[dict, list[str]]:
    """Split a raw extraction payload into (accepted values, rejected keys).

    Never raises. Non-dict payloads yield ({}, []).
    """
    accepted: dict = {}
    rejected: list[str] = []
    if not isinstance(payload, dict):
        return {}, []
    for key, raw in payload.items():
        if key not in ALL_FIELDS:
            rejected.append(str(key))
            continue
        try:
            accepted[key] = validate_field_value(key, raw)
        except (ValueError, TypeError, ValidationError):
            rejected.append(key)
    return accepted, rejected


def looks_like_sensitive_identifier(text: str) -> bool:
    """True if text appears to contain a card-like number or an OTP/password/bank identifier."""
    if _SENSITIVE_NUMBER_RE.search(text):
        return True
    return bool(_SENSITIVE_WORD_RE.search(text))
