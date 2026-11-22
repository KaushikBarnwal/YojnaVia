import json
import uuid
from django.test import TestCase, Client
from apps.citizens.models import UserProfile, HouseholdMember, Application, VerificationLog
from apps.schemes.models import Scheme, RequiredDocument

class CitizensAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.scheme = Scheme.objects.create(
            code="SAMPLE-TEST-SCHEME",
            name="Sample Test Scheme",
            category="EDUCATION",
            jurisdiction="STATE",
            state="Maharashtra",
            department="Higher Education",
            statutory_gr="GR-TEST",
            benefit_type="TUITION_FEE_WAIVER",
            benefit_amount_text="₹20,000",
            brief_description="Test scheme",
            is_sample=True,
            verification_status="UNVERIFIED",
            is_active=True
        )
        RequiredDocument.objects.create(
            scheme=self.scheme,
            name="Income Certificate",
            description="Tahsildar Income",
            is_mandatory=True,
            sort_order=1
        )

    def test_profile_create_success_and_owner_token(self):
        """Profile creation returns HTTP 201, owner_token, and exposes profile_ref."""
        payload = {
            "display_label": "Sunita Patil (Sample)",
            "state": "Maharashtra",
            "district": "Pune",
            "caste_category": "OBC",
            "annual_household_income_inr": 80000.00,
            "is_sample": True,
            "members": [
                {"relation": "SELF", "label": "Sunita", "age": 34, "annual_income_inr": 80000.00}
            ]
        }
        res = self.client.post('/api/v1/ps5/profiles/', json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn('profile_ref', data)
        self.assertIsNotNone(data['profile_ref'])
        self.assertIn('owner_token', data)

        # Profile stored with hashed token, not raw token
        profile_ref = data['profile_ref']
        profile = UserProfile.objects.get(id=profile_ref)
        self.assertNotEqual(profile.owner_token_hash, data['owner_token'])

    def test_profile_rejects_non_sample(self):
        """Phase 1 must strictly reject is_sample=False."""
        payload = {
            "display_label": "Real Citizen",
            "is_sample": False,
            "state": "Maharashtra"
        }
        res = self.client.post('/api/v1/ps5/profiles/', json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_anti_aadhaar_validation(self):
        """Entering a 12-digit Aadhaar number pattern in text fields must be rejected."""
        payload = {
            "display_label": "Citizen with Aadhaar 1234 5678 9012",
            "is_sample": True,
            "state": "Maharashtra"
        }
        res = self.client.post('/api/v1/ps5/profiles/', json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn("Aadhaar", str(res.content))

    def test_profile_detail_token_authentication(self):
        """Profile detail endpoint requires valid X-Profile-Token header."""
        create_res = self.client.post('/api/v1/ps5/profiles/', json.dumps({
            "display_label": "Sample Token User",
            "is_sample": True,
            "state": "Maharashtra"
        }), content_type='application/json')
        self.assertEqual(create_res.status_code, 201)
        data = create_res.json()
        profile_ref = data['profile_ref']
        token = data['owner_token']

        # Request with correct token -> 200
        get_res = self.client.get(f'/api/v1/ps5/profiles/{profile_ref}/', HTTP_X_PROFILE_TOKEN=token)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()['display_label'], "Sample Token User")

        # Request with wrong token -> 404 (indistinguishable from non-existent)
        bad_res = self.client.get(f'/api/v1/ps5/profiles/{profile_ref}/', HTTP_X_PROFILE_TOKEN='wrong')
        self.assertEqual(bad_res.status_code, 404)

        # Request with missing token -> 404
        no_res = self.client.get(f'/api/v1/ps5/profiles/{profile_ref}/')
        self.assertEqual(no_res.status_code, 404)

    def test_application_lifecycle_and_updates(self):
        """Application creation, duplicate prevention, and patch updates."""
        create_res = self.client.post('/api/v1/ps5/profiles/', json.dumps({
            "display_label": "Applicant Profile",
            "is_sample": True,
            "state": "Maharashtra"
        }), content_type='application/json')
        profile_data = create_res.json()
        profile_ref = profile_data['profile_ref']
        token = profile_data['owner_token']

        # 1. Create Application
        app_res = self.client.post('/api/v1/ps5/applications/', json.dumps({
            "profile_ref": profile_ref,
            "scheme_code": self.scheme.code,
            "status": "IN_PROGRESS",
            "reference_note": "Aaple Sarkar Application Ref 9842"
        }), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
        self.assertEqual(app_res.status_code, 201)
        app_data = app_res.json()
        self.assertIn('application_ref', app_data)
        self.assertIsNotNone(app_data['application_ref'])
        app_ref = app_data['application_ref']

        # 2. Prevent duplicate application for same scheme
        dup_res = self.client.post('/api/v1/ps5/applications/', json.dumps({
            "profile_ref": profile_ref,
            "scheme_code": self.scheme.code
        }), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
        self.assertEqual(dup_res.status_code, 400)

        # 3. List applications
        list_res = self.client.get(f'/api/v1/ps5/applications/?profile_ref={profile_ref}', HTTP_X_PROFILE_TOKEN=token)
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.json()['applications']), 1)

        # 4. Patch update application
        patch_res = self.client.patch(f'/api/v1/ps5/applications/{app_ref}/', json.dumps({
            "status": "SUBMITTED",
            "submitted_on": "2026-11-21",
            "notes": "Verified by college clerk"
        }), content_type='application/json', HTTP_X_PROFILE_TOKEN=token)
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()['status'], "SUBMITTED")
        self.assertEqual(patch_res.json()['submitted_on'], "2026-11-21")

    def test_scheme_list_and_document_retrieval(self):
        """Listing schemes and retrieving required documents."""
        res = self.client.get('/api/v1/ps5/schemes/')
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()['schemes']), 1)

        doc_res = self.client.get(f'/api/v1/ps5/schemes/{self.scheme.code}/documents/')
        self.assertEqual(doc_res.status_code, 200)
        docs = doc_res.json()['required_documents']
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['name'], "Income Certificate")
