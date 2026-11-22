"""Tri-state evaluator tests (TEST data only)."""

from django.test import SimpleTestCase

from apps.eligibility_engine.evaluator import evaluate_scheme
from apps.eligibility_engine.fields import FIELD_REGISTRY

REQUIRED_LEAF_KEYS = (
    'field',
    'operator',
    'required_value',
    'actual_value',
    'result',
    'explanation',
    'source_ref',
)
FORBIDDEN_PHRASES = (
    'change your',
    'reduce your',
    'increase your',
    'bypass',
    'avoid the rule',
)


def meta(verified=True, sample=False):
    return {
        'code': 'TEST-SCHEME-A',
        'name': 'TEST',
        'is_sample': sample,
        'verification_status': 'VERIFIED' if verified else 'UNVERIFIED',
        'official_source_url': 'https://example.invalid/test',
        'last_verified_on': '2024-01-01',
    }


def facts(**kw):
    values = {name: None for name in FIELD_REGISTRY}
    values.update(kw)
    return values


def leaf(rule_id, field, op, value, mandatory=None, remedy=None):
    node = {
        'id': rule_id,
        'description': f'Test condition {rule_id}',
        'field': field,
        'op': op,
        'value': value,
    }
    if mandatory is not None:
        node['mandatory'] = mandatory
    if remedy is not None:
        node['remedy'] = remedy
    return node


def group(kind, rule_id, *children):
    return {
        'id': rule_id,
        'description': f'Test group {rule_id}',
        kind: list(children),
    }


def negation(rule_id, child):
    return {
        'id': rule_id,
        'description': f'Test negation {rule_id}',
        'not': child,
    }


def wrap(*clauses):
    return {'clauses': list(clauses)}


def iter_nodes(node):
    yield node
    for child in node.get('children', []):
        yield from iter_nodes(child)


def all_nodes(result):
    for top in result['criteria']:
        yield from iter_nodes(top)


class MandatoryOutcomeTests(SimpleTestCase):
    def test_all_matching_is_likely_eligible(self):
        criteria = wrap(
            leaf('age_min', 'age_years', 'gte', 18, mandatory=True),
            leaf('state_match', 'state', 'eq', 'Maharashtra', mandatory=True),
        )
        result = evaluate_scheme(criteria, facts(age_years=20, state='Maharashtra'), meta())
        self.assertEqual(result['outcome'], 'likely_eligible')

    def test_income_above_cap_is_not_eligible(self):
        criteria = wrap(leaf('income_cap', 'annual_household_income_inr', 'lte', 250000, mandatory=True))
        result = evaluate_scheme(criteria, facts(annual_household_income_inr=250001), meta())
        self.assertEqual(result['outcome'], 'not_eligible')
        self.assertIn('income_cap', result['failed_mandatory'])

    def test_boundary_lte_passes_at_exact_value(self):
        criteria = wrap(leaf('income_cap', 'annual_household_income_inr', 'lte', 250000, mandatory=True))
        result = evaluate_scheme(criteria, facts(annual_household_income_inr='250000'), meta())
        self.assertEqual(result['outcome'], 'likely_eligible')

    def test_boundary_lt_fails_at_exact_value(self):
        criteria = wrap(leaf('income_cap', 'annual_household_income_inr', 'lt', 250000, mandatory=True))
        result = evaluate_scheme(criteria, facts(annual_household_income_inr='250000'), meta())
        self.assertEqual(result['outcome'], 'not_eligible')

    def test_age_gte_boundary(self):
        criteria = wrap(leaf('age_min', 'age_years', 'gte', 18, mandatory=True))
        at_18 = evaluate_scheme(criteria, facts(age_years=18), meta())
        at_17 = evaluate_scheme(criteria, facts(age_years=17), meta())
        self.assertEqual(at_18['outcome'], 'likely_eligible')
        self.assertEqual(at_17['outcome'], 'not_eligible')

    def test_missing_income_needs_confirmation(self):
        criteria = wrap(leaf('income_cap', 'annual_household_income_inr', 'lte', 250000, mandatory=True))
        result = evaluate_scheme(criteria, facts(annual_household_income_inr=None), meta())
        self.assertEqual(result['outcome'], 'needs_confirmation')
        fields = [entry['field'] for entry in result['missing_fields']]
        self.assertIn('annual_household_income_inr', fields)

    def test_mandatory_fail_plus_mandatory_unknown_is_not_eligible(self):
        criteria = wrap(
            leaf('age_min', 'age_years', 'gte', 18, mandatory=True),
            leaf('income_cap', 'annual_household_income_inr', 'lte', 250000, mandatory=True),
        )
        result = evaluate_scheme(
            criteria,
            facts(age_years=16, annual_household_income_inr=None),
            meta(),
        )
        self.assertEqual(result['outcome'], 'not_eligible')

    def test_optional_fail_with_mandatory_pass_is_likely_eligible(self):
        criteria = wrap(
            leaf('age_min', 'age_years', 'gte', 18, mandatory=True),
            leaf('state_opt', 'state', 'eq', 'Maharashtra', mandatory=False),
        )
        result = evaluate_scheme(criteria, facts(age_years=20, state='Karnataka'), meta())
        self.assertEqual(result['outcome'], 'likely_eligible')

    def test_optional_unknown_is_likely_eligible(self):
        criteria = wrap(
            leaf('age_min', 'age_years', 'gte', 18, mandatory=True),
            leaf('income_opt', 'annual_household_income_inr', 'lte', 100000, mandatory=False),
        )
        result = evaluate_scheme(criteria, facts(age_years=20, annual_household_income_inr=None), meta())
        self.assertEqual(result['outcome'], 'likely_eligible')


class NestedLogicTests(SimpleTestCase):
    def criteria(self):
        return wrap(group(
            'any',
            'eligible_path',
            group(
                'all',
                'age_and_state',
                leaf('age_min', 'age_years', 'gte', 18),
                leaf('state_match', 'state', 'eq', 'Maharashtra'),
            ),
            leaf('income_low', 'annual_household_income_inr', 'lte', 100000),
        ))

    def test_first_branch_passes(self):
        result = evaluate_scheme(
            self.criteria(),
            facts(age_years=20, state='Maharashtra', annual_household_income_inr=500000),
            meta(),
        )
        self.assertEqual(result['outcome'], 'likely_eligible')

    def test_second_branch_passes(self):
        result = evaluate_scheme(
            self.criteria(),
            facts(age_years=16, state='Karnataka', annual_household_income_inr=50000),
            meta(),
        )
        self.assertEqual(result['outcome'], 'likely_eligible')

    def test_both_branches_fail(self):
        result = evaluate_scheme(
            self.criteria(),
            facts(age_years=16, state='Karnataka', annual_household_income_inr=500000),
            meta(),
        )
        self.assertEqual(result['outcome'], 'not_eligible')


class NotOperatorTests(SimpleTestCase):
    def criteria(self):
        return wrap(negation(
            'not_domicile',
            leaf('domicile_true', 'is_maharashtra_domicile', 'eq', True),
        ))

    def test_negated_true_is_not_eligible(self):
        result = evaluate_scheme(self.criteria(), facts(is_maharashtra_domicile=True), meta())
        self.assertEqual(result['outcome'], 'not_eligible')

    def test_negated_unknown_needs_confirmation(self):
        result = evaluate_scheme(self.criteria(), facts(is_maharashtra_domicile=None), meta())
        self.assertEqual(result['outcome'], 'needs_confirmation')


class OperatorTests(SimpleTestCase):
    def test_contains_passes_when_value_present(self):
        criteria = wrap(leaf('has_spouse', 'member_relations', 'contains', 'SPOUSE', mandatory=True))
        result = evaluate_scheme(
            criteria,
            facts(member_relations=['SELF', 'SPOUSE']),
            meta(),
        )
        self.assertEqual(result['outcome'], 'likely_eligible')

    def test_contains_fails_when_value_absent(self):
        criteria = wrap(leaf('has_spouse', 'member_relations', 'contains', 'SPOUSE', mandatory=True))
        result = evaluate_scheme(criteria, facts(member_relations=['SELF']), meta())
        self.assertEqual(result['outcome'], 'not_eligible')

    def test_in_passes_when_member_of_list(self):
        criteria = wrap(leaf('caste_in', 'caste_category', 'in', ['SC', 'ST'], mandatory=True))
        result = evaluate_scheme(criteria, facts(caste_category='SC'), meta())
        self.assertEqual(result['outcome'], 'likely_eligible')


class EdgeCriteriaTests(SimpleTestCase):
    def test_empty_clauses_needs_confirmation_with_warning(self):
        result = evaluate_scheme({'clauses': []}, facts(), meta())
        self.assertEqual(result['outcome'], 'needs_confirmation')
        self.assertTrue(result['warnings'])

    def test_empty_criteria_needs_confirmation_with_message(self):
        result = evaluate_scheme({}, facts(), meta())
        self.assertEqual(result['outcome'], 'needs_confirmation')
        self.assertTrue(any('No eligibility criteria' in w for w in result['warnings']))

    def test_sample_scheme_carries_sample_warning(self):
        criteria = wrap(leaf('age_min', 'age_years', 'gte', 18, mandatory=True))
        result = evaluate_scheme(criteria, facts(age_years=20), meta(sample=True))
        self.assertTrue(any('SAMPLE TEST DATA' in w for w in result['warnings']))

    def test_unverified_scheme_carries_warning(self):
        criteria = wrap(leaf('age_min', 'age_years', 'gte', 18, mandatory=True))
        result = evaluate_scheme(criteria, facts(age_years=20), meta(verified=False))
        self.assertTrue(any('not verified' in w for w in result['warnings']))


class RecommendationTests(SimpleTestCase):
    REMEDY = {
        'text': 'Check the official notice for the route.',
        'source_ref': 'https://example.invalid/notice',
    }

    def test_fail_with_remedy_produces_recommendation(self):
        criteria = wrap(leaf('age_min', 'age_years', 'gte', 18, mandatory=True, remedy=self.REMEDY))
        result = evaluate_scheme(criteria, facts(age_years=16), meta())
        self.assertEqual(len(result['recommendations']), 1)
        self.assertEqual(result['recommendations'][0]['text'], self.REMEDY['text'])

    def test_fail_without_remedy_produces_no_recommendation(self):
        criteria = wrap(leaf('age_min', 'age_years', 'gte', 18, mandatory=True))
        result = evaluate_scheme(criteria, facts(age_years=16), meta())
        self.assertEqual(result['recommendations'], [])


class ResultShapeTests(SimpleTestCase):
    def sample_result(self):
        criteria = wrap(
            leaf('age_min', 'age_years', 'gte', 18, mandatory=True),
            group(
                'any',
                'route',
                group(
                    'all',
                    'age_and_state',
                    leaf('age_route', 'age_years', 'gte', 21),
                    leaf('state_route', 'state', 'eq', 'Maharashtra'),
                ),
                leaf('income_route', 'annual_household_income_inr', 'lte', 100000),
            ),
            negation('not_domicile', leaf('domicile_true', 'is_maharashtra_domicile', 'eq', True)),
            leaf('has_spouse', 'member_relations', 'contains', 'SPOUSE'),
        )
        return evaluate_scheme(
            criteria,
            facts(age_years=16, state='Karnataka', annual_household_income_inr=50000,
                  is_maharashtra_domicile=None, member_relations=['SELF']),
            meta(),
        )

    def test_every_leaf_has_required_keys(self):
        result = self.sample_result()
        leaves = [node for node in all_nodes(result) if node['type'] == 'leaf']
        self.assertTrue(leaves)
        for node in leaves:
            for key in REQUIRED_LEAF_KEYS:
                self.assertIn(key, node, msg=f'{node["criterion_id"]} missing {key}')

    def test_no_explanation_contains_forbidden_phrase(self):
        result = self.sample_result()
        for node in all_nodes(result):
            text = str(node.get('explanation', '')).lower()
            for phrase in FORBIDDEN_PHRASES:
                self.assertNotIn(phrase, text, msg=f'{node["criterion_id"]}: {text}')


class NoLlmInvariantTests(SimpleTestCase):
    def test_engine_has_no_llm_or_network_dependencies(self):
        import sys
        # Verify no LLM SDK is imported by eligibility_engine
        for mod in ('google.generativeai', 'openai', 'anthropic', 'langchain'):
            self.assertNotIn(mod, sys.modules)

    def test_evaluator_is_strictly_deterministic(self):
        criteria = wrap(
            leaf('age_min', 'age_years', 'gte', 18, mandatory=True),
            leaf('income_cap', 'annual_household_income_inr', 'lte', 250000, mandatory=True),
            leaf('state_mh', 'state', 'eq', 'Maharashtra', mandatory=True),
        )
        profile_facts = facts(age_years=20, annual_household_income_inr='180000', state='Maharashtra')
        first_result = evaluate_scheme(criteria, profile_facts, meta())

        # 50 iterations must yield identical outputs
        for _ in range(50):
            iteration_result = evaluate_scheme(criteria, profile_facts, meta())
            self.assertEqual(iteration_result, first_result)
