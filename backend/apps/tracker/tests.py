from django.test import TestCase
from apps.tracker.lifecycle import EntitlementLifecycleService
from apps.schemes.models import Scheme
from apps.profiles.models import StudentProfile
from apps.tracker.models import ApplicationRecord
from scripts.seed_student_data import seed_documents, seed_schemes

class EntitlementLifecycleTestCase(TestCase):
    def setUp(self):
        docs = seed_documents()
        seed_schemes(docs)
        self.profile = StudentProfile.objects.create(session_token="test_token_123", name="Test Student")
        self.scheme = Scheme.objects.get(code="MH_DTE_EBC_2024")
        self.record = ApplicationRecord.objects.create(
            profile=self.profile,
            scheme=self.scheme,
            status="APPLIED",
            stage="ONLINE_REGISTRATION",
            applied_date="2024-09-15",
            application_reference_number="EBC-9988"
        )

    def test_lifecycle_stages_count(self):
        stages = EntitlementLifecycleService.get_lifecycle_stages()
        self.assertEqual(len(stages), 6)
        keys = [s["id"] for s in stages]
        self.assertEqual(keys, ["DISCOVER", "PREPARE", "APPLY", "FOLLOW_UP", "DECISION", "RENEW"])

    def test_roadmap_generation(self):
        roadmap = EntitlementLifecycleService.get_application_lifecycle_roadmap(self.record)
        self.assertEqual(roadmap["scheme_code"], "MH_DTE_EBC_2024")
        self.assertEqual(roadmap["current_stage"], "ONLINE_REGISTRATION")
        self.assertIn("income_certificate_renewal_deadline", roadmap["renewal_intelligence"])
        self.assertIn("31 March", roadmap["renewal_intelligence"]["income_certificate_renewal_deadline"])
        self.assertIn("reapplication_intelligence", roadmap)
        self.assertEqual(roadmap["total_stages"], 6)

    def test_community_intelligence_endpoint(self):
        response = self.client.get("/api/v1/tracker/community_intelligence/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("privacy_controls", data)
        self.assertEqual(data["privacy_controls"]["k_anonymity_threshold"], 5)
        self.assertTrue(data["privacy_controls"]["zero_pii_certified"])
        self.assertIn("frequently_searched_schemes", data)
        self.assertIn("common_document_barriers", data)
        self.assertIn("preparation_abandonment_funnel", data)
        self.assertIn("confusion_hotspots", data)

    def test_community_intelligence_k_anonymity_suppression(self):
        from apps.tracker.community_intelligence import CommunityGapIntelligenceService
        suppressed = CommunityGapIntelligenceService.apply_k_anonymity(3, k=5)
        self.assertTrue(suppressed["is_suppressed"])
        self.assertIn("<5", suppressed["display"])

        preserved = CommunityGapIntelligenceService.apply_k_anonymity(12, k=5)
        self.assertFalse(preserved["is_suppressed"])
        self.assertEqual(preserved["display"], "12")



