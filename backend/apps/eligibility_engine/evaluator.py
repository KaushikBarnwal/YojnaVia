"""Deterministic tri-state eligibility evaluator.

Pure Python: no Django, no LLM, no network. Every decision is a fixed rule
applied to the stored criteria and the citizen's profile facts.
"""

import operator
from decimal import Decimal
from typing import Any

from .fields import FIELD_REGISTRY, INVALID, coerce_value
from .schema import InvalidRuleError, validate_criteria

PASS = 'PASS'
FAIL = 'FAIL'
UNKNOWN = 'UNKNOWN'

DISCLAIMER = 'Indicative only. Final eligibility is decided by the issuing authority.'
RULES_UNAVAILABLE = 'Eligibility rules for this scheme are not available right now.'
NO_CRITERIA = 'No eligibility criteria are recorded for this scheme yet.'
NO_MANDATORY = 'No mandatory criteria are recorded for this scheme.'
SAMPLE_WARNING = 'SAMPLE TEST DATA. This is not a verified government scheme record.'
UNVERIFIED_WARNING = (
    'This scheme record is not verified against its official source. '
    'Treat this result as indicative test output only.'
)

GROUP_KINDS = ('all', 'any', 'not')
NEGATED = {PASS: FAIL, FAIL: PASS, UNKNOWN: UNKNOWN}
NOT_EXPLANATION = 'This condition is reversed.'
GROUP_EXPLANATIONS = {
    'all': {
        PASS: 'All of the following must be met.',
        FAIL: 'Not all of the following are met.',
        UNKNOWN: 'Some of the following could not be confirmed.',
    },
    'any': {
        PASS: 'At least one of the following must be met.',
        FAIL: 'None of the following are met.',
        UNKNOWN: 'Some of the following could not be confirmed.',
    },
}
OP_PHRASES = {
    'eq': 'equal to',
    'neq': 'not equal to',
    'lt': 'less than',
    'lte': 'at most',
    'gt': 'greater than',
    'gte': 'at least',
    'in': 'one of',
    'not_in': 'not one of',
    'contains': 'includes',
}
COMPARATORS = {
    'eq': operator.eq,
    'neq': operator.ne,
    'lt': operator.lt,
    'lte': operator.le,
    'gt': operator.gt,
    'gte': operator.ge,
    'in': lambda actual, required: actual in required,
    'not_in': lambda actual, required: actual not in required,
}


# ---------------------------------------------------------------- public API

def evaluate_scheme(criteria, facts, scheme_meta):
    """Evaluate a scheme's stored criteria against profile facts."""
    meta = dict(scheme_meta or {})
    notices = _meta_warnings(meta)
    try:
        validate_criteria(criteria)
    except InvalidRuleError:
        return _build(meta, 'needs_confirmation', [RULES_UNAVAILABLE] + notices, [])
    if criteria == {}:
        return _build(meta, 'needs_confirmation', [NO_CRITERIA] + notices, [])

    results = []
    for index, clause in enumerate(_top_clauses(criteria)):
        result = evaluate_node(clause, facts, f'clauses[{index}]')
        result['mandatory'] = bool(clause.get('mandatory', True))
        results.append(result)
    outcome, extra = _outcome(results)
    return _build(meta, outcome, extra + notices, results)


def evaluate_node(node, facts, path='root'):
    """Return the tri-state result for one leaf or group node."""
    kind = _node_kind(node)
    if kind == 'leaf':
        return _evaluate_leaf(node, facts, path)

    children = [
        evaluate_node(child, facts, f'{path}.{index}')
        for index, child in enumerate(_children(node, kind))
    ]
    if kind == 'not':
        result = NEGATED[children[0]['result']]
        explanation = NOT_EXPLANATION
    else:
        result = _combine(kind, [child['result'] for child in children])
        explanation = GROUP_EXPLANATIONS[kind][result]
    group = _base(node, path, kind, result, explanation)
    group['children'] = children
    return group


# ------------------------------------------------------------- node handling

def _node_kind(node):
    if 'field' in node:
        return 'leaf'
    for kind in GROUP_KINDS:
        if kind in node:
            return kind
    raise ValueError(f'Unrecognised eligibility node keys: {sorted(node)}')


def _children(node, kind):
    raw = node.get(kind)
    return raw if isinstance(raw, list) else [raw]


def _top_clauses(criteria):
    if 'clauses' in criteria:
        return criteria['clauses']
    return [criteria]


def _combine(kind, results):
    if kind == 'all':
        if FAIL in results:
            return FAIL
        if UNKNOWN in results:
            return UNKNOWN
        return PASS
    if PASS in results:
        return PASS
    if UNKNOWN in results:
        return UNKNOWN
    return FAIL


def _base(node, path, kind, result, explanation):
    return {
        'criterion_id': node.get('id') or path,
        'type': kind,
        'description': node.get('description', ''),
        'result': result,
        'explanation': explanation,
        'source_ref': node.get('source_ref'),
    }


# ------------------------------------------------------------------- leaves

def _evaluate_leaf(node, facts, path):
    field = node.get('field')
    op = node.get('op')
    required = node.get('value')
    field_meta = FIELD_REGISTRY.get(field, {})
    label = field_meta.get('label', field)

    coerced = coerce_value(field, facts.get(field))
    invalid = coerced is INVALID
    actual = None if (invalid or coerced is None) else coerced

    result = UNKNOWN
    if actual is not None:
        outcome = _apply(op, actual, required, field_meta.get('type'))
        if outcome is not None:
            result = PASS if outcome else FAIL

    remedy = node.get('remedy') if result == FAIL else None
    leaf = _base(
        node, path, 'leaf', result,
        _leaf_explanation(label, op, actual, required, result, invalid),
    )
    leaf.update(
        field=field,
        field_label=label,
        operator=op,
        required_value=_json_safe(required),
        actual_value=_json_safe(actual),
        remedy=remedy,
    )
    return leaf


def _apply(op, actual, required, field_type):
    """Return True/False, or None when the comparison cannot be made."""
    try:
        return _compare(op, actual, required, field_type)
    except (TypeError, ValueError, ArithmeticError):
        return None


def _compare(op, actual, required, field_type):
    if op == 'contains':
        if not isinstance(actual, list):
            return None
        return required in actual
    comparator = COMPARATORS.get(op)
    if comparator is None:
        return None
    return comparator(
        _normalise(actual, field_type),
        _normalise(required, field_type),
    )


def _normalise(value, field_type):
    if isinstance(value, list):
        return [_normalise(item, field_type) for item in value]
    if field_type == 'decimal':
        return Decimal(str(value))
    if field_type == 'str' and isinstance(value, str):
        return value.casefold()
    return value


def _leaf_explanation(label, op, actual, required, result, invalid):
    if result == UNKNOWN:
        if invalid:
            return (f'{label} could not be read from the profile, '
                    'so this condition cannot be confirmed yet.')
        if actual is None:
            return f'{label} was not provided, so this condition cannot be confirmed yet.'
        return f'{label} could not be compared, so this condition cannot be confirmed yet.'
    actual_text = str(actual)
    if isinstance(required, list):
        required_text = ', '.join(str(item) for item in required)
    else:
        required_text = str(required)
    lead = 'This meets the condition' if result == PASS else 'This does not meet the condition'
    return f'{label} is {actual_text}. {lead}: {OP_PHRASES.get(op, op)} {required_text}.'


def _json_safe(value: Any):
    if value is INVALID:
        return None
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


# ------------------------------------------------------ scheme-level results

def _outcome(results):
    mandatory = [result for result in results if result['mandatory']]
    if not mandatory:
        return 'needs_confirmation', [NO_MANDATORY]
    statuses = [result['result'] for result in mandatory]
    if FAIL in statuses:
        return 'not_eligible', []
    if UNKNOWN in statuses:
        return 'needs_confirmation', []
    return 'likely_eligible', []


def _meta_warnings(meta):
    warnings = []
    if meta.get('is_sample'):
        warnings.append(SAMPLE_WARNING)
    if meta.get('verification_status') != 'VERIFIED':
        warnings.append(UNVERIFIED_WARNING)
    return warnings


def _build(meta, outcome, warnings, results):
    leaves = [leaf for top in results for leaf in _walk_leaves(top)]
    return {
        'scheme_code': meta.get('code'),
        'scheme_name': meta.get('name'),
        'outcome': outcome,
        'disclaimer': DISCLAIMER,
        'is_sample': bool(meta.get('is_sample')),
        'verification_status': meta.get('verification_status'),
        'source': {
            'official_source_url': meta.get('official_source_url'),
            'last_verified_on': meta.get('last_verified_on'),
        },
        'warnings': warnings,
        'criteria': results,
        'missing_fields': _missing_fields(leaves),
        'failed_mandatory': _failed_mandatory(results),
        'recommendations': _recommendations(leaves),
    }


def _walk_leaves(result):
    if result['type'] == 'leaf':
        yield result
        return
    for child in result.get('children', []):
        yield from _walk_leaves(child)


def _missing_fields(leaves):
    by_field = {}
    for leaf in leaves:
        if leaf['result'] != UNKNOWN:
            continue
        entry = by_field.setdefault(leaf['field'], {
            'field': leaf['field'],
            'label': leaf['field_label'],
            'criterion_ids': [],
        })
        entry['criterion_ids'].append(leaf['criterion_id'])
    return list(by_field.values())


def _failed_mandatory(results):
    failed = []
    for top in results:
        if top['mandatory']:
            failed.extend(
                leaf['criterion_id'] for leaf in _walk_leaves(top) if leaf['result'] == FAIL
            )
    return failed


def _recommendations(leaves):
    items = []
    for leaf in leaves:
        remedy = leaf.get('remedy')
        if leaf['result'] == FAIL and remedy and remedy.get('text'):
            items.append({
                'criterion_id': leaf['criterion_id'],
                'text': remedy['text'],
                'source_ref': remedy.get('source_ref'),
            })
    return items
