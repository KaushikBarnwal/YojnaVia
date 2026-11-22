"""Structural validation tests for eligibility criteria (TEST data only)."""

from django.test import SimpleTestCase

from apps.eligibility_engine.schema import InvalidRuleError, validate_criteria


def leaf(rule_id, field, op, value, **extra):
    node = {
        'id': rule_id,
        'description': f'Test condition {rule_id}',
        'field': field,
        'op': op,
        'value': value,
    }
    node.update(extra)
    return node


def wrap(*clauses):
    return {'clauses': list(clauses)}


class ValidCriteriaTests(SimpleTestCase):
    def test_valid_tree_accepted(self):
        criteria = {
            'clauses': [
                {
                    'id': 'age_min',
                    'description': 'Age at least 18',
                    'field': 'age_years',
                    'op': 'gte',
                    'value': 18,
                },
            ],
        }
        validate_criteria(criteria)

    def test_empty_dict_accepted(self):
        validate_criteria({})


class InvalidCriteriaTests(SimpleTestCase):
    def assertInvalid(self, criteria):
        with self.assertRaises(InvalidRuleError):
            validate_criteria(criteria)

    def test_unknown_field_rejected(self):
        self.assertInvalid(wrap(leaf('x_field', 'not_a_field', 'eq', 'A')))

    def test_unknown_op_rejected(self):
        self.assertInvalid(wrap(leaf('x_op', 'age_years', 'between', 18)))

    def test_unknown_top_level_key_rejected(self):
        criteria = wrap(leaf('age_min', 'age_years', 'gte', 18))
        criteria['extra'] = 1
        self.assertInvalid(criteria)

    def test_empty_all_list_rejected(self):
        self.assertInvalid(wrap({'id': 'grp', 'description': 'Group', 'all': []}))

    def test_node_with_all_and_any_rejected(self):
        self.assertInvalid(wrap({
            'id': 'grp',
            'description': 'Group',
            'all': [leaf('a1', 'age_years', 'gte', 18)],
            'any': [leaf('a2', 'age_years', 'gte', 21)],
        }))

    def test_not_given_as_list_rejected(self):
        self.assertInvalid(wrap({
            'id': 'neg',
            'description': 'Negation',
            'not': [leaf('a1', 'age_years', 'gte', 18)],
        }))

    def test_mandatory_on_nested_node_rejected(self):
        self.assertInvalid(wrap({
            'id': 'grp',
            'description': 'Group',
            'all': [leaf('a1', 'age_years', 'gte', 18, mandatory=False)],
        }))

    def test_duplicate_ids_rejected(self):
        self.assertInvalid(wrap(
            leaf('same_id', 'age_years', 'gte', 18),
            leaf('same_id', 'age_years', 'lte', 60),
        ))

    def test_bad_id_format_rejected(self):
        self.assertInvalid(wrap(leaf('Bad-ID', 'age_years', 'gte', 18)))

    def test_contains_on_int_field_rejected(self):
        self.assertInvalid(wrap(leaf('x_contains', 'age_years', 'contains', 18)))

    def test_lt_on_str_field_rejected(self):
        self.assertInvalid(wrap(leaf('x_lt', 'state', 'lt', 'Maharashtra')))

    def test_bool_value_for_int_field_rejected(self):
        self.assertInvalid(wrap(leaf('x_bool', 'age_years', 'gte', True)))

    def test_non_list_value_for_in_on_int_field_rejected(self):
        self.assertInvalid(wrap(leaf('x_in', 'age_years', 'in', 18)))

    def test_depth_seven_not_chain_rejected(self):
        node = leaf('leaf_deep', 'age_years', 'gte', 18)
        for i in range(7):
            node = {'id': f'neg_{i}', 'description': 'Negation', 'not': node}
        self.assertInvalid(wrap(node))

    def test_remedy_without_source_ref_rejected(self):
        self.assertInvalid(wrap(
            leaf('remedy_bad', 'age_years', 'gte', 18, remedy={'text': 'Do something.'}),
        ))

    def test_unknown_enum_choice_rejected(self):
        self.assertInvalid(wrap(leaf('caste_bad', 'caste_category', 'eq', 'XYZ')))
