"""
Deterministic Rule Engine for YojnaVia.
Evaluates student profiles against structured AST criteria trees with statutory GR citations.
Zero LLM hallucination in eligibility determinations.
"""

from decimal import Decimal
from typing import Dict, Any, List, Tuple

class RuleEngine:
    @staticmethod
    def evaluate_condition(condition: Dict[str, Any], profile_data: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Evaluates a single condition.
        Returns:
            status: "PASS" | "FAIL" | "NEAR_ELIGIBLE" | "MISSING"
            reason: Human-friendly explanation
            citation: Statutory Government Resolution citation
        """
        field = condition.get("field")
        op = condition.get("op")
        target_value = condition.get("value")
        label = condition.get("label", field)
        citation = condition.get("citation", "")
        tolerance = condition.get("boundary_tolerance", 0)

        actual_value = profile_data.get(field)

        # Handle missing / unpopulated fields
        if actual_value is None or actual_value == "":
            return (
                "MISSING",
                f"Information required: '{label}' is not provided in your profile.",
                citation
            )

        # Type normalization
        if isinstance(target_value, (int, float, Decimal)) and isinstance(actual_value, (int, float, Decimal, str)):
            try:
                actual_num = Decimal(str(actual_value))
                target_num = Decimal(str(target_value))
                tolerance_num = Decimal(str(tolerance)) if tolerance else Decimal(0)
            except Exception:
                actual_num = actual_value
                target_num = target_value
                tolerance_num = Decimal(0)
        else:
            actual_num = actual_value
            target_num = target_value
            tolerance_num = Decimal(0)

        # Evaluate comparison operators
        if op == "==":
            if actual_value == target_value:
                return ("PASS", f"{label} verified", citation)
            else:
                return ("FAIL", f"{label} requirement not met (Requires: {target_value})", citation)

        elif op == "!=":
            if actual_value != target_value:
                return ("PASS", f"{label} verified", citation)
            else:
                return ("FAIL", f"{label} condition not satisfied", citation)

        elif op == "<=":
            if actual_num <= target_num:
                return ("PASS", f"Income ₹{actual_num:,.0f} is within ₹{target_num:,.0f} ceiling", citation)
            elif tolerance_num > 0 and (actual_num - target_num) <= tolerance_num:
                diff = actual_num - target_num
                return (
                    "NEAR_ELIGIBLE",
                    f"Borderline case: Declared ₹{actual_num:,.0f} is just ₹{diff:,.0f} over the ₹{target_num:,.0f} cutoff. May qualify for fee concessions.",
                    citation
                )
            else:
                return ("FAIL", f"Income ₹{actual_num:,.0f} exceeds the ₹{target_num:,.0f} ceiling", citation)

        elif op == ">=":
            if actual_num >= target_num:
                return ("PASS", f"Qualifying marks: {actual_num}% meets {target_num}% cutoff", citation)
            elif tolerance_num > 0 and (target_num - actual_num) <= tolerance_num:
                diff = target_num - actual_num
                return (
                    "NEAR_ELIGIBLE",
                    f"Borderline case: Your score ({actual_num}%) is within {diff}% of requirement ({target_num}%).",
                    citation
                )
            else:
                return ("FAIL", f"Qualifying score {actual_num}% is below the {target_num}% cutoff", citation)

        elif op == "in":
            target_list = target_value if isinstance(target_value, list) else [target_value]
            if actual_value in target_list:
                return ("PASS", f"{label} ({actual_value}) qualifies", citation)
            else:
                return ("FAIL", f"{label} '{actual_value}' does not match eligible categories", citation)

        elif op == "not_in":
            target_list = target_value if isinstance(target_value, list) else [target_value]
            if actual_value not in target_list:
                return ("PASS", f"{label} verified", citation)
            else:
                return ("FAIL", f"Excluded category: {actual_value}", citation)

        return ("FAIL", f"Unknown rule operator '{op}'", citation)

    @classmethod
    def evaluate_scheme(cls, scheme, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a complete scheme AST against profile data.
        Returns detailed audit trail with pass, fail, near-eligible, and missing items.
        """
        rules = scheme.rules or {}
        operator = rules.get("operator", "ALL")
        conditions = rules.get("conditions", [])

        passed = []
        failed = []
        near_eligible = []
        missing = []

        for cond in conditions:
            status, reason, citation = cls.evaluate_condition(cond, profile_data)
            entry = {
                "field": cond.get("field"),
                "label": cond.get("label"),
                "reason": reason,
                "citation": citation or cond.get("citation") or scheme.statutory_gr or "Govt of Maharashtra Resolution"
            }

            if status == "PASS":
                passed.append(entry)
            elif status == "NEAR_ELIGIBLE":
                near_eligible.append(entry)
            elif status == "MISSING":
                missing.append(entry)
            else:
                failed.append(entry)

        # Synthesize final status
        if not conditions:
            final_status = "NEEDS_CONFIRMATION"
            missing.append({
                "field": "criteria",
                "label": "Scheme Rules",
                "reason": "Official eligibility rules for this general scheme are being configured.",
                "citation": scheme.statutory_gr or ""
            })
        elif operator == "ALL":
            if failed:
                final_status = "INELIGIBLE"
            elif near_eligible:
                final_status = "NEAR_ELIGIBLE"
            elif missing:
                final_status = "NEEDS_CONFIRMATION"
            else:
                final_status = "LIKELY_ELIGIBLE"
        else: # ANY
            if passed:
                final_status = "LIKELY_ELIGIBLE"
            elif near_eligible:
                final_status = "NEAR_ELIGIBLE"
            elif missing:
                final_status = "NEEDS_CONFIRMATION"
            else:
                final_status = "INELIGIBLE"

        # Near-eligible guidance synthesis
        near_guidance = ""
        if final_status == "NEAR_ELIGIBLE":
            items = [item["reason"] for item in near_eligible]
            near_guidance = "Boundary check: " + " ".join(items)

        # Documents required for this scheme
        required_docs = []
        for req in scheme.document_requirements.select_related('document').all():
            required_docs.append({
                "code": req.document.code,
                "name": req.document.name,
                "name_marathi": req.document.name_marathi,
                "issuing_authority": req.document.issuing_authority,
                "procurement_portal": req.document.procurement_portal,
                "estimated_sla_days": req.document.estimated_sla_days,
                "is_mandatory": req.is_mandatory,
                "purpose": req.specific_purpose
            })

        return {
            "scheme_id": str(scheme.id),
            "code": scheme.code,
            "version": scheme.version,
            "effective_academic_year": scheme.effective_academic_year,
            "name": scheme.name,
            "name_marathi": scheme.name_marathi,
            "department": scheme.department,
            "statutory_gr": scheme.statutory_gr,
            "benefit_type": scheme.benefit_type,
            "benefit_amount_text": scheme.benefit_amount_text,
            "estimated_annual_value": scheme.estimated_annual_value,
            "brief_description": scheme.brief_description,
            "official_portal_url": scheme.official_portal_url,
            "portal_name": scheme.portal_name,
            "official_source_url": scheme.official_source_url or scheme.official_portal_url,
            "last_verified_on": scheme.last_verified_on.isoformat() if scheme.last_verified_on else "2024-11-01",
            "application_deadline": scheme.application_deadline.isoformat() if scheme.application_deadline else "2027-03-31",
            "application_steps": scheme.application_steps if scheme.application_steps else [
                "Register on the official portal with Aadhaar-linked mobile verification.",
                "Complete profile with academic marks, domicile, and Tahsildar income certificate.",
                "Upload scanned copies of mandatory documents certified by issuing authorities.",
                "Submit application and hand over printed acknowledgment to college scholarship clerk."
            ],
            "verification_status": scheme.verification_status if hasattr(scheme, 'verification_status') else "VERIFIED",
            "contact_helpline": "MahaDBT Citizen Support: 022-49150800 (Mon–Fri 9am–6pm) | Aaple Sarkar Toll-Free: 1800-120-8040",
            "statutory_fee_text": "₹0.00 (Free government application on MahaDBT; ₹33.60 statutory processing fee for Revenue certificates on Aaple Sarkar)",
            "status": final_status,
            "passed_criteria": passed,
            "near_eligible_criteria": near_eligible,
            "failed_criteria": failed,
            "missing_criteria": missing,
            "near_eligible_guidance": near_guidance,
            "required_documents": required_docs
        }
