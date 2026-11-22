"""API tests for the evaluation endpoint (TEST data only)."""

import hashlib
import json
import secrets

from django.test import Client, TestCase

from apps.citizens.models import HouseholdMember, UserProfile
from apps.schemes.models import Scheme

ENDPOINT = '/api/v1/ps5/evaluations/'


def _iter_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _iter_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_keys(item)


class EvaluationApiTests(TestCase):
    def setUp(self):
        self.raw = secrets.token_urlsafe(32)
        self.profile = UserProfile.objects.create(
            display_label='SAMPLE Student',
            is_sample=True,
            state='Maharashtra',
            age_years=20,
            annual_household_income_inr='150000.00',
            caste_category='OPEN',
            is_maharashtra_domicile=True,
            owner_token_hash=hashlib.sha256(self.raw.encode()).hexdigest(),
        )
        HouseholdMember.objects.create(
            profile=self.profile,
            relation='SELF',
            label='Self',
            age=20,
            is_student=True,
        )
        Scheme.objects.create(
            code='TEST-SCHEME-A',
            name='[SAMPLE TEST DATA] Scheme A',
            department='TEST',
            statutory_gr='TEST DATA',
            official_portal_url='https://example.invalid/',
            benefit_type='BOOK_STATIONERY',
            benefit_amount_text='TEST',
            brief_description='TEST DATA',
            is_sample=True,
            verification_status='UNVERIFIED',
            is_active=True,
            eligibility_criteria={
                'clauses': [
                    {
                        'id': 'income_cap',
                        'description': 'Income at most 250000',
                        'field': 'annual_household_income_inr',
                        'op': 'lte',
                        'value': 250000,
                    },
                ],
            },
        )
        self.client = Client()

    def _post(self, body, token=None):
        extra = {}
        if token is not None:
            extra['HTTP_X_PROFILE_TOKEN'] = token
        return self.client.post(
            ENDPOINT,
            json.dumps(body),
            content_type='application/json',
            **extra,
        )

    def test_request_without_token_returns_404(self):
        response = self._post({'profile_ref': str(self.profile.id)})
        self.assertEqual(response.status_code, 404)

    def test_wrong_token_returns_404(self):
        response = self._post({'profile_ref': str(self.profile.id)}, token='wrong')
        self.assertEqual(response.status_code, 404)

    def test_correct_token_returns_evaluation(self):
        response = self._post({'profile_ref': str(self.profile.id)}, token=self.raw)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['results'][0]['outcome'], 'likely_eligible')

    def test_unknown_scheme_code_returns_400(self):
        response = self._post(
            {'profile_ref': str(self.profile.id), 'scheme_codes': ['NOPE-CODE']},
            token=self.raw,
        )
        self.assertEqual(response.status_code, 400)

    def test_response_does_not_leak_token_or_hash(self):
        response = self._post({'profile_ref': str(self.profile.id)}, token=self.raw)
        body = response.content.decode()
        self.assertNotIn(self.raw, body)
        self.assertNotIn('owner_token_hash', body)

    def test_response_has_no_id_keys(self):
        response = self._post({'profile_ref': str(self.profile.id)}, token=self.raw)
        keys = list(_iter_keys(response.json()))
        self.assertNotIn('id', keys)

    def test_evaluation_not_eligible_outcome(self):
        # Create a scheme that the profile fails (income cap 50000, profile has 150000)
        Scheme.objects.create(
            code='TEST-INELIGIBLE',
            name='Ineligible Scheme',
            department='TEST',
            statutory_gr='TEST',
            official_portal_url='https://example.invalid/',
            benefit_type='MAINTENANCE_STIPEND',
            benefit_amount_text='TEST',
            brief_description='TEST',
            is_sample=True,
            verification_status='UNVERIFIED',
            is_active=True,
            eligibility_criteria={
                'clauses': [
                    {
                        'id': 'low_income',
                        'description': 'Income at most 50000',
                        'field': 'annual_household_income_inr',
                        'op': 'lte',
                        'value': 50000,
                        'mandatory': True,
                    },
                ],
            },
        )
        response = self._post(
            {'profile_ref': str(self.profile.id), 'scheme_codes': ['TEST-INELIGIBLE']},
            token=self.raw,
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()['results'][0]
        self.assertEqual(result['outcome'], 'not_eligible')
        self.assertIn('low_income', result['failed_mandatory'])

    def test_evaluation_needs_confirmation_outcome(self):
        # Profile without income specified should return needs_confirmation on income-capped scheme
        raw2 = secrets.token_urlsafe(32)
        profile_incomplete = UserProfile.objects.create(
            display_label='SAMPLE Incomplete Student',
            is_sample=True,
            owner_token_hash=hashlib.sha256(raw2.encode()).hexdigest(),
        )
        response = self._post(
            {'profile_ref': str(profile_incomplete.id), 'scheme_codes': ['TEST-SCHEME-A']},
            token=raw2,
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()['results'][0]
        self.assertEqual(result['outcome'], 'needs_confirmation')
        self.assertTrue(any(f['field'] == 'annual_household_income_inr' for f in result['missing_fields']))
