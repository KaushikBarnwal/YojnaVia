from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme
from .models import ApplicationRecord
from .serializers import ApplicationRecordSerializer
from .rejection_recovery import RejectionRecoveryService

# Next action mappings according to stage / status
STATUS_NEXT_ACTIONS = {
    'NOT_STARTED': "Review required certificates and prepare application checklist.",
    'DOCUMENTS_PENDING': "Procure pending civil documents (Tahsildar Income / Domicile / Caste Validity) via Aaple Sarkar.",
    'DOCUMENTS_READY': "Register on the official portal (MahaDBT) with Aadhaar-linked OTP verification.",
    'APPLIED': "Submit printed acknowledgment copy along with attested document copies to College Scholarship Clerk.",
    'UNDER_REVIEW': "Track scrutiny status at College Clerk and Divisional Assistant Commissioner levels.",
    'APPROVED': "Sanction order issued. Ensure bank account is active and Aadhaar-seeded for Direct Benefit Transfer.",
    'REJECTED': "Review department scrutiny rejection remarks on MahaDBT portal and address document grievances."
}

STAGE_TO_STATUS = {
    'DISCOVERED': 'NOT_STARTED',
    'DOCUMENTS_PREPARATION': 'DOCUMENTS_PENDING',
    'ONLINE_REGISTRATION': 'APPLIED',
    'COLLEGE_SCRUTINY': 'UNDER_REVIEW',
    'DEPT_APPROVAL': 'UNDER_REVIEW',
    'DISBURSED': 'APPROVED',
}

STATUS_TO_STAGE = {
    'NOT_STARTED': 'DISCOVERED',
    'DOCUMENTS_PENDING': 'DOCUMENTS_PREPARATION',
    'DOCUMENTS_READY': 'DOCUMENTS_PREPARATION',
    'APPLIED': 'ONLINE_REGISTRATION',
    'UNDER_REVIEW': 'COLLEGE_SCRUTINY',
    'APPROVED': 'DISBURSED',
    'REJECTED': 'DEPT_APPROVAL',
}

class TrackerView(APIView):
    def get(self, request):
        session_token = request.query_params.get('session_token')
        if not session_token:
            return Response({"error": "session_token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = StudentProfile.objects.get(session_token=session_token)
            records = ApplicationRecord.objects.filter(profile=profile).select_related('scheme')
            serializer = ApplicationRecordSerializer(records, many=True)
            return Response({"applications": serializer.data})
        except StudentProfile.DoesNotExist:
            return Response({"applications": []})

    def post(self, request):
        session_token = request.data.get('session_token')
        scheme_code = request.data.get('scheme_code')
        req_status = request.data.get('status')
        stage = request.data.get('stage')
        completed_documents = request.data.get('completed_documents', [])
        ref_no = request.data.get('application_reference_number', '')
        applied_date = request.data.get('applied_date') or None
        submission_mode = request.data.get('submission_mode', 'Online Portal')
        notes = request.data.get('notes', '')

        if not session_token or not scheme_code:
            return Response({"error": "session_token and scheme_code are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile, _ = StudentProfile.objects.get_or_create(session_token=session_token, defaults={"name": "Student"})
            scheme = Scheme.objects.get(code=scheme_code)

            # Harmonize status and stage
            if req_status:
                canonical_status = req_status
                canonical_stage = STATUS_TO_STAGE.get(req_status, 'DISCOVERED')
            elif stage:
                canonical_stage = stage
                canonical_status = STAGE_TO_STATUS.get(stage, 'NOT_STARTED')
            else:
                canonical_status = 'NOT_STARTED'
                canonical_stage = 'DISCOVERED'

            next_action = STATUS_NEXT_ACTIONS.get(canonical_status, "Proceed to next step.")

            defaults = {
                "status": canonical_status,
                "stage": canonical_stage,
                "completed_documents": completed_documents,
                "application_reference_number": ref_no,
                "submission_mode": submission_mode,
                "is_user_reported": True,
                "next_immediate_action": next_action,
                "notes": notes
            }
            if applied_date:
                defaults["applied_date"] = applied_date

            record, created = ApplicationRecord.objects.update_or_create(
                profile=profile,
                scheme=scheme,
                defaults=defaults
            )

            serializer = ApplicationRecordSerializer(record)
            return Response({
                "status": "RECORD_SAVED",
                "is_new": created,
                "record": serializer.data
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)

class AcknowledgeReEvaluationView(APIView):
    def post(self, request):
        session_token = request.data.get('session_token')
        scheme_code = request.data.get('scheme_code')

        if not session_token:
            return Response({"error": "session_token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = StudentProfile.objects.get(session_token=session_token)
            qs = ApplicationRecord.objects.filter(profile=profile)
            if scheme_code:
                qs = qs.filter(scheme__code=scheme_code)
            count = qs.update(needs_re_evaluation=False)
            return Response({"status": "ACKNOWLEDGED", "updated_count": count})
        except StudentProfile.DoesNotExist:
            return Response({"status": "ACKNOWLEDGED", "updated_count": 0})


class RejectionScenariosView(APIView):
    """
    Returns verified canonical scrutiny rejection scenarios under MahaDBT / RTS Act.
    GET /api/v1/tracker/rejection_scenarios/
    """
    def get(self, request):
        return Response({"scenarios": RejectionRecoveryService.get_all_scenarios()})


class RejectionRecoveryView(APIView):
    """
    Translates scrutiny remarks, explains the 15-day resubmission window, document remedies,
    and verified statutory appeal routes.
    POST /api/v1/tracker/rejection_recovery/
    """
    def post(self, request):
        code = request.data.get("rejection_code")
        custom_text = request.data.get("custom_rejection_text")
        scheme_code = request.data.get("scheme_code")
        result = RejectionRecoveryService.diagnose_and_navigate(
            rejection_code=code,
            custom_rejection_text=custom_text,
            scheme_code=scheme_code
        )
        return Response(result)


