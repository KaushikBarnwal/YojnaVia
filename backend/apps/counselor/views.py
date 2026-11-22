import uuid
from datetime import date, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed

from apps.eligibility.views import evaluate_profile_data, ApplicationPreflightService
from apps.schemes.models import Scheme, RequiredDocument
from apps.tracker.models import ApplicationRecord
from .models import (
    ServiceCenter,
    CounselorUser,
    CitizenCase,
    CitizenConsentRecord,
    CaseAccessAuditLog,
    CounselorCaseNote,
)
from .serializers import (
    ServiceCenterSerializer,
    CounselorUserSerializer,
    CitizenCaseListSerializer,
    CitizenCaseDetailSerializer,
    CounselorCaseNoteSerializer,
    CaseAccessAuditLogSerializer,
)
from .permissions import (
    authenticate_counselor,
    require_counselor_auth,
    verify_case_center_access,
    verify_active_consent,
    COUNSELOR_TOKENS,
)
from .services import CounselorService


class CounselorLoginView(APIView):
    """
    POST /api/v1/counselor/auth/login/
    Authenticates CSC Counselor or Supervisor. Supports credentials or 1-click demo login.
    """

    def post(self, request):
        CounselorService.seed_default_centers_and_counselors()

        demo_user = request.data.get('demo_user', '').strip()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        target_username = demo_user or username
        if not target_username:
            return Response(
                {"error": "username or demo_user is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CounselorUser.objects.select_related('center').get(username=target_username, is_active=True)
        except CounselorUser.DoesNotExist:
            return Response(
                {"error": f"Invalid credentials. Counselor account '{target_username}' not found."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Simple verification for prototype demo
        if not demo_user and password and user.password_hash != password:
            return Response(
                {"error": "Invalid password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = f"csc-{uuid.uuid4().hex[:16]}"
        COUNSELOR_TOKENS[token] = user.id

        return Response({
            "token": token,
            "user": CounselorUserSerializer(user).data,
            "message": f"Welcome, {user.name} ({user.get_role_display()})"
        })


class CounselorMeView(APIView):
    """GET /api/v1/counselor/auth/me/"""

    def get(self, request):
        CounselorService.seed_default_centers_and_counselors()
        user = require_counselor_auth(request)
        return Response({
            "user": CounselorUserSerializer(user).data
        })


class CounselorCaseListView(APIView):
    """
    GET /api/v1/counselor/cases/
    POST /api/v1/counselor/cases/
    Manages assisted cases for the authenticated counselor's center.
    """

    def get(self, request):
        CounselorService.seed_default_centers_and_counselors()
        user = require_counselor_auth(request)

        # Scope cases strictly to user's assigned center (Platform Admin sees all)
        if user.role == 'ADMIN':
            cases = CitizenCase.objects.select_related('center', 'assigned_counselor', 'consent').all()
        else:
            cases = CitizenCase.objects.filter(center=user.center).select_related('center', 'assigned_counselor', 'consent')

        # Filters
        status_filter = request.query_params.get('status')
        if status_filter:
            cases = cases.filter(case_status=status_filter.upper())

        priority_filter = request.query_params.get('priority')
        if priority_filter:
            cases = cases.filter(priority=priority_filter.upper())

        search_q = request.query_params.get('search', '').strip()
        if search_q:
            cases = cases.filter(citizen_name__icontains=search_q) | cases.filter(case_number__icontains=search_q)

        if str(request.query_params.get('assigned_only', '')).lower() in ('true', '1'):
            cases = cases.filter(assigned_counselor=user)

        if str(request.query_params.get('follow_up_due', '')).lower() in ('true', '1'):
            today = date.today()
            cases = cases.filter(follow_up_date__lte=today + timedelta(days=7)).exclude(case_status='CLOSED_HANDOVER')

        serializer = CitizenCaseListSerializer(cases[:100], many=True)
        return Response({
            "center": ServiceCenterSerializer(user.center).data,
            "total_cases": cases.count(),
            "cases": serializer.data
        })

    def post(self, request):
        CounselorService.seed_default_centers_and_counselors()
        user = require_counselor_auth(request)

        citizen_name = request.data.get('citizen_name', '').strip()
        if not citizen_name:
            return Response(
                {"error": "citizen_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        citizen_mobile = request.data.get('citizen_mobile', '').strip()
        target_category = request.data.get('target_scheme_category', 'Higher Education & Scholarships')
        priority = request.data.get('priority', 'MEDIUM')
        consent_method = request.data.get('consent_method', 'IN_PERSON_VERBAL')
        scope_description = request.data.get('scope_description', '')
        initial_notes = request.data.get('initial_notes', '')

        case = CounselorService.register_citizen_case(
            counselor=user,
            citizen_name=citizen_name,
            citizen_mobile=citizen_mobile,
            target_scheme_category=target_category,
            priority=priority,
            consent_method=consent_method,
            scope_description=scope_description,
            initial_notes=initial_notes
        )

        serializer = CitizenCaseDetailSerializer(case)
        return Response({
            "message": f"Case {case.case_number} registered successfully with active citizen consent.",
            "case": serializer.data
        }, status=status.HTTP_201_CREATED)


class CounselorCaseDetailView(APIView):
    """
    GET /api/v1/counselor/cases/<uuid:case_id>/
    PUT /api/v1/counselor/cases/<uuid:case_id>/
    """

    def get(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('center', 'assigned_counselor', 'consent', 'profile').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        # Cross-Center Protection
        verify_case_center_access(user, case, action="PROFILE_VIEWED")

        # Audit view
        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=user,
            action='PROFILE_VIEWED',
            details={"viewer": user.username}
        )

        serializer = CitizenCaseDetailSerializer(case)
        return Response({
            "case": serializer.data
        })

    def put(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        verify_case_center_access(user, case, action="CASE_UPDATED")

        # Allow updating status, priority, category, follow-up
        if 'priority' in request.data:
            case.priority = request.data['priority']
        if 'case_status' in request.data:
            case.case_status = request.data['case_status']
        if 'target_scheme_category' in request.data:
            case.target_scheme_category = request.data['target_scheme_category']
        if 'follow_up_date' in request.data:
            case.follow_up_date = request.data['follow_up_date'] or None
        if 'citizen_mobile' in request.data:
            case.citizen_mobile = request.data['citizen_mobile']

        case.save()
        return Response({
            "message": "Case metadata updated",
            "case": CitizenCaseDetailSerializer(case).data
        })


class CounselorUpdateProfileView(APIView):
    """
    POST /api/v1/counselor/cases/<uuid:case_id>/update_profile/
    Assisted intake profile confirmation with mandatory consent check.
    """

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('profile', 'center', 'consent').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        profile_data = request.data.get('profile', request.data)
        updated_profile = CounselorService.update_profile(case, user, profile_data)

        # Run deterministic eligibility engine on the confirmed profile
        eligibility = evaluate_profile_data({
            "age": updated_profile.age,
            "gender": updated_profile.gender,
            "state": updated_profile.state,
            "district": updated_profile.district,
            "caste_category": updated_profile.caste_category,
            "caste_name": updated_profile.caste_name,
            "annual_family_income": float(updated_profile.annual_family_income),
            "current_course_level": updated_profile.current_course_level,
            "course_name": updated_profile.course_name,
            "admission_quota": updated_profile.admission_quota,
            "previous_year_percentage": float(updated_profile.previous_year_percentage or 0),
            "accommodation_type": updated_profile.accommodation_type,
            "parent_is_farmer": updated_profile.parent_is_farmer,
            "parent_land_acres": float(updated_profile.parent_land_acres or 0),
            "has_aadhaar_seeded_bank": updated_profile.has_aadhaar_seeded_bank,
        })

        return Response({
            "message": "Citizen profile confirmed and synchronized with deterministic eligibility engine.",
            "case": CitizenCaseDetailSerializer(case).data,
            "eligibility": eligibility
        })


class CounselorCaseConsentWithdrawView(APIView):
    """
    POST /api/v1/counselor/cases/<uuid:case_id>/withdraw_consent/
    Immediately revokes citizen consent.
    """

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('consent', 'center').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'Citizen requested consent withdrawal at Kendra desk.')
        CounselorService.withdraw_consent(case, user, reason)

        return Response({
            "message": f"Consent for case {case.case_number} has been revoked. Profile access is now blocked.",
            "consent_status": "WITHDRAWN"
        })


class CounselorCaseNotesView(APIView):
    """
    GET, POST /api/v1/counselor/cases/<uuid:case_id>/notes/
    """

    def get(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        verify_case_center_access(user, case, action="NOTES_VIEWED")
        notes = case.notes.all()
        return Response({
            "case_number": case.case_number,
            "notes": CounselorCaseNoteSerializer(notes, many=True).data
        })

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        verify_case_center_access(user, case, action="NOTE_ADDED")

        content = request.data.get('content', '').strip()
        if not content:
            return Response({"error": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

        note_type = request.data.get('note_type', 'GENERAL')
        is_pinned = bool(request.data.get('is_pinned', False))

        note = CounselorCaseNote.objects.create(
            case=case,
            counselor=user,
            note_type=note_type,
            content=content,
            is_pinned=is_pinned
        )

        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=user,
            action='CASE_NOTE_ADDED',
            details={"note_type": note_type}
        )

        return Response({
            "message": "Note added successfully",
            "note": CounselorCaseNoteSerializer(note).data
        }, status=status.HTTP_201_CREATED)


class CounselorCaseEscalateView(APIView):
    """
    POST /api/v1/counselor/cases/<uuid:case_id>/escalate/
    Escalates case to Center Supervisor.
    """

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('center', 'consent').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response({"error": "reason is required for supervisor escalation"}, status=status.HTTP_400_BAD_REQUEST)

        CounselorService.escalate_case(case, user, reason)
        return Response({
            "message": f"Case {case.case_number} escalated to Center Supervisor.",
            "case_status": "ESCALATED_SUPERVISOR"
        })


class CounselorCaseCloseView(APIView):
    """
    POST /api/v1/counselor/cases/<uuid:case_id>/close/
    Closes case with handover summary.
    """

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('center').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        summary = request.data.get('summary', 'Assisted application readiness completed and document checklist handed over.')
        CounselorService.close_and_handover(case, user, summary)
        return Response({
            "message": f"Case {case.case_number} closed and handed over to citizen.",
            "case_status": "CLOSED_HANDOVER"
        })


class CounselorEvaluateEligibilityView(APIView):
    """
    POST /api/v1/counselor/cases/<uuid:case_id>/evaluate_eligibility/
    Reuses existing deterministic eligibility engine for the assisted citizen case.
    """

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('profile', 'center', 'consent').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        verify_case_center_access(user, case, action="ELIGIBILITY_EVALUATED")
        verify_active_consent(case)

        profile = case.profile
        eligibility = evaluate_profile_data({
            "age": profile.age,
            "gender": profile.gender,
            "state": profile.state,
            "district": profile.district,
            "caste_category": profile.caste_category,
            "caste_name": profile.caste_name,
            "annual_family_income": float(profile.annual_family_income),
            "current_course_level": profile.current_course_level,
            "course_name": profile.course_name,
            "admission_quota": profile.admission_quota,
            "previous_year_percentage": float(profile.previous_year_percentage or 0),
            "accommodation_type": profile.accommodation_type,
            "parent_is_farmer": profile.parent_is_farmer,
            "parent_land_acres": float(profile.parent_land_acres or 0),
            "has_aadhaar_seeded_bank": profile.has_aadhaar_seeded_bank,
        })

        if case.case_status == 'INTAKE_PENDING':
            case.case_status = 'ELIGIBILITY_DISCOVERED'
            case.save(update_fields=['case_status', 'updated_at'])

        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=user,
            action='ELIGIBILITY_EVALUATED',
            details={"matched_schemes": len(eligibility.get("results", []))}
        )

        return Response({
            "case_number": case.case_number,
            "citizen_name": case.citizen_name,
            "eligibility": eligibility
        })


class CounselorPreflightReviewView(APIView):
    """
    POST /api/v1/counselor/cases/<uuid:case_id>/preflight/
    Reuses existing 6-point pre-submission scrutiny audit for a scheme.
    """

    def post(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('profile', 'center', 'consent').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        verify_case_center_access(user, case, action="PREFLIGHT_RUN")
        verify_active_consent(case)

        scheme_code = request.data.get('scheme_code', 'MH_DTE_EBC_2024')
        checked_docs = request.data.get('checked_documents', [])
        custom_params = request.data.get('custom_audit_params', {})

        profile = case.profile
        profile_data = {
            "age": profile.age,
            "gender": profile.gender,
            "state": profile.state,
            "district": profile.district,
            "caste_category": profile.caste_category,
            "caste_name": profile.caste_name,
            "annual_family_income": float(profile.annual_family_income or 0),
            "current_course_level": profile.current_course_level,
            "course_name": profile.course_name,
            "admission_quota": profile.admission_quota,
            "previous_year_percentage": float(profile.previous_year_percentage or 0),
            "accommodation_type": profile.accommodation_type,
            "parent_is_farmer": profile.parent_is_farmer,
            "parent_land_acres": float(profile.parent_land_acres or 0),
            "has_aadhaar_seeded_bank": profile.has_aadhaar_seeded_bank,
        }

        audit_res = ApplicationPreflightService.run_preflight_audit(
            scheme_code=scheme_code,
            profile_data=profile_data,
            checked_doc_codes=checked_docs,
            custom_audit_params=custom_params
        )

        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=user,
            action='PREFLIGHT_RUN',
            details={"scheme_code": scheme_code, "score": audit_res.get("readiness_score_pct")}
        )

        return Response({
            "case_number": case.case_number,
            "preflight_audit": audit_res
        })


class CounselorDocumentChecklistView(APIView):
    """
    GET, POST /api/v1/counselor/cases/<uuid:case_id>/documents/
    Generates tailored document procurement checklist and updates verification marks.
    """

    def get(self, request, case_id):
        user = require_counselor_auth(request)
        try:
            case = CitizenCase.objects.select_related('profile', 'center', 'consent').get(id=case_id)
        except CitizenCase.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        verify_case_center_access(user, case, action="DOCUMENTS_CHECKED")
        verify_active_consent(case)

        # Generate checklist from required schemes
        req_docs = RequiredDocument.objects.select_related('scheme', 'document').all()
        checklist = []
        seen = set()
        for rd in req_docs:
            doc = rd.document
            if doc.code not in seen:
                seen.add(doc.code)
                checklist.append({
                    "code": doc.code,
                    "name": doc.name,
                    "issuing_authority": doc.issuing_authority,
                    "portal_name": doc.portal_name,
                    "estimated_sla_days": doc.estimated_sla_days or 15,
                    "is_mandatory": rd.is_mandatory,
                    "scheme_code": rd.scheme.code,
                    "scheme_name": rd.scheme.name,
                    "verified": False
                })

        return Response({
            "case_number": case.case_number,
            "citizen_name": case.citizen_name,
            "checklist": checklist
        })


class CenterAnalyticsView(APIView):
    """
    GET /api/v1/counselor/analytics/
    Aggregated Kendra-level performance statistics. Zero citizen PII.
    """

    def get(self, request):
        CounselorService.seed_default_centers_and_counselors()
        user = require_counselor_auth(request)

        analytics = CounselorService.get_center_analytics(user.center)
        return Response(analytics)
