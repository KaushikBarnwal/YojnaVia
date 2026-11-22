from django.test import TestCase
from apps.schemes.models import Scheme
from apps.documents.models import Document, SchemeDocumentRequirement
from apps.eligibility.engine import RuleEngine
from apps.eligibility.stacking import StackingOptimizer
from apps.eligibility.what_if import WhatIfSimulatorService
from apps.documents.graph import DocumentGraphService
from apps.profiles.views import DEMO_PERSONAS
from scripts.seed_student_data import seed_documents, seed_schemes

class EligibilityAndStackingTestCase(TestCase):
    def setUp(self):
        docs = seed_documents()
        seed_schemes(docs)

    def test_rohan_obc_stacking_bundle(self):
        """
        Rohan: 20yo OBC Mech Engg, Income ₹1.1L, Pune rental room, farmer parents.
        Expected:
        - Eligible for OBC Scholarship (Tuition)
        - Eligible for Panjabrao Deshmukh (Hostel Allowance)
        - Recommended Bundle: Both stacked together for ~₹70,000/year!
        """
        rohan_data = DEMO_PERSONAS["rohan_obc"]
        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

        evaluations = [RuleEngine.evaluate_scheme(s, rohan_data) for s in schemes]
        status_map = {e["code"]: e["status"] for e in evaluations}

        self.assertEqual(status_map.get("MH_OBC_POSTMATRIC_2024"), "LIKELY_ELIGIBLE")
        self.assertEqual(status_map.get("MH_PANJABRAO_HOSTEL_2024"), "LIKELY_ELIGIBLE")
        self.assertEqual(status_map.get("MH_DTE_EBC_2024"), "INELIGIBLE") # OBC, not Open/EWS

        bundle = StackingOptimizer.optimize_bundle(evaluations)
        self.assertGreaterEqual(len(bundle["recommended_bundle"]), 2)
        self.assertGreaterEqual(bundle["total_package_value"], 70000)

    def test_sneha_ebc_pharmacy(self):
        """
        Sneha: 19yo Female, Open/General, Income ₹3.2L, Day Scholar.
        Expected:
        - Eligible for EBC (RCSM) 50% tuition reimbursement
        - Ineligible for OBC/SC schemes
        """
        sneha_data = DEMO_PERSONAS["sneha_ebc"]
        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

        evaluations = [RuleEngine.evaluate_scheme(s, sneha_data) for s in schemes]
        status_map = {e["code"]: e["status"] for e in evaluations}

        self.assertEqual(status_map.get("MH_DTE_EBC_2024"), "LIKELY_ELIGIBLE")
        self.assertEqual(status_map.get("MH_OBC_POSTMATRIC_2024"), "INELIGIBLE")
        self.assertEqual(status_map.get("MH_SC_POSTMATRIC_2024"), "INELIGIBLE")

    def test_vikas_sc_polytechnic(self):
        """
        Vikas: 18yo SC student, Income ₹65k, Private rental room.
        Expected:
        - Eligible for SC Post-Matric Scholarship (100% Tuition + Stipend)
        - Eligible for Swadhar Yojana (₹48,000 - ₹51,000/yr Living Allowance)
        - Stacked Bundle value >= ₹1,00,000
        """
        vikas_data = DEMO_PERSONAS["vikas_sc"]
        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

        evaluations = [RuleEngine.evaluate_scheme(s, vikas_data) for s in schemes]
        status_map = {e["code"]: e["status"] for e in evaluations}

        self.assertEqual(status_map.get("MH_SC_POSTMATRIC_2024"), "LIKELY_ELIGIBLE")
        self.assertEqual(status_map.get("MH_SWADHAR_SC_2024"), "LIKELY_ELIGIBLE")

        bundle = StackingOptimizer.optimize_bundle(evaluations)
        self.assertGreaterEqual(len(bundle["recommended_bundle"]), 2)
        self.assertGreaterEqual(bundle["total_package_value"], 100000)

    def test_pooja_borderline_near_eligible(self):
        """
        Pooja: OBC student with income ₹1.65L (exceeds ₹1.5L cutoff by ₹15k).
        Expected:
        - Evaluates to NEAR_ELIGIBLE for OBC Post-Matric with boundary guidance
        """
        pooja_data = DEMO_PERSONAS["pooja_borderline"]
        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

        evaluations = [RuleEngine.evaluate_scheme(s, pooja_data) for s in schemes]
        status_map = {e["code"]: e["status"] for e in evaluations}

        self.assertEqual(status_map.get("MH_OBC_POSTMATRIC_2024"), "NEAR_ELIGIBLE")
        obc_eval = next(e for e in evaluations if e["code"] == "MH_OBC_POSTMATRIC_2024")
        self.assertTrue("Boundary" in obc_eval["near_eligible_guidance"] or len(obc_eval["near_eligible_criteria"]) > 0)

    def test_document_graph_multiplier(self):
        """
        Test that Tahsildar Income Certificate is identified as the top multiplier document.
        """
        graph = DocumentGraphService.get_document_dependency_graph()
        self.assertIsNotNone(graph["top_multiplier_document"])
        self.assertIn("INCOME", graph["top_multiplier_document"]["code"])
        self.assertGreaterEqual(graph["top_multiplier_document"]["schemes_count"], 3)

    def test_what_if_hostel_allowance_unlock(self):
        """
        Test that moving a Day Scholar to Private Rental unlocks Panjabrao Deshmukh Hostel Allowance.
        """
        sneha = dict(DEMO_PERSONAS["sneha_ebc"])
        sneha["accommodation_type"] = "DAY_SCHOLAR"

        result = WhatIfSimulatorService.run_simulation(
            baseline_profile=sneha,
            modifications={"accommodation_type": "PRIVATE_RENTAL_PG"}
        )

        unlocked_codes = [s["code"] for s in result["newly_unlocked_schemes"]]
        self.assertIn("MH_PANJABRAO_HOSTEL_2024", unlocked_codes)
        self.assertGreater(result["financial_impact"]["delta_inr"], 0)

    def test_what_if_presets_available(self):
        """
        Test that PRESET_SCENARIOS are properly configured with labels, tags, and valid modifications.
        """
        presets = WhatIfSimulatorService.get_preset_scenarios()
        self.assertGreaterEqual(len(presets), 5)
        keys = [p["id"] for p in presets]
        self.assertIn("move_to_hostel", keys)
        self.assertIn("income_rise_above_8lakh", keys)
