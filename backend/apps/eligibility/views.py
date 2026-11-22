from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme
from .models import EligibilityAssessment
from .engine import RuleEngine
from .stacking import StackingOptimizer
from .family import FamilyBenefitsService
from .preflight import ApplicationPreflightService
from .what_if import WhatIfSimulatorService


def evaluate_profile_data(profile_data):
    """Deterministic eligibility evaluation shared by the evaluate endpoint and the intake assistant."""
    # Retrieve active schemes
    schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

    evaluated_results = []
    counts = {
        "total": len(schemes),
        "likely_eligible": 0,
        "near_eligible": 0,
        "needs_confirmation": 0,
        "ineligible": 0
    }

    for s in schemes:
        eval_res = RuleEngine.evaluate_scheme(s, profile_data)
        st = eval_res["status"]
        if st == "LIKELY_ELIGIBLE":
            counts["likely_eligible"] += 1
        elif st == "NEAR_ELIGIBLE":
            counts["near_eligible"] += 1
        elif st == "NEEDS_CONFIRMATION":
            counts["needs_confirmation"] += 1
        else:
            counts["ineligible"] += 1

        evaluated_results.append(eval_res)

    # Run Scholarship Stacking & Conflict Detection Optimizer
    stacking_result = StackingOptimizer.optimize_bundle(evaluated_results)

    return {
        "summary": counts,
        "results": evaluated_results,
        "stacking_bundle": stacking_result
    }


class EvaluateEligibilityView(APIView):
    def post(self, request):
        session_token = request.data.get('session_token')
        profile_data = request.data.get('profile')

        # Load profile from token if not directly supplied
        if not profile_data and session_token:
            try:
                profile_obj = StudentProfile.objects.get(session_token=session_token)
                profile_data = {
                    "age": profile_obj.age,
                    "gender": profile_obj.gender,
                    "state": profile_obj.state,
                    "district": profile_obj.district,
                    "is_maharashtra_domicile": profile_obj.is_maharashtra_domicile,
                    "caste_category": profile_obj.caste_category,
                    "annual_family_income": profile_obj.annual_family_income,
                    "current_course_level": profile_obj.current_course_level,
                    "admission_quota": profile_obj.admission_quota,
                    "accommodation_type": profile_obj.accommodation_type,
                    "parent_is_farmer": profile_obj.parent_is_farmer,
                    "parent_land_acres": profile_obj.parent_land_acres,
                    "previous_year_percentage": profile_obj.previous_year_percentage,
                }
            except StudentProfile.DoesNotExist:
                return Response({"error": "Profile not found for session_token"}, status=status.HTTP_404_NOT_FOUND)
        elif not profile_data:
            return Response({"error": "Either session_token or profile data must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(evaluate_profile_data(profile_data))


class FamilyEligibilityView(APIView):
    """
    Evaluates family-level benefits discovery across household members.
    Supports GET with ?persona=rohan_obc or POST with custom members list.
    """
    def get(self, request):
        persona = request.query_params.get('persona', 'rohan_obc')
        data = FamilyBenefitsService.get_family_assessment(persona_key=persona)
        return Response(data)

    def post(self, request):
        persona = request.data.get('persona', 'rohan_obc')
        custom_data = request.data.get('custom_family')
        data = FamilyBenefitsService.get_family_assessment(persona_key=persona, custom_family_data=custom_data)
        return Response(data)


class ApplicationPreflightView(APIView):
    """
    Performs deterministic 6-point pre-submission verification for a scheme.
    POST /api/v1/eligibility/preflight/
    """
    def post(self, request):
        scheme_code = request.data.get("scheme_code")
        if not scheme_code:
            return Response({"error": "scheme_code is required"}, status=status.HTTP_400_BAD_REQUEST)

        token = request.data.get("session_token")
        profile_data = request.data.get("profile")
        if not profile_data and token:
            try:
                profile_obj = StudentProfile.objects.get(session_token=token)
                profile_data = {
                    "age": profile_obj.age,
                    "gender": profile_obj.gender,
                    "state": profile_obj.state,
                    "district": profile_obj.district,
                    "is_maharashtra_domicile": profile_obj.is_maharashtra_domicile,
                    "caste_category": profile_obj.caste_category,
                    "annual_family_income": profile_obj.annual_family_income,
                    "current_course_level": profile_obj.current_course_level,
                    "admission_quota": profile_obj.admission_quota,
                    "accommodation_type": profile_obj.accommodation_type,
                    "parent_is_farmer": profile_obj.parent_is_farmer,
                    "parent_land_acres": profile_obj.parent_land_acres,
                    "previous_year_percentage": profile_obj.previous_year_percentage,
                }
            except StudentProfile.DoesNotExist:
                profile_data = {}
        elif not profile_data:
            profile_data = {}

        checked_docs = request.data.get("checked_documents", [])
        custom_params = request.data.get("custom_audit_params", {})
        result = ApplicationPreflightService.run_preflight_audit(
            scheme_code=scheme_code,
            profile_data=profile_data,
            checked_doc_codes=checked_docs,
            custom_audit_params=custom_params
        )
        return Response(result)


class WhatIfPresetScenariosView(APIView):
    """
    Returns 1-click preset what-if life event scenarios.
    GET /api/v1/eligibility/what_if/presets/
    """
    def get(self, request):
        return Response({"scenarios": WhatIfSimulatorService.get_preset_scenarios()})


class WhatIfSimulationView(APIView):
    """
    Runs interactive what-if eligibility simulation comparing baseline vs simulated changes.
    POST /api/v1/eligibility/what_if/
    {
      "session_token": "...",
      "preset_scenario_id": "advance_education_degree",
      "modifications": {"annual_family_income": 120000, ...}
    }
    """
    def post(self, request):
        token = request.data.get("session_token")
        modifications = request.data.get("modifications", {})
        scenario_id = request.data.get("preset_scenario_id")

        profile_data = {}
        if token:
            try:
                profile_obj = StudentProfile.objects.get(session_token=token)
                profile_data = {
                    "age": profile_obj.age,
                    "gender": profile_obj.gender,
                    "state": profile_obj.state,
                    "district": profile_obj.district,
                    "is_maharashtra_domicile": profile_obj.is_maharashtra_domicile,
                    "caste_category": profile_obj.caste_category,
                    "annual_family_income": profile_obj.annual_family_income,
                    "current_course_level": profile_obj.current_course_level,
                    "admission_quota": profile_obj.admission_quota,
                    "accommodation_type": profile_obj.accommodation_type,
                    "parent_is_farmer": profile_obj.parent_is_farmer,
                    "parent_land_acres": profile_obj.parent_land_acres,
                    "previous_year_percentage": profile_obj.previous_year_percentage,
                }
            except StudentProfile.DoesNotExist:
                profile_data = {}

        if not profile_data and "profile" in request.data:
            profile_data = request.data.get("profile", {})

        simulation_res = WhatIfSimulatorService.run_simulation(
            baseline_profile=profile_data,
            modifications=modifications,
            preset_scenario_id=scenario_id
        )
        return Response(simulation_res)


