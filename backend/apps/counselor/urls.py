from django.urls import path
from .views import (
    CounselorLoginView,
    CounselorMeView,
    CounselorCaseListView,
    CounselorCaseDetailView,
    CounselorUpdateProfileView,
    CounselorCaseConsentWithdrawView,
    CounselorCaseNotesView,
    CounselorCaseEscalateView,
    CounselorCaseCloseView,
    CounselorEvaluateEligibilityView,
    CounselorPreflightReviewView,
    CounselorDocumentChecklistView,
    CenterAnalyticsView,
)

urlpatterns = [
    # Authentication & Profile
    path('auth/login/', CounselorLoginView.as_view(), name='counselor-login'),
    path('auth/me/', CounselorMeView.as_view(), name='counselor-me'),

    # Cases & Assisted Management
    path('cases/', CounselorCaseListView.as_view(), name='counselor-cases-list'),
    path('cases/<uuid:case_id>/', CounselorCaseDetailView.as_view(), name='counselor-case-detail'),
    path('cases/<uuid:case_id>/update_profile/', CounselorUpdateProfileView.as_view(), name='counselor-case-update-profile'),
    path('cases/<uuid:case_id>/withdraw_consent/', CounselorCaseConsentWithdrawView.as_view(), name='counselor-case-withdraw-consent'),
    path('cases/<uuid:case_id>/notes/', CounselorCaseNotesView.as_view(), name='counselor-case-notes'),
    path('cases/<uuid:case_id>/escalate/', CounselorCaseEscalateView.as_view(), name='counselor-case-escalate'),
    path('cases/<uuid:case_id>/close/', CounselorCaseCloseView.as_view(), name='counselor-case-close'),

    # Scheme Discovery & Preflight Reuse
    path('cases/<uuid:case_id>/evaluate_eligibility/', CounselorEvaluateEligibilityView.as_view(), name='counselor-case-evaluate'),
    path('cases/<uuid:case_id>/preflight/', CounselorPreflightReviewView.as_view(), name='counselor-case-preflight'),
    path('cases/<uuid:case_id>/documents/', CounselorDocumentChecklistView.as_view(), name='counselor-case-documents'),

    # Center-Level Analytics
    path('analytics/', CenterAnalyticsView.as_view(), name='counselor-analytics'),
]
