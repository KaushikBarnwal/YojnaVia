"""
Entitlement Lifecycle Intelligence Engine.
Tracks the complete student benefit journey across 6 unified stages:
Discover -> Prepare -> Apply -> Follow up -> Decision -> Renew
Separates user-reported milestones from official government department status,
calculates renewal dates, and guides students through reapplication windows.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from apps.schemes.models import Scheme
from .models import ApplicationRecord

LIFECYCLE_STAGES = [
    {
        "id": "DISCOVER",
        "order": 1,
        "name": "Discover & Validate",
        "tagline": "Statutory rule matching & stacking check",
        "description": "Identify matching Maharashtra state and central schemes based on course, social category, and household income.",
        "icon": "Search",
        "typical_duration": "1-2 days",
        "milestones": [
            {"code": "INTAKE_DONE", "label": "Profile attributes captured via conversational intake", "is_mandatory": True},
            {"code": "RULES_EVALUATED", "label": "Deterministic rules matched against Government Resolutions", "is_mandatory": True},
            {"code": "STACKING_CHECKED", "label": "Compatibility checked: No prohibited dual tuition claims", "is_mandatory": True}
        ]
    },
    {
        "id": "PREPARE",
        "order": 2,
        "name": "Prepare Documents",
        "tagline": "Civil certificate procurement under RTS Act",
        "description": "Procure digital barcode certificates from Tahsildar/SDO via Aaple Sarkar portal within statutory SLA.",
        "icon": "FileText",
        "typical_duration": "15-21 days",
        "milestones": [
            {"code": "INCOME_CERT", "label": "Tahsildar Income Certificate for preceding FY (15-day RTS SLA)", "is_mandatory": True},
            {"code": "DOMICILE_CERT", "label": "Maharashtra State Domicile / Residence Certificate", "is_mandatory": True},
            {"code": "CASTE_VALIDITY", "label": "District Scrutiny Committee Caste Validity (for professional degrees)", "is_mandatory": False},
            {"code": "NCL_CERT", "label": "Non-Creamy Layer Certificate with valid March 31 expiry date (OBC/VJNT/SBC)", "is_mandatory": False},
            {"code": "HOSTEL_ANNEXURE", "label": "Counter-Signed Annexure-A Hostel Certificate (if claiming hostel allowance)", "is_mandatory": False}
        ]
    },
    {
        "id": "APPLY",
        "order": 3,
        "name": "Apply on Portal",
        "tagline": "MahaDBT registration & preflight verification",
        "description": "Execute Preflight Audit to catch scrutiny blockers, then register and upload documents on MahaDBT.",
        "icon": "Send",
        "typical_duration": "1-3 days",
        "milestones": [
            {"code": "PREFLIGHT_AUDIT", "label": "Run Application Preflight Audit to clear quota & FY blockers", "is_mandatory": True},
            {"code": "MAHADBT_REGISTRATION", "label": "Aadhaar OTP portal registration on mahadbt.maharashtra.gov.in", "is_mandatory": True},
            {"code": "FORM_SUBMISSION", "label": "Online form submission & generation of Application Reference Number", "is_mandatory": True}
        ]
    },
    {
        "id": "FOLLOW_UP",
        "order": 4,
        "name": "Follow-Up & Physical Scrutiny",
        "tagline": "College clerk submission & bank DBT seeding",
        "description": "Hand over physical self-attested documents to your college scholarship clerk and verify NPCI bank mapping.",
        "icon": "Users",
        "typical_duration": "7-14 days",
        "milestones": [
            {"code": "HARDCOPY_SUBMITTED", "label": "Printed application form & attested copies handed to College Clerk", "is_mandatory": True},
            {"code": "CLERK_RECEIPT", "label": "Obtain stamped submission acknowledgment from college scholarship counter", "is_mandatory": True},
            {"code": "NPCI_DBT_VERIFIED", "label": "Aadhaar-bank account active seeding confirmed on NPCI mapper", "is_mandatory": True}
        ]
    },
    {
        "id": "DECISION",
        "order": 5,
        "name": "Decision & Scrutiny Query",
        "tagline": "Sanction order or 15-day rectification window",
        "description": "Monitor college clerk and departmental approval; resolve scrutiny remarks within the 15-day window.",
        "icon": "Clock",
        "typical_duration": "30-60 days",
        "milestones": [
            {"code": "CLERK_SCRUTINY_PASS", "label": "College scrutiny desk approval verified on MahaDBT portal", "is_mandatory": True},
            {"code": "DEPT_SANCTION", "label": "Divisional Assistant Commissioner sanction order generated", "is_mandatory": True},
            {"code": "SCRUTINY_RECTIFIED", "label": "If queries occur: Re-upload within the active 15-day scrutiny window", "is_mandatory": False}
        ]
    },
    {
        "id": "RENEW",
        "order": 6,
        "name": "Annual Academic Renewal",
        "tagline": "Continuation application for next academic year",
        "description": "Maintain entitlement year-on-year without starting a fresh registration from scratch.",
        "icon": "RotateCcw",
        "typical_duration": "Annual cycle (July–August)",
        "milestones": [
            {"code": "PASSING_MARKSHEET", "label": "Pass annual degree/diploma examinations with required percentage", "is_mandatory": True},
            {"code": "ANNUAL_INCOME_RENEW", "label": "Re-certify Tahsildar Income Certificate before March 31 expiry", "is_mandatory": True},
            {"code": "RENEWAL_SUBMISSION", "label": "Submit 'Renewal Application' on MahaDBT for Academic Year continuation", "is_mandatory": True}
        ]
    }
]


class EntitlementLifecycleService:
    @classmethod
    def get_lifecycle_stages(cls) -> List[Dict[str, Any]]:
        """Returns standard 6-stage lifecycle blueprint."""
        return LIFECYCLE_STAGES

    @classmethod
    def get_application_lifecycle_roadmap(
        cls,
        app_record: ApplicationRecord
    ) -> Dict[str, Any]:
        """
        Builds complete lifecycle intelligence roadmap for a tracked scheme application.
        Calculates renewal dates, reapplication windows, and stage progress.
        """
        scheme = app_record.scheme
        status = app_record.status
        stage_code = app_record.stage

        # Determine current stage index (1 to 6)
        stage_map = {
            "DISCOVERED": 1,
            "DOCUMENTS_PREPARATION": 2,
            "ONLINE_REGISTRATION": 3,
            "COLLEGE_SCRUTINY": 4,
            "DEPT_APPROVAL": 5,
            "DISBURSED": 6
        }
        current_stage_idx = stage_map.get(stage_code, 1)
        if status == "APPROVED":
            current_stage_idx = 6  # Ready for next cycle renewal

        # Calculate renewal date and reapplication window
        today = date.today()
        current_year = today.year
        # MahaDBT renewal cycle typically starts July 1st of the next academic year
        next_renewal_date = date(current_year if today.month < 7 else current_year + 1, 7, 1)
        income_cert_expiry = date(current_year if today.month <= 3 else current_year + 1, 3, 31)

        # Scrutiny resubmission window
        resubmission_window_active = status in ("REJECTED", "UNDER_REVIEW")
        resubmission_deadline_days = 15 if resubmission_window_active else None

        # Build enriched stages with active / completed flags
        enriched_stages = []
        for stg in LIFECYCLE_STAGES:
            stg_order = stg["order"]
            is_completed = stg_order < current_stage_idx
            is_current = stg_order == current_stage_idx
            stg_state = "COMPLETED" if is_completed else ("CURRENT" if is_current else "UPCOMING")

            enriched_stages.append({
                **stg,
                "state": stg_state,
                "is_current": is_current,
                "is_completed": is_completed
            })

        return {
            "application_id": str(app_record.id),
            "scheme_code": scheme.code,
            "scheme_name": scheme.name,
            "portal_name": scheme.portal_name,
            "official_portal_url": scheme.official_portal_url,
            "application_reference_number": app_record.application_reference_number or "Not yet generated",
            "applied_date": app_record.applied_date.isoformat() if hasattr(app_record.applied_date, 'isoformat') else (str(app_record.applied_date) if app_record.applied_date else None),
            "current_status": status,
            "current_stage": stage_code,
            "current_stage_order": current_stage_idx,
            "total_stages": 6,
            "progress_pct": int((current_stage_idx / 6) * 100),
            "is_user_reported": True,
            "official_vs_user_reported_notice": (
                "Official Portal vs User-Reported Status: All milestones and stage selections shown here are self-reported "
                "by the student for personal compliance planning. YojnaVia does not claim direct integration with internal "
                "government treasury databases. Official sanction letters are issued exclusively via mahadbt.maharashtra.gov.in."
            ),
            "lifecycle_milestones": enriched_stages,
            "next_immediate_action": app_record.next_immediate_action,
            "renewal_intelligence": {
                "renewal_frequency": "Annual (Academic Year Basis)",
                "next_academic_renewal_window_opens": next_renewal_date.strftime("%d %B %Y"),
                "income_certificate_renewal_deadline": income_cert_expiry.strftime("%d %B %Y"),
                "renewal_notes": "Under Maharashtra Government rules, students who pass their qualifying annual examination remain eligible for next-year renewal without fresh registration."
            },
            "reapplication_intelligence": {
                "is_scrutiny_window_active": resubmission_window_active,
                "scrutiny_window_days": resubmission_deadline_days,
                "next_fresh_admission_cycle": "Academic Year 2025-26 (Opens July 2025)",
                "appeal_route": "Maharashtra Right to Public Services Act (RTS 2015) - within 30 days of departmental rejection order"
            }
        }
