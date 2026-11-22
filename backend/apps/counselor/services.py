import random
import uuid
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db.models import Count

from apps.profiles.models import StudentProfile
from .models import (
    ServiceCenter,
    CounselorUser,
    CitizenCase,
    CitizenConsentRecord,
    CaseAccessAuditLog,
    CounselorCaseNote,
)
from .permissions import verify_case_center_access, verify_active_consent


class CounselorService:

    @classmethod
    def seed_default_centers_and_counselors(cls) -> None:
        """Seeds authentic Maharashtra CSC / Aaple Sarkar centers and demo staff."""
        c1, _ = ServiceCenter.objects.get_or_create(
            code="CSC_SANGLI_412",
            defaults={
                "name": "Aaple Sarkar Seva Kendra #412 (Sangli Central)",
                "vle_id": "MH-VLE-98214",
                "center_type": "AAPLE_SARKAR_KENDRA",
                "district": "Sangli",
                "taluka": "Miraj",
                "pincode": "416416",
                "contact_phone": "+919822011223",
                "is_active": True,
            }
        )

        c2, _ = ServiceCenter.objects.get_or_create(
            code="KENDRA_NASHIK_108",
            defaults={
                "name": "Aaple Sarkar Seva Kendra #108 (Nashik Dindori)",
                "vle_id": "MH-VLE-88431",
                "center_type": "AAPLE_SARKAR_KENDRA",
                "district": "Nashik",
                "taluka": "Dindori",
                "pincode": "422202",
                "contact_phone": "+919823099887",
                "is_active": True,
            }
        )

        CounselorUser.objects.get_or_create(
            username="counselor_sangli",
            defaults={
                "name": "Suresh Patil (Operator)",
                "password_hash": "counselor123",
                "role": "COUNSELOR",
                "center": c1,
                "phone": "+919822100001",
                "email": "suresh.patil@sangli.csc.in",
                "is_active": True,
            }
        )

        CounselorUser.objects.get_or_create(
            username="supervisor_sangli",
            defaults={
                "name": "Anjali Deshmukh (Lead VLE / Supervisor)",
                "password_hash": "supervisor123",
                "role": "SUPERVISOR",
                "center": c1,
                "phone": "+919822100002",
                "email": "anjali.vle@sangli.csc.in",
                "is_active": True,
            }
        )

        CounselorUser.objects.get_or_create(
            username="counselor_nashik",
            defaults={
                "name": "Rahul Shinde (Operator)",
                "password_hash": "counselor123",
                "role": "COUNSELOR",
                "center": c2,
                "phone": "+919823100001",
                "email": "rahul.shinde@nashik.csc.in",
                "is_active": True,
            }
        )

    @classmethod
    def register_citizen_case(
        cls,
        counselor: CounselorUser,
        citizen_name: str,
        citizen_mobile: str = "",
        target_scheme_category: str = "Higher Education & Scholarships",
        priority: str = "MEDIUM",
        consent_method: str = "IN_PERSON_VERBAL",
        scope_description: str = "",
        initial_notes: str = "",
        follow_up_days: int = 7
    ) -> CitizenCase:
        """
        Creates a new citizen case with mandatory consent recording and audit trail.
        Allocates an isolated session token and StudentProfile for the citizen.
        """
        current_year = date.today().year
        case_seq = f"{random.randint(1000, 9999)}"
        case_number = f"CS-{current_year}-{case_seq}"

        # 1. Allocate isolated profile
        session_token = f"csc-assisted-{uuid.uuid4().hex[:14]}"
        profile = StudentProfile.objects.create(
            session_token=session_token,
            name=citizen_name,
            district=counselor.center.district,
            state="Maharashtra",
            is_maharashtra_domicile=True
        )

        # 2. Create CitizenCase bound to the counselor's center
        follow_up = date.today() + timedelta(days=follow_up_days) if follow_up_days else None
        case = CitizenCase.objects.create(
            case_number=case_number,
            center=counselor.center,
            assigned_counselor=counselor,
            profile=profile,
            citizen_name=citizen_name,
            citizen_mobile=citizen_mobile,
            case_status='INTAKE_PENDING',
            priority=priority,
            target_scheme_category=target_scheme_category,
            follow_up_date=follow_up
        )

        # 3. Record Mandatory Citizen Consent
        default_scope = (
            f"Citizen {citizen_name} explicitly authorizes Counselor {counselor.name} at {counselor.center.name} "
            f"to assist with demographic profile intake, civil document verification, scheme matching, "
            f"and portal tracking. Citizen retains the right to withdraw consent at any time."
        )
        CitizenConsentRecord.objects.create(
            case=case,
            consent_status='ACTIVE',
            consent_method=consent_method,
            scope_description=scope_description.strip() or default_scope,
            attesting_counselor=counselor
        )

        # 4. Audit Log
        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=counselor,
            action='CASE_CREATED',
            details={"citizen_name": citizen_name, "center": counselor.center.code, "consent_method": consent_method}
        )

        # 5. Initial Note if provided
        if initial_notes.strip():
            CounselorCaseNote.objects.create(
                case=case,
                counselor=counselor,
                note_type='GENERAL',
                content=initial_notes.strip()
            )

        return case

    @classmethod
    def withdraw_consent(cls, case: CitizenCase, counselor: CounselorUser, reason: str) -> None:
        """Immediately withdraws citizen consent and logs the revocation."""
        verify_case_center_access(counselor, case, action="CONSENT_WITHDRAWN")
        if hasattr(case, 'consent'):
            case.consent.withdraw(reason)
        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=counselor,
            action='CONSENT_WITHDRAWN',
            details={"reason": reason, "counselor": counselor.username}
        )

    @classmethod
    def update_profile(cls, case: CitizenCase, counselor: CounselorUser, profile_data: Dict[str, Any]) -> StudentProfile:
        """Updates citizen profile attributes with consent & audit verification."""
        verify_case_center_access(counselor, case, action="PROFILE_UPDATED")
        verify_active_consent(case)

        profile = case.profile
        # Prevent any Aadhaar or sensitive identifier collection
        allowed_fields = [
            'age', 'gender', 'state', 'district', 'caste_category', 'caste_name',
            'annual_family_income', 'has_ration_card', 'ration_card_type',
            'current_course_level', 'course_name', 'admission_quota',
            'previous_year_percentage', 'accommodation_type', 'parent_is_farmer',
            'parent_land_acres', 'has_aadhaar_seeded_bank'
        ]

        updated_keys = []
        for key in allowed_fields:
            if key in profile_data:
                setattr(profile, key, profile_data[key])
                updated_keys.append(key)

        profile.is_confirmed = True
        profile.save()

        # Update case status if intake was pending
        if case.case_status == 'INTAKE_PENDING':
            case.case_status = 'ELIGIBILITY_DISCOVERED'
            case.save(update_fields=['case_status', 'updated_at'])

        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=counselor,
            action='PROFILE_UPDATED',
            details={"fields_updated": updated_keys}
        )
        return profile

    @classmethod
    def escalate_case(cls, case: CitizenCase, counselor: CounselorUser, reason: str) -> None:
        """Escalates complex case to Center Supervisor."""
        verify_case_center_access(counselor, case, action="CASE_ESCALATED")
        verify_active_consent(case)

        case.escalated_to_supervisor = True
        case.case_status = 'ESCALATED_SUPERVISOR'
        case.escalation_reason = reason
        case.save(update_fields=['escalated_to_supervisor', 'case_status', 'escalation_reason', 'updated_at'])

        CounselorCaseNote.objects.create(
            case=case,
            counselor=counselor,
            note_type='SUPERVISOR_REMARK',
            content=f"ESCALATION: {reason}",
            is_pinned=True
        )

        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=counselor,
            action='CASE_ESCALATED',
            details={"reason": reason, "escalated_by": counselor.username}
        )

    @classmethod
    def close_and_handover(cls, case: CitizenCase, counselor: CounselorUser, summary: str) -> None:
        """Closes case and records handover of documents / guidance to citizen."""
        verify_case_center_access(counselor, case, action="CASE_CLOSED")

        case.case_status = 'CLOSED_HANDOVER'
        case.closed_at = timezone.now()
        case.closure_summary = summary
        case.save(update_fields=['case_status', 'closed_at', 'closure_summary', 'updated_at'])

        CounselorCaseNote.objects.create(
            case=case,
            counselor=counselor,
            note_type='HANDOVER_SUMMARY',
            content=f"CASE CLOSED & HANDED OVER: {summary}",
            is_pinned=True
        )

        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=counselor,
            action='CASE_CLOSED',
            details={"summary": summary}
        )

    @classmethod
    def get_center_analytics(cls, center: ServiceCenter) -> Dict[str, Any]:
        """
        Computes aggregate center metrics without exposing any citizen PII.
        """
        cases = CitizenCase.objects.filter(center=center)
        total_cases = cases.count()

        status_counts = {}
        for row in cases.values('case_status').annotate(total=Count('id')):
            status_counts[row['case_status']] = row['total']

        priority_counts = {}
        for row in cases.values('priority').annotate(total=Count('id')):
            priority_counts[row['priority']] = row['total']

        today = date.today()
        pending_followups = cases.filter(
            follow_up_date__lte=today + timedelta(days=7),
            follow_up_date__gte=today - timedelta(days=30)
        ).exclude(case_status='CLOSED_HANDOVER').count()

        # Top requested scheme categories
        categories = {}
        for row in cases.values('target_scheme_category').annotate(total=Count('id')).order_by('-total')[:5]:
            categories[row['target_scheme_category']] = row['total']

        return {
            "center": {
                "name": center.name,
                "code": center.code,
                "vle_id": center.vle_id,
                "district": center.district,
                "taluka": center.taluka,
            },
            "metrics": {
                "total_cases_handled": total_cases,
                "cases_awaiting_documents": status_counts.get('DOCUMENTS_PENDING', 0),
                "cases_ready_for_application": status_counts.get('READY_FOR_APPLICATION', 0),
                "cases_applied_tracking": status_counts.get('APPLIED_TRACKING', 0),
                "cases_escalated": status_counts.get('ESCALATED_SUPERVISOR', 0),
                "cases_closed": status_counts.get('CLOSED_HANDOVER', 0),
                "pending_followups_this_week": pending_followups,
                "status_distribution": status_counts,
                "priority_distribution": priority_counts,
                "top_scheme_categories": categories,
            }
        }
