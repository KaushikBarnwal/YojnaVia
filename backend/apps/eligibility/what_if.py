"""
What-If Eligibility Simulation Engine.
Enables citizens to explore how their scheme eligibility, funding amounts, and criteria
change under hypothetical life events (education progression, income shifts, relocation,
living arrangement changes, admission quota mode) without modifying their official profile.
"""

from copy import deepcopy
from typing import Dict, Any, List, Optional
from apps.schemes.models import Scheme
from .engine import RuleEngine
from .stacking import StackingOptimizer


PRESET_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "cap_merit_admission": {
        "id": "cap_merit_admission",
        "title": "Secure Admission via Centralized CAP Round (vs Management Quota)",
        "category": "Admission Mode",
        "description": "See how securing admission through Government CAP Merit Rounds instantly unlocks 50% to 100% tuition waivers under Maharashtra GR TEM-2018/CR-363.",
        "icon": "CheckCircle2",
        "modifications": {
            "admission_quota": "CAP_ROUND"
        }
    },
    "move_to_hostel": {
        "id": "move_to_hostel",
        "title": "Move to a Private Hostel or Rented Room (>30 km from home)",
        "category": "Living Arrangement",
        "description": "Explore how living away from home in a rental accommodation unlocks Dr. Panjabrao Deshmukh or Dr. Ambedkar Swadhar hostel maintenance allowances (up to ₹30,000 - ₹51,000/yr).",
        "icon": "Home",
        "modifications": {
            "accommodation_type": "PRIVATE_RENTAL_PG"
        }
    },
    "advance_education_degree": {
        "id": "advance_education_degree",
        "title": "Enroll in Professional Degree / Technical Diploma (CAP Merit)",
        "category": "Education Progression",
        "description": "See how enrolling in professional engineering, pharmacy, or polytechnic programs unlocks high-value DTE tuition and living allowances.",
        "icon": "GraduationCap",
        "modifications": {
            "current_course_level": "PROFESSIONAL_DEGREE",
            "admission_quota": "CAP_ROUND"
        }
    },
    "income_drop_below_1lakh": {
        "id": "income_drop_below_1lakh",
        "title": "Household Income Falls Under ₹1.0 Lakh (BPL / Marginal)",
        "category": "Income Shift",
        "description": "Simulate what happens if your family's annual income falls into the lowest threshold, unlocking 100% full fee exemptions and maximum maintenance allowances.",
        "icon": "TrendingDown",
        "modifications": {
            "annual_family_income": 80000
        }
    },
    "income_rise_above_8lakh": {
        "id": "income_rise_above_8lakh",
        "title": "Household Income Rises Above ₹8.0 Lakh (Non-Creamy Layer Cap)",
        "category": "Income Shift",
        "description": "Understand the impact of crossing the government's ₹8.0 Lakh non-creamy layer ceiling on mean-tested state scholarships.",
        "icon": "TrendingUp",
        "modifications": {
            "annual_family_income": 950000
        }
    },
    "relocate_out_of_maharashtra": {
        "id": "relocate_out_of_maharashtra",
        "title": "Relocate Residence Outside Maharashtra",
        "category": "Domicile & Residence",
        "description": "See which state-funded welfare schemes strictly require Maharashtra domicile and which central entitlements remain intact.",
        "icon": "MapPin",
        "modifications": {
            "state": "Karnataka",
            "is_maharashtra_domicile": False
        }
    }
}


class WhatIfSimulatorService:
    @classmethod
    def get_preset_scenarios(cls) -> List[Dict[str, Any]]:
        """Returns all available 1-click what-if simulation templates."""
        return list(PRESET_SCENARIOS.values())

    @classmethod
    def run_simulation(
        cls,
        baseline_profile: Dict[str, Any],
        modifications: Dict[str, Any],
        preset_scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs deterministic what-if eligibility simulation.
        Compares baseline evaluation against simulated modifications and produces:
        - Unlocked schemes (newly eligible)
        - Lost schemes (no longer eligible)
        - Net financial benefit delta (in INR)
        - Rule-by-rule criteria diff (which specific clauses flipped)
        - Unchanged criteria
        """
        # 1. Merge modifications into simulated profile
        simulated_profile = deepcopy(baseline_profile)
        for key, value in (modifications or {}).items():
            if value is not None and value != "":
                simulated_profile[key] = value

        # 2. Fetch active schemes
        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

        # 3. Evaluate Baseline
        baseline_results = {}
        for s in schemes:
            eval_res = RuleEngine.evaluate_scheme(s, baseline_profile)
            baseline_results[s.code] = eval_res

        # 4. Evaluate Simulated
        simulated_results = {}
        for s in schemes:
            eval_res = RuleEngine.evaluate_scheme(s, simulated_profile)
            simulated_results[s.code] = eval_res

        # 5. Calculate Bundles for both
        baseline_bundle = StackingOptimizer.optimize_bundle(list(baseline_results.values()))
        simulated_bundle = StackingOptimizer.optimize_bundle(list(simulated_results.values()))

        baseline_val = baseline_bundle.get("total_package_value", 0)
        simulated_val = simulated_bundle.get("total_package_value", 0)
        financial_delta = simulated_val - baseline_val

        # 6. Diff Scheme States
        newly_unlocked = []
        lost_schemes = []
        retained_schemes = []
        all_scheme_diffs = []

        for s in schemes:
            b_res = baseline_results[s.code]
            s_res = simulated_results[s.code]

            b_status = b_res["status"]
            s_status = s_res["status"]

            # Criteria diff
            b_passed_reasons = {p.get("field", str(i)): p.get("reason", "") for i, p in enumerate(b_res.get("passed_criteria", []))}
            s_passed_reasons = {p.get("field", str(i)): p.get("reason", "") for i, p in enumerate(s_res.get("passed_criteria", []))}
            b_failed_reasons = {f.get("field", str(i)): f.get("reason", "") for i, f in enumerate(b_res.get("failed_criteria", []))}
            s_failed_reasons = {f.get("field", str(i)): f.get("reason", "") for i, f in enumerate(s_res.get("failed_criteria", []))}

            flipped_to_pass = []
            flipped_to_fail = []

            for rule_id, reason in s_passed_reasons.items():
                if rule_id not in b_passed_reasons:
                    flipped_to_pass.append({"rule": rule_id, "reason": reason})

            for rule_id, reason in s_failed_reasons.items():
                if rule_id not in b_failed_reasons:
                    flipped_to_fail.append({"rule": rule_id, "reason": reason})

            scheme_diff = {
                "code": s.code,
                "name": s.name,
                "benefit_amount_text": s.benefit_amount_text,
                "baseline_status": b_status,
                "simulated_status": s_status,
                "status_changed": b_status != s_status,
                "flipped_to_pass": flipped_to_pass,
                "flipped_to_fail": flipped_to_fail,
                "gr_citation": s.rules_summary.get("gr_citation", "") if hasattr(s, "rules_summary") else ""
            }
            all_scheme_diffs.append(scheme_diff)

            is_base_eligible = b_status in ("LIKELY_ELIGIBLE", "NEAR_ELIGIBLE")
            is_sim_eligible = s_status in ("LIKELY_ELIGIBLE", "NEAR_ELIGIBLE")

            if not is_base_eligible and is_sim_eligible:
                newly_unlocked.append(scheme_diff)
            elif is_base_eligible and not is_sim_eligible:
                lost_schemes.append(scheme_diff)
            elif is_base_eligible and is_sim_eligible:
                retained_schemes.append(scheme_diff)

        scenario_meta = PRESET_SCENARIOS.get(preset_scenario_id) if preset_scenario_id else None

        return {
            "simulation_id": preset_scenario_id or "custom_simulation",
            "scenario_title": scenario_meta["title"] if scenario_meta else "Custom Life Event Simulation",
            "modifications_applied": modifications,
            "financial_impact": {
                "baseline_total_inr": baseline_val,
                "simulated_total_inr": simulated_val,
                "delta_inr": financial_delta,
                "delta_formatted": f"{'+' if financial_delta >= 0 else ''}₹{financial_delta:,}"
            },
            "summary": {
                "newly_unlocked_count": len(newly_unlocked),
                "lost_schemes_count": len(lost_schemes),
                "retained_count": len(retained_schemes),
                "total_schemes_simulated": len(schemes)
            },
            "newly_unlocked_schemes": newly_unlocked,
            "lost_schemes": lost_schemes,
            "retained_schemes": retained_schemes,
            "all_scheme_diffs": all_scheme_diffs,
            "simulated_stacking_bundle": simulated_bundle,
            "legal_guardrail_disclaimer": (
                "Hypothetical Simulation Notice: This interactive simulator is intended strictly for educational and future financial planning. "
                "Simulated outcomes do not represent official sanction or entitlement approvals. Official applications on MahaDBT must reflect "
                "legally valid civil documents issued by competent revenue authorities. Never misrepresent current facts in formal submissions."
            )
        }
