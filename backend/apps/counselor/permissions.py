import uuid
from typing import Optional
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from .models import CounselorUser, CitizenCase, CaseAccessAuditLog

# In-memory session token dictionary for counselor accounts
COUNSELOR_TOKENS = {}


def authenticate_counselor(request) -> Optional[CounselorUser]:
    """
    Extracts and authenticates Counselor or Center Supervisor from Authorization header
    or demo header for seamless UI testing.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1].strip()
        if token in COUNSELOR_TOKENS:
            user_id = COUNSELOR_TOKENS[token]
            try:
                return CounselorUser.objects.select_related('center').get(id=user_id, is_active=True)
            except CounselorUser.DoesNotExist:
                return None

    # Demo fallback header for quick evaluation & testing
    demo_user = request.META.get('HTTP_X_COUNSELOR_USERNAME') or request.query_params.get('counselor_user')
    if demo_user:
        try:
            return CounselorUser.objects.select_related('center').get(username=demo_user, is_active=True)
        except CounselorUser.DoesNotExist:
            return None

    return None


def require_counselor_auth(request) -> CounselorUser:
    """Enforces active counselor or supervisor session."""
    user = authenticate_counselor(request)
    if not user:
        raise AuthenticationFailed("Authentication required. Please log in with authorized Counselor credentials.")
    return user


def verify_case_center_access(user: CounselorUser, case: CitizenCase, action: str = "PROFILE_VIEWED") -> None:
    """
    Strict Cross-Center Protection:
    Ensures counselor can only view or modify cases assigned to their own center.
    Attempts to access another center's case are logged and blocked with 403 Forbidden.
    """
    if user.role == 'ADMIN':
        return

    if user.center_id != case.center_id:
        CaseAccessAuditLog.objects.create(
            case=case,
            counselor=user,
            action='UNAUTHORIZED_ACCESS_BLOCKED',
            details={"attempted_by": user.username, "user_center": user.center.code, "case_center": case.center.code}
        )
        raise PermissionDenied(
            f"Access Denied: Case {case.case_number} is registered at {case.center.name}. "
            f"Cross-center access is strictly forbidden under citizen privacy rules."
        )


def verify_active_consent(case: CitizenCase) -> None:
    """
    Consent Guard:
    Verifies that the citizen's consent is active.
    If consent has been withdrawn, profile access is immediately denied.
    """
    if not hasattr(case, 'consent') or case.consent.consent_status != 'ACTIVE':
        raise PermissionDenied(
            f"Access Denied: Citizen consent for case {case.case_number} has been withdrawn or expired. "
            f"Assisted profile access is legally revoked."
        )
