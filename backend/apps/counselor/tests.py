import json
from django.test import TestCase
from rest_framework.test import APIClient

from apps.counselor.models import (
    ServiceCenter,
    CounselorUser,
    CitizenCase,
    CitizenConsentRecord,
    CaseAccessAuditLog,
    CounselorCaseNote,
)
from apps.counselor.services import CounselorService
from apps.counselor.permissions import COUNSELOR_TOKENS


class CSCCounselorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        CounselorService.seed_default_centers_and_counselors()
        self.counselor_sangli = CounselorUser.objects.get(username="counselor_sangli")
        self.supervisor_sangli = CounselorUser.objects.get(username="supervisor_sangli")
        self.counselor_nashik = CounselorUser.objects.get(username="counselor_nashik")

    def test_counselor_authentication_and_assigned_center(self):
        """Counselor logs in and retrieves assigned Kendra details."""
        res = self.client.post("/api/v1/counselor/auth/login/", data={
            "demo_user": "counselor_sangli"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["username"], "counselor_sangli")
        self.assertEqual(data["user"]["center"]["code"], "CSC_SANGLI_412")
        self.assertEqual(data["user"]["role"], "COUNSELOR")

    def test_case_registration_and_mandatory_consent(self):
        """Case registration must record explicit citizen consent and create audit log."""
        token = "test-token-sangli"
        COUNSELOR_TOKENS[token] = self.counselor_sangli.id

        payload = {
            "citizen_name": "Tanvi Jadhav",
            "citizen_mobile": "+919876543210",
            "target_scheme_category": "Higher Education & Scholarships",
            "priority": "HIGH",
            "consent_method": "IN_PERSON_VERBAL",
            "initial_notes": "First-generation learner seeking B.Tech tuition fee waiver."
        }
        res = self.client.post(
            "/api/v1/counselor/cases/",
            data=payload,
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        case_data = data["case"]
        self.assertTrue(case_data["case_number"].startswith("CS-"))
        self.assertEqual(case_data["citizen_name"], "Tanvi Jadhav")
        self.assertEqual(case_data["consent"]["consent_status"], "ACTIVE")

        # Verify audit log exists
        case = CitizenCase.objects.get(id=case_data["id"])
        self.assertTrue(case.audit_logs.filter(action="CASE_CREATED").exists())

    def test_cross_center_access_restrictions(self):
        """Counselor from Nashik must be blocked from accessing Sangli case."""
        # 1. Sangli counselor creates case
        case = CounselorService.register_citizen_case(
            counselor=self.counselor_sangli,
            citizen_name="Amol Shinde",
            citizen_mobile="+919822112233"
        )

        # 2. Nashik counselor attempts to access the Sangli case
        nashik_token = "test-nashik-token"
        COUNSELOR_TOKENS[nashik_token] = self.counselor_nashik.id

        res = self.client.get(
            f"/api/v1/counselor/cases/{case.id}/",
            HTTP_AUTHORIZATION=f"Bearer {nashik_token}"
        )
        # Must be forbidden with 403
        self.assertEqual(res.status_code, 403)
        self.assertIn("Cross-center access is strictly forbidden", res.json()["detail"])

        # Audit log must record the unauthorized access block
        blocked_log = CaseAccessAuditLog.objects.filter(case=case, action="UNAUTHORIZED_ACCESS_BLOCKED").first()
        self.assertIsNotNone(blocked_log)
        self.assertEqual(blocked_log.counselor, self.counselor_nashik)

    def test_consent_withdrawal_blocks_profile_access(self):
        """When citizen withdraws consent, counselor access to profile is immediately revoked."""
        token = "token-sangli-consent"
        COUNSELOR_TOKENS[token] = self.counselor_sangli.id

        case = CounselorService.register_citizen_case(
            counselor=self.counselor_sangli,
            citizen_name="Prakash Patil"
        )

        # Withdraw consent
        withdraw_res = self.client.post(
            f"/api/v1/counselor/cases/{case.id}/withdraw_consent/",
            data={"reason": "Citizen decided to apply independently."},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(withdraw_res.status_code, 200)

        # Subsequent profile update must be rejected with 403
        update_res = self.client.post(
            f"/api/v1/counselor/cases/{case.id}/update_profile/",
            data=json.dumps({"profile": {"annual_family_income": 120000}}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(update_res.status_code, 403)
        self.assertIn("has been withdrawn", update_res.json()["detail"])

    def test_counselor_to_supervisor_escalation(self):
        """Counselor escalates case; supervisor reviews note and case status."""
        token = "token-escalation"
        COUNSELOR_TOKENS[token] = self.counselor_sangli.id

        case = CounselorService.register_citizen_case(
            counselor=self.counselor_sangli,
            citizen_name="Meena More"
        )

        res = self.client.post(
            f"/api/v1/counselor/cases/{case.id}/escalate/",
            data={"reason": "Annual family income border case exceeds ceiling by ₹5,000. Seeking RTS appeal review."},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(res.status_code, 200)

        case.refresh_from_db()
        self.assertTrue(case.escalated_to_supervisor)
        self.assertEqual(case.case_status, "ESCALATED_SUPERVISOR")
        self.assertTrue(case.notes.filter(note_type="SUPERVISOR_REMARK").exists())

    def test_case_closure_and_handover(self):
        """Case closure records handover summary to citizen."""
        token = "token-closure"
        COUNSELOR_TOKENS[token] = self.counselor_sangli.id

        case = CounselorService.register_citizen_case(
            counselor=self.counselor_sangli,
            citizen_name="Ganesh Sawant"
        )

        res = self.client.post(
            f"/api/v1/counselor/cases/{case.id}/close/",
            data={"summary": "Handed over printed MahaDBT acknowledgment slip and Aaple Sarkar certificate checklist."},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(res.status_code, 200)

        case.refresh_from_db()
        self.assertEqual(case.case_status, "CLOSED_HANDOVER")
        self.assertIsNotNone(case.closed_at)

    def test_assisted_intake_and_eligibility_discovery_reuse(self):
        """Assisted intake updates profile and reuses deterministic eligibility engine."""
        token = "token-intake"
        COUNSELOR_TOKENS[token] = self.counselor_sangli.id

        case = CounselorService.register_citizen_case(
            counselor=self.counselor_sangli,
            citizen_name="Rohit Koli"
        )

        # Update profile with verified data
        update_payload = {
            "profile": {
                "age": 20,
                "gender": "MALE",
                "state": "Maharashtra",
                "district": "Sangli",
                "caste_category": "OBC",
                "annual_family_income": 120000.0,
                "current_course_level": "PROFESSIONAL_DEGREE",
                "admission_quota": "CAP_ROUND",
                "has_aadhaar_seeded_bank": True
            }
        }
        res = self.client.post(
            f"/api/v1/counselor/cases/{case.id}/update_profile/",
            data=json.dumps(update_payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("eligibility", data)
        self.assertIn("results", data["eligibility"])

        # Preflight Audit Reuse
        preflight_res = self.client.post(
            f"/api/v1/counselor/cases/{case.id}/preflight/",
            data={"scheme_code": "MH_DTE_EBC_2024"},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(preflight_res.status_code, 200)
        self.assertIn("preflight_audit", preflight_res.json())

    def test_center_analytics_aggregation_no_pii(self):
        """Analytics endpoint returns Kendra aggregate figures with zero citizen PII."""
        token = "token-analytics"
        COUNSELOR_TOKENS[token] = self.counselor_sangli.id

        CounselorService.register_citizen_case(counselor=self.counselor_sangli, citizen_name="Citizen A")
        CounselorService.register_citizen_case(counselor=self.counselor_sangli, citizen_name="Citizen B")

        res = self.client.get("/api/v1/counselor/analytics/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("center", data)
        self.assertEqual(data["center"]["code"], "CSC_SANGLI_412")
        self.assertIn("metrics", data)
        self.assertGreaterEqual(data["metrics"]["total_cases_handled"], 2)

        # Zero PII check: citizen names or mobile numbers must NOT exist in analytics output
        analytics_str = json.dumps(data)
        self.assertNotIn("Citizen A", analytics_str)
        self.assertNotIn("Citizen B", analytics_str)
