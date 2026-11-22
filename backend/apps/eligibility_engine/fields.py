"""Field registry and value coercion for the eligibility engine.

Pure Python: no Django import. Deterministic; no LLM involved.
"""

import math
from decimal import Decimal, InvalidOperation


class _Invalid:
    """Singleton sentinel returned when a raw value cannot be read as its declared type."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'INVALID'


INVALID = _Invalid()


FIELD_REGISTRY = {
    'age_years': {
        'type': 'int',
        'label': 'Age in years',
    },
    'annual_household_income_inr': {
        'type': 'decimal',
        'label': 'Annual household income (INR)',
    },
    'state': {
        'type': 'str',
        'label': 'State of residence',
    },
    'district': {
        'type': 'str',
        'label': 'District',
    },
    'caste_category': {
        'type': 'enum',
        'choices': ['GENERAL', 'OPEN', 'OBC', 'SC', 'ST', 'VJNT', 'SBC', 'EWS', 'OTHER'],
        'label': 'Caste category',
    },
    'is_maharashtra_domicile': {
        'type': 'bool',
        'label': 'Maharashtra domicile',
    },
    'household_size': {
        'type': 'int',
        'label': 'Number of household members',
    },
    'member_relations': {
        'type': 'list_enum',
        'choices': ['SELF', 'SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER'],
        'label': 'Relations of household members',
    },
    'has_student_member': {
        'type': 'bool',
        'label': 'Any household member is a student',
    },
}


def _coerce_int(raw):
    if isinstance(raw, bool):
        return INVALID
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if text.isascii() and text.isdigit():
            return int(text)
    return INVALID


def _coerce_decimal(raw):
    if isinstance(raw, bool):
        return INVALID
    if isinstance(raw, Decimal):
        value = raw
    elif isinstance(raw, int):
        value = Decimal(raw)
    elif isinstance(raw, float):
        if not math.isfinite(raw):
            return INVALID
        value = Decimal(str(raw))
    elif isinstance(raw, str):
        try:
            value = Decimal(raw.strip())
        except InvalidOperation:
            return INVALID
    else:
        return INVALID
    if not value.is_finite():
        return INVALID
    return value


def _coerce_str(raw):
    if isinstance(raw, str):
        return raw.strip()
    return INVALID


def _coerce_bool(raw):
    if isinstance(raw, bool):
        return raw
    return INVALID


def _coerce_enum(raw, choices):
    if not isinstance(raw, str):
        return INVALID
    if choices is not None and raw not in choices:
        return INVALID
    return raw


def _coerce_list_enum(raw, choices):
    if not isinstance(raw, (list, tuple)):
        return INVALID
    items = []
    for item in raw:
        if not isinstance(item, str):
            return INVALID
        if choices is not None and item not in choices:
            return INVALID
        items.append(item)
    return items


def coerce(field_type, raw, choices=None):
    """Coerce a raw profile value to the declared field type.

    Returns None when raw is None, the coerced value when readable, or INVALID.
    """
    if raw is None:
        return None
    if field_type == 'int':
        return _coerce_int(raw)
    if field_type == 'decimal':
        return _coerce_decimal(raw)
    if field_type == 'str':
        return _coerce_str(raw)
    if field_type == 'bool':
        return _coerce_bool(raw)
    if field_type == 'enum':
        return _coerce_enum(raw, choices)
    if field_type == 'list_enum':
        return _coerce_list_enum(raw, choices)
    return INVALID


def coerce_value(field_name, raw):
    """Coerce a raw value using the type and choices registered for field_name."""
    spec = FIELD_REGISTRY[field_name]
    return coerce(spec['type'], raw, spec.get('choices'))


def build_facts(profile):
    """Collect raw profile values keyed by every FIELD_REGISTRY name (missing -> None).

    Coercion is left to the evaluator via coerce_value.
    """
    facts = {name: None for name in FIELD_REGISTRY}

    for name in (
        'age_years',
        'annual_household_income_inr',
        'state',
        'district',
        'caste_category',
        'is_maharashtra_domicile',
    ):
        facts[name] = getattr(profile, name, None)

    members = list(profile.members.all()) if hasattr(profile, 'members') else []
    if members:
        facts['household_size'] = len(members)
        facts['member_relations'] = [getattr(m, 'relation', None) for m in members]
        facts['has_student_member'] = any(bool(getattr(m, 'is_student', None)) for m in members)

    return facts
