import datetime
import json
from django.test import TestCase, Client
from apps.schemes.models import Scheme, SchemeRuleVersion
from apps.profiles.models import StudentProfile
from apps.tracker.models import ApplicationRecord


class Phase5AdminAndTrackerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.scheme = Scheme.objects.create(
            code="MH-PH5-TEST",
            name="Maharashtra Merit Scholarship",
            department="Higher Education",
            category="EDUCATION",
            jurisdiction="STATE",
            state="Maharashtra",
            benefit_type="TUITION_FEE_WAIVER",
            benefit_amount_text="100% Tuition Waiver",
            estimated_annual_value=60000,
            statutory_gr="GR-PH5-2024",
            rules={
                "operator": "ALL",
                "conditions": [
                    {
                        "field": "annual_family_income",
                        "op": "<=",
                        "value": 250000,
                        "label": "Annual Income <= 2.5L",
                        "citation": "GR-PH5-Para2"
                    }
                ]
            },
            verification_status="UNVERIFIED",
            version="2024.1",
            is_active=True
        )

        self.student = StudentProfile.objects.create(
            session_token="test-session-token-p5",
            name="Vaibhav Patil",
            age=21,
            annual_family_income=200000,
            caste_category="OBC",
            state="Maharashtra",
            district="Pune",
            is_maharashtra_domicile=True
        )

        # Create tracked application
        self.app_record = ApplicationRecord.objects.create(
            profile=self.student,
            scheme=self.scheme,
            status="NOT_STARTED",
            stage="DISCOVERED"
        )

    def test_admin_login_success_and_failure(self):
        # 1-Click Demo Login
        r_demo = self.client.post(
            "/api/v1/admin/auth/login/",
            json.dumps({"demo_role": "SCHEME_OFFICER"}),
            content_type="application/json"
        )
        self.assertEqual(r_demo.status_code, 200)
        self.assertIn("token", r_demo.json())
        self.assertEqual(r_demo.json()["user"]["role"], "SCHEME_OFFICER")

        # Credential login
        r_cred = self.client.post(
            "/api/v1/admin/auth/login/",
            json.dumps({"username": "officer", "password": "officer123"}),
            content_type="application/json"
        )
        self.assertEqual(r_cred.status_code, 200)

        # Bad password
        r_bad = self.client.post(
            "/api/v1/admin/auth/login/",
            json.dumps({"username": "officer", "password": "wrong"}),
            content_type="application/json"
        )
        self.assertEqual(r_bad.status_code, 401)

    def test_admin_schemes_list_and_deactivate(self):
        r = self.client.get("/api/v1/admin/schemes/")
        self.assertEqual(r.status_code, 200)
        schemes = r.json()["schemes"]
        self.assertTrue(any(s["code"] == "MH-PH5-TEST" for s in schemes))

        # Deactivate toggle
        r_deact = self.client.post("/api/v1/admin/schemes/MH-PH5-TEST/deactivate/")
        self.assertEqual(r_deact.status_code, 200)
        self.assertFalse(r_deact.json()["is_active"])

        # History should have DEACTIVATED entry
        hist = SchemeRuleVersion.objects.filter(scheme=self.scheme, change_type="DEACTIVATED")
        self.assertTrue(hist.exists())

    def test_verification_status_validation(self):
        # Reject VERIFIED without official_source_url
        r_invalid = self.client.post(
            "/api/v1/admin/schemes/",
            json.dumps({
                "code": "MH-INVALID-VER",
                "name": "Invalid Scheme",
                "verification_status": "VERIFIED",
                "last_verified_on": "2024-11-01"
            }),
            content_type="application/json"
        )
        self.assertEqual(r_invalid.status_code, 400)
        self.assertIn("official_source_url", r_invalid.json()["error"])

    def test_rule_change_and_application_invalidation(self):
        new_rules = {
            "operator": "ALL",
            "conditions": [
                {
                    "field": "annual_family_income",
                    "op": "<=",
                    "value": 150000,
                    "label": "Tighter Income Cutoff <= 1.5L",
                    "citation": "GR-PH5-Amendment-2024"
                }
            ]
        }

        r = self.client.post(
            "/api/v1/admin/schemes/MH-PH5-TEST/rules/",
            json.dumps({
                "rules": new_rules,
                "change_summary": "Lowered income ceiling from 2.5L to 1.5L"
            }),
            content_type="application/json"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["new_version"], "2024.2")
        self.assertEqual(data["affected_applications_count"], 1)

        # Verify application record was marked as needs_re_evaluation
        self.app_record.refresh_from_db()
        self.assertTrue(self.app_record.needs_re_evaluation)
        self.assertIn("Lowered income ceiling", self.app_record.re_evaluation_reason)

        # Check SchemeRuleVersion record
        version_rec = SchemeRuleVersion.objects.get(scheme=self.scheme, version="2024.2")
        self.assertEqual(version_rec.affected_applications_count, 1)

    def test_re_run_matching_endpoint(self):
        r = self.client.post("/api/v1/admin/schemes/MH-PH5-TEST/re_evaluate_matching/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total_applications_re_evaluated"], 1)
        self.assertIn("summary", data)

    def test_tracker_seven_statuses_and_user_reported(self):
        # Update tracker status to APPLIED with reference number and date
        r = self.client.post(
            "/api/v1/tracker/update/",
            json.dumps({
                "session_token": "test-session-token-p5",
                "scheme_code": "MH-PH5-TEST",
                "status": "APPLIED",
                "application_reference_number": "MHD-2024-998877",
                "applied_date": "2026-11-20",
                "submission_mode": "Online MahaDBT Portal",
                "notes": "Scrutiny fee paid online"
            }),
            content_type="application/json"
        )
        self.assertEqual(r.status_code, 200)
        rec = r.json()["record"]
        self.assertEqual(rec["status"], "APPLIED")
        self.assertEqual(rec["application_reference_number"], "MHD-2024-998877")
        self.assertEqual(rec["applied_date"], "2026-11-20")
        self.assertTrue(rec["is_user_reported"])

        # Test Acknowledge Re-Evaluation
        self.app_record.needs_re_evaluation = True
        self.app_record.save()

        r_ack = self.client.post(
            "/api/v1/tracker/acknowledge_re_evaluation/",
            json.dumps({
                "session_token": "test-session-token-p5",
                "scheme_code": "MH-PH5-TEST"
            }),
            content_type="application/json"
        )
        self.assertEqual(r_ack.status_code, 200)
        self.app_record.refresh_from_db()
        self.assertFalse(self.app_record.needs_re_evaluation)
