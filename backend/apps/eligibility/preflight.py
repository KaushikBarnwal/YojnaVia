"""
Application Preflight Audit Engine.
Performs deterministic, 6-point pre-submission verification to catch scrutiny errors,
expired certificates, name/record discrepancies, and quota ineligibilities before citizens
submit applications on official government portals (MahaDBT / Aaple Sarkar).
"""

from typing import Dict, Any, List
from decimal import Decimal
from apps.schemes.models import Scheme
from apps.profiles.models import StudentProfile


class ApplicationPreflightService:
    @classmethod
    def run_preflight_audit(
        cls,
        scheme_code: str,
        profile_data: Dict[str, Any],
        checked_doc_codes: List[str] = None,
        custom_audit_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive deterministic 6-point preflight audit for a scheme.
        Returns:
        - readiness_score_pct: 0 to 100
        - status: "READY" | "WARNINGS" | "BLOCKED"
        - blockers: list of fatal issues that will trigger scrutiny rejection
        - warnings: list of potential scrutiny queries or delay risks
        - cleared_checks: list of verified valid items
        - action_plan: immediate steps to reach 100% readiness
        """
        try:
            scheme = Scheme.objects.prefetch_related('document_requirements__document').get(code=scheme_code)
        except Scheme.DoesNotExist:
            return {
                "scheme_code": scheme_code,
                "readiness_score_pct": 0,
                "status": "BLOCKED",
                "blockers": [{"title": "Scheme Not Found", "description": f"Scheme {scheme_code} is not active in the database."}],
                "warnings": [],
                "cleared_checks": [],
                "action_plan": []
            }

        checked_docs = set(checked_doc_codes or [])
        custom = custom_audit_params or {}

        blockers = []
        warnings = []
        cleared_checks = []

        # =========================================================================
        # CHECK 1: Mandatory Document Completeness
        # =========================================================================
        mandatory_reqs = scheme.document_requirements.filter(is_mandatory=True).select_related('document')
        missing_mandatory = []
        for req in mandatory_reqs:
            doc = req.document
            if doc.code not in checked_docs:
                missing_mandatory.append({
                    "code": doc.code,
                    "name": doc.name,
                    "issuing_authority": doc.issuing_authority,
                    "sla_days": doc.estimated_sla_days,
                    "portal": doc.procurement_portal
                })

        if missing_mandatory:
            doc_names = ", ".join([d["name"] for d in missing_mandatory[:2]])
            if len(missing_mandatory) > 2:
                doc_names += f" and {len(missing_mandatory) - 2} other(s)"
            blockers.append({
                "code": "MISSING_MANDATORY_DOCUMENTS",
                "title": f"{len(missing_mandatory)} Mandatory Certificate(s) Not Ready",
                "description": f"MahaDBT scrutiny clerks will immediately reject applications missing: {doc_names}.",
                "fix_route": "Obtain certificates via Aaple Sarkar portal or mark as ready in your document checklist.",
                "missing_documents": missing_mandatory
            })
        else:
            cleared_checks.append({
                "title": "All Mandatory Certificates Ready",
                "description": f"All {mandatory_reqs.count()} mandatory scheme documents are accounted for."
            })

        # =========================================================================
        # CHECK 2: Certificate Validity & Financial Year Check
        # =========================================================================
        income_fy = custom.get("income_certificate_fy") or "2023-2024"
        current_req_fy = "2023-2024"  # For AY 2024-2025

        if income_fy != current_req_fy:
            blockers.append({
                "code": "EXPIRED_INCOME_CERTIFICATE_FY",
                "title": f"Income Certificate Financial Year Mismatch (FY {income_fy})",
                "description": f"MahaDBT AY 2024-25 mandatorily requires an Income Certificate issued for FY {current_req_fy}. A certificate for FY {income_fy} will be rejected during scrutiny.",
                "fix_route": "Apply for an updated Tahsildar Income Certificate for FY 2023-24 on Aaple Sarkar (15-day SLA)."
            })
        else:
            cleared_checks.append({
                "title": "Income Certificate Financial Year Valid",
                "description": f"Income certificate corresponds to official requirement FY {current_req_fy}."
            })

        # Caste Validity requirement for professional degree courses (Engineering, Pharmacy, MBA)
        course_level = profile_data.get("current_course_level", "PROFESSIONAL_DEGREE")
        caste_cat = profile_data.get("caste_category", "OPEN")
        has_caste_validity = custom.get("has_caste_validity", True if caste_cat in ["OPEN", "EWS"] else False)

        if caste_cat in ["OBC", "SC", "ST", "VJNT", "SBC"] and course_level == "PROFESSIONAL_DEGREE":
            if not has_caste_validity:
                blockers.append({
                    "code": "CASTE_VALIDITY_CERTIFICATE_REQUIRED",
                    "title": "Caste Validity Certificate Missing for Professional Degree",
                    "description": "Sub-Divisional Officer (SDO) Caste Certificate alone is insufficient for professional degree scholarships. Government Resolutions strictly mandate a Caste Validity Certificate issued by the Divisional Caste Scrutiny Committee.",
                    "fix_route": "Submit an application to the District Caste Scrutiny Committee or attach the official Application Acknowledgment Receipt with undertaking."
                })
            else:
                cleared_checks.append({
                    "title": "Caste Validity Certificate Verified",
                    "description": "Verified Caste Validity Certificate from District Scrutiny Committee."
                })

        # Non-Creamy Layer (NCL) for OBC / VJNT / SBC
        has_valid_ncl = custom.get("has_valid_ncl", True)
        if caste_cat in ["OBC", "VJNT", "SBC"]:
            if not has_valid_ncl:
                blockers.append({
                    "code": "NCL_CERTIFICATE_EXPIRED",
                    "title": "Non-Creamy Layer (NCL) Certificate Expired",
                    "description": "OBC/VJNT/SBC post-matric concessions require an NCL certificate valid up to March 31, 2025.",
                    "fix_route": "Apply for NCL renewal at the Taluka Tahsildar office via Aaple Sarkar."
                })
            else:
                cleared_checks.append({
                    "title": "Non-Creamy Layer Certificate Valid",
                    "description": "NCL certificate covers the current statutory academic term."
                })

        # =========================================================================
        # CHECK 3: Admission Mode (CAP Round vs Management Quota)
        # =========================================================================
        admission_quota = profile_data.get("admission_quota", "CAP_ROUND")
        if scheme.code in ["MH_DTE_EBC_2024", "MH_OBC_POSTMATRIC_2024"]:
            if admission_quota == "INSTITUTE_QUOTA":
                blockers.append({
                    "code": "INELIGIBLE_ADMISSION_QUOTA",
                    "title": "Management / Institutional Quota Ineligible for EBC / Freeship",
                    "description": "Under Maharashtra GR TEM-2018/CR-363, tuition fee waivers and EBC concessions are strictly limited to candidates admitted through the Centralized Admission Process (CAP Round) merit list. Management quota candidates cannot claim this benefit.",
                    "fix_route": "Verify your admission receipt. If admitted through CAP Direct Second Year or CAP mop-up, update your admission mode to CAP_ROUND."
                })
            else:
                cleared_checks.append({
                    "title": "Centralized Admission Process (CAP) Quota Confirmed",
                    "description": "Candidate was admitted through official government CAP merit round."
                })

        # =========================================================================
        # CHECK 4: Identity & Demographic Consistency (Name Discrepancies)
        # =========================================================================
        name_mismatch = custom.get("name_dob_discrepancy", False)
        student_name = profile_data.get("name", "Student")
        if name_mismatch:
            warnings.append({
                "code": "NAME_INITIAL_DISCREPANCY",
                "title": "Name / Initial Discrepancy Across Marksheet and Aadhaar",
                "description": f"A discrepancy was detected between candidate's educational marksheet and civil certificates for '{student_name}'. Minor spelling differences or expanded middle names often trigger scrutiny clerk inquiries.",
                "fix_route": "Upload a ₹100 Notarized Self-Affidavit confirming both name variants refer to the same individual."
            })
        else:
            cleared_checks.append({
                "title": "Name & Date of Birth Consistent",
                "description": "No discrepancies flagged between entered educational and civil records."
            })

        # =========================================================================
        # CHECK 5: Aadhaar DBT Bank Seeding & NPCI Mapping
        # =========================================================================
        has_seeded_bank = profile_data.get("has_aadhaar_seeded_bank", True)
        if not has_seeded_bank:
            blockers.append({
                "code": "BANK_ACCOUNT_NOT_DBT_SEEDED",
                "title": "Bank Account Not Seeded with Aadhaar (NPCI Inactive)",
                "description": "All government scholarships in Maharashtra are disbursed strictly via Aadhaar Payment Bridge (APB). Unseeded bank accounts result in transaction rejection during treasury clearance.",
                "fix_route": "Visit your nationalized bank branch immediately and submit the 'Aadhaar DBT Seeding & Mandate Form'. Verify status on UIDAI portal."
            })
        else:
            cleared_checks.append({
                "title": "Aadhaar-Seeded Bank Account Active",
                "description": "Direct Benefit Transfer (DBT) payment bridge confirmed ready."
            })

        # =========================================================================
        # CHECK 6: Scheme-Specific Boundary Rules (Hostel Distance & Living)
        # =========================================================================
        accommodation = profile_data.get("accommodation_type", "PRIVATE_RENTAL_PG")
        if scheme.code in ["MH_PANJABRAO_HOSTEL_2024", "MH_SWADHAR_SC_2024"]:
            if accommodation == "DAY_SCHOLAR":
                blockers.append({
                    "code": "DAY_SCHOLAR_INELIGIBLE_FOR_HOSTEL_ALLOWANCE",
                    "title": "Day Scholar Not Eligible for Hostel Allowance",
                    "description": "Dr. Panjabrao Deshmukh and Swadhar allowances are exclusively for students residing in hostels or non-relative rented rooms outside their home municipal limits. Day scholars living with parents cannot claim this benefit.",
                    "fix_route": "If you reside in a private PG or hostel, update your accommodation profile and prepare the hostel agreement / warden certificate."
                })
            else:
                cleared_checks.append({
                    "title": "Hostel / Rented Residency Qualified",
                    "description": "Residing in private PG/hostel outside parent home limits."
                })

        # =========================================================================
        # Compute Readiness Score & Action Plan
        # =========================================================================
        total_checks = len(blockers) + len(warnings) + len(cleared_checks)
        if total_checks == 0:
            readiness_pct = 100
        else:
            # Blockers count -20, warnings -10
            penalty = (len(blockers) * 25) + (len(warnings) * 10)
            readiness_pct = max(10, 100 - penalty)

        if blockers:
            overall_status = "BLOCKED"
        elif warnings:
            overall_status = "WARNINGS"
        else:
            overall_status = "READY"

        action_plan = []
        for b in blockers:
            action_plan.append({"priority": "CRITICAL", "action": b["fix_route"], "title": b["title"]})
        for w in warnings:
            action_plan.append({"priority": "RECOMMENDED", "action": w["fix_route"], "title": w["title"]})

        return {
            "scheme_code": scheme.code,
            "scheme_name": scheme.name,
            "readiness_score_pct": readiness_pct,
            "status": overall_status,
            "blockers_count": len(blockers),
            "warnings_count": len(warnings),
            "cleared_count": len(cleared_checks),
            "blockers": blockers,
            "warnings": warnings,
            "cleared_checks": cleared_checks,
            "action_plan": action_plan,
            "statutory_reassurance": (
                "This deterministic preflight audit evaluates your preparation against historical scrutiny rejection criteria under Maharashtra Government Resolutions. "
                "Resolving all blockers minimizes the risk of scrutiny queries on MahaDBT. Final sanction authority rests exclusively with the department."
            )
        }
