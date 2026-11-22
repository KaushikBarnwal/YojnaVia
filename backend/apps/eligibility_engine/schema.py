"""Structural validation for eligibility criteria JSON.

Pure Python: no Django import. Deterministic; no LLM involved.
"""

import math
import re
from decimal import Decimal, InvalidOperation

from .fields import FIELD_REGISTRY


class InvalidRuleError(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message
        super().__init__(f'{path}: {message}')


OPS = {'eq', 'neq', 'lt', 'lte', 'gt', 'gte', 'in', 'not_in', 'contains'}

MAX_DEPTH = 6
MAX_LEAVES = 100

_ID_RE = re.compile(r'[a-z0-9_]{1,40}')
_COMMON_KEYS = {'id', 'description', 'source_ref'}
_GROUP_KEYS = ('all', 'any', 'not')
_LEAF_KEYS = {'field', 'op', 'value', 'remedy'}
_CMP_OPS = {'eq', 'neq', 'lt', 'lte', 'gt', 'gte'}
_EQ_OPS = {'eq', 'neq'}
_SET_OPS = {'in', 'not_in'}


class _State:
    def __init__(self):
        self.seen_ids = set()
        self.leaf_count = 0


def validate_criteria(criteria):
    """Validate a criteria tree. Returns None on success, raises InvalidRuleError otherwise."""
    if criteria is None or criteria == {}:
        return None
    if not isinstance(criteria, dict):
        raise InvalidRuleError('criteria', 'must be an object with a "clauses" key')

    unknown = sorted(str(k) for k in criteria if k != 'clauses')
    if unknown:
        raise InvalidRuleError('criteria', f'unknown top-level key(s): {", ".join(unknown)}')
    if 'clauses' not in criteria:
        raise InvalidRuleError('criteria', 'missing required key "clauses"')

    clauses = criteria['clauses']
    if not isinstance(clauses, list) or not clauses:
        raise InvalidRuleError('criteria', '"clauses" must be a non-empty list')

    state = _State()
    for i, clause in enumerate(clauses):
        _validate_node(clause, f'clauses[{i}]', 1, True, state)
    return None


def _validate_node(node, path, depth, is_top, state):
    if depth > MAX_DEPTH:
        raise InvalidRuleError(path, f'nesting depth exceeds {MAX_DEPTH}')
    if not isinstance(node, dict):
        raise InvalidRuleError(path, 'rule must be an object')

    group_keys = [k for k in _GROUP_KEYS if k in node]
    looks_like_leaf = any(k in node for k in ('field', 'op', 'value'))

    if len(group_keys) > 1:
        raise InvalidRuleError(path, 'use exactly one of all, any or not')
    if group_keys:
        kind_keys = {group_keys[0]}
    elif looks_like_leaf:
        kind_keys = _LEAF_KEYS
    else:
        raise InvalidRuleError(path, 'rule must be a group (all/any/not) or a leaf (field/op/value)')

    allowed = _COMMON_KEYS | kind_keys | ({'mandatory'} if is_top else set())
    for key in node:
        if key not in allowed:
            raise InvalidRuleError(f'{path}.{key}', 'unexpected key for this rule kind')

    _check_id(node, path, state)
    _check_description(node, path)
    if 'source_ref' in node:
        _check_text(node['source_ref'], 1, 200, f'{path}.source_ref')
    if is_top and 'mandatory' in node:
        if not isinstance(node['mandatory'], bool):
            raise InvalidRuleError(f'{path}.mandatory', 'must be true or false')

    if group_keys:
        _validate_group(node, group_keys[0], path, depth, state)
    else:
        _validate_leaf(node, path, state)


def _check_id(node, path, state):
    if 'id' not in node:
        raise InvalidRuleError(f'{path}.id', 'id is required')
    rule_id = node['id']
    if not isinstance(rule_id, str) or not _ID_RE.fullmatch(rule_id):
        raise InvalidRuleError(f'{path}.id', 'id must match ^[a-z0-9_]{1,40}$')
    if rule_id in state.seen_ids:
        raise InvalidRuleError(f'{path}.id', f'duplicate id {rule_id!r}')
    state.seen_ids.add(rule_id)


def _check_description(node, path):
    if 'description' not in node:
        raise InvalidRuleError(f'{path}.description', 'description is required')
    desc = node['description']
    _check_text(desc, 1, 300, f'{path}.description')
    if not desc.strip():
        raise InvalidRuleError(f'{path}.description', 'description must not be blank')


def _check_text(value, min_len, max_len, path):
    if not isinstance(value, str) or not (min_len <= len(value) <= max_len):
        raise InvalidRuleError(path, f'must be a string of {min_len} to {max_len} characters')


def _validate_group(node, key, path, depth, state):
    if key == 'not':
        child = node['not']
        if not isinstance(child, dict):
            raise InvalidRuleError(f'{path}.not', 'must be a single rule object')
        _validate_node(child, f'{path}.not', depth + 1, False, state)
        return

    children = node[key]
    if not isinstance(children, list) or not children:
        raise InvalidRuleError(f'{path}.{key}', 'must be a non-empty list of rules')
    for i, child in enumerate(children):
        _validate_node(child, f'{path}.{key}[{i}]', depth + 1, False, state)


def _validate_leaf(node, path, state):
    state.leaf_count += 1
    if state.leaf_count > MAX_LEAVES:
        raise InvalidRuleError(path, f'more than {MAX_LEAVES} leaf criteria')

    for key in ('field', 'op', 'value'):
        if key not in node:
            raise InvalidRuleError(f'{path}.{key}', f'{key} is required')

    field = node['field']
    if not isinstance(field, str) or field not in FIELD_REGISTRY:
        raise InvalidRuleError(f'{path}.field', 'unknown field')

    op = node['op']
    if not isinstance(op, str) or op not in OPS:
        raise InvalidRuleError(f'{path}.op', 'unknown operator')

    if 'remedy' in node:
        _validate_remedy(node['remedy'], f'{path}.remedy')

    spec = FIELD_REGISTRY[field]
    _check_leaf_value(spec['type'], op, node['value'], path, spec.get('choices'))


def _validate_remedy(remedy, path):
    if not isinstance(remedy, dict):
        raise InvalidRuleError(path, 'remedy must be an object')
    for key in remedy:
        if key not in ('text', 'source_ref'):
            raise InvalidRuleError(f'{path}.{key}', 'unexpected key in remedy')
    for key in ('text', 'source_ref'):
        if key not in remedy:
            raise InvalidRuleError(f'{path}.{key}', f'{key} is required in remedy')
    _check_text(remedy['text'], 1, 300, f'{path}.text')
    _check_text(remedy['source_ref'], 1, 200, f'{path}.source_ref')


def _check_leaf_value(ftype, op, value, path, choices):
    op_path = f'{path}.op'
    value_path = f'{path}.value'

    if ftype in ('int', 'decimal'):
        if op in _CMP_OPS:
            if not _is_number(value):
                raise InvalidRuleError(value_path, 'value must be a number')
        elif op in _SET_OPS:
            _check_list(value, value_path)
            for i, item in enumerate(value):
                if not _is_number(item):
                    raise InvalidRuleError(f'{value_path}[{i}]', 'must be a number')
        else:
            _bad_op(op_path, op, ftype)

    elif ftype == 'str':
        if op in _EQ_OPS:
            if not isinstance(value, str):
                raise InvalidRuleError(value_path, 'value must be a string')
        elif op in _SET_OPS:
            _check_list(value, value_path)
            for i, item in enumerate(value):
                if not isinstance(item, str):
                    raise InvalidRuleError(f'{value_path}[{i}]', 'must be a string')
        else:
            _bad_op(op_path, op, ftype)

    elif ftype == 'bool':
        if op not in _EQ_OPS:
            _bad_op(op_path, op, ftype)
        if not isinstance(value, bool):
            raise InvalidRuleError(value_path, 'value must be true or false')

    elif ftype == 'enum':
        if op in _EQ_OPS:
            if not _in_choices(value, choices):
                raise InvalidRuleError(value_path, 'value must be one of the allowed choices')
        elif op in _SET_OPS:
            _check_list(value, value_path)
            for i, item in enumerate(value):
                if not _in_choices(item, choices):
                    raise InvalidRuleError(f'{value_path}[{i}]', 'must be one of the allowed choices')
        else:
            _bad_op(op_path, op, ftype)

    elif ftype == 'list_enum':
        if op != 'contains':
            _bad_op(op_path, op, ftype)
        if not _in_choices(value, choices):
            raise InvalidRuleError(value_path, 'value must be one of the allowed choices')

    else:
        raise InvalidRuleError(op_path, f'unsupported field type {ftype!r}')


def _bad_op(op_path, op, ftype):
    raise InvalidRuleError(op_path, f'operator {op!r} is not allowed for {ftype} fields')


def _check_list(value, path):
    if not isinstance(value, list) or not value:
        raise InvalidRuleError(path, 'must be a non-empty list')


def _in_choices(value, choices):
    return isinstance(value, str) and value in (choices or [])


def _parse_decimal(text):
    try:
        number = Decimal(text.strip())
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


def _is_number(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, Decimal):
        return value.is_finite()
    if isinstance(value, str):
        return _parse_decimal(value) is not None
    return False
