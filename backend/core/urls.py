"""
URL configuration for core project - YOJNAVIA.
"""
from django.contrib import admin
from django.urls import include, path
from apps.profiles.views import ProfileMeView, LoadPersonaView, PersonasListAPIView
from apps.schemes.views import SchemeListView, SchemeDetailView
from apps.eligibility.views import EvaluateEligibilityView, FamilyEligibilityView, ApplicationPreflightView
from apps.documents.views import DocumentDependencyGraphView
from apps.tracker.views import TrackerView, AcknowledgeReEvaluationView, RejectionScenariosView, RejectionRecoveryView
from apps.ai_assistant.views import IntakeChatView, IntakeStateView, IntakeCorrectView, IntakeRestartView
from apps.schemes.admin_views import (
    AdminLoginView,
    AdminMeView,
    AdminSchemeListView,
    AdminSchemeDetailView,
    AdminSchemeRuleUpdateView,
    AdminSchemeDeactivateToggleView,
    AdminSchemeHistoryView,
    AdminReRunMatchingView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Profiles & Personas
    path('api/v1/profiles/me/', ProfileMeView.as_view(), name='profile-me'),
    path('api/v1/profiles/load_persona/', LoadPersonaView.as_view(), name='load-persona'),
    path('api/v1/profiles/personas/', PersonasListAPIView.as_view(), name='personas-list'),

    # Schemes
    path('api/v1/schemes/', SchemeListView.as_view(), name='schemes-list'),
    path('api/v1/schemes/<str:code>/', SchemeDetailView.as_view(), name='scheme-detail'),
    path('api/v1/ps5/', include('apps.citizens.urls')),
    path('api/v1/ps5/evaluations/', include('apps.eligibility_engine.urls')),

    # Eligibility & Stacking Engine
    path('api/v1/eligibility/evaluate/', EvaluateEligibilityView.as_view(), name='evaluate-eligibility'),
    path('api/v1/eligibility/family/', FamilyEligibilityView.as_view(), name='family-eligibility'),
    path('api/v1/eligibility/preflight/', ApplicationPreflightView.as_view(), name='application-preflight'),

    # Cross-Scheme Document Dependency Graph
    path('api/v1/documents/dependency_graph/', DocumentDependencyGraphView.as_view(), name='document-dependency-graph'),

    # Actionable Application Tracker & Rejection Navigator
    path('api/v1/tracker/', TrackerView.as_view(), name='tracker-list'),
    path('api/v1/tracker/update/', TrackerView.as_view(), name='tracker-update'),
    path('api/v1/tracker/save/', TrackerView.as_view(), name='tracker-save'),
    path('api/v1/tracker/acknowledge_re_evaluation/', AcknowledgeReEvaluationView.as_view(), name='tracker-acknowledge'),
    path('api/v1/tracker/rejection_scenarios/', RejectionScenariosView.as_view(), name='rejection-scenarios'),
    path('api/v1/tracker/rejection_recovery/', RejectionRecoveryView.as_view(), name='rejection-recovery'),

    # Phase 5: Administration & Scheme Management
    path('api/v1/admin/auth/login/', AdminLoginView.as_view(), name='admin-login'),
    path('api/v1/admin/auth/me/', AdminMeView.as_view(), name='admin-me'),
    path('api/v1/admin/schemes/', AdminSchemeListView.as_view(), name='admin-schemes-list'),
    path('api/v1/admin/schemes/<str:code>/', AdminSchemeDetailView.as_view(), name='admin-scheme-detail'),
    path('api/v1/admin/schemes/<str:code>/rules/', AdminSchemeRuleUpdateView.as_view(), name='admin-scheme-rules'),
    path('api/v1/admin/schemes/<str:code>/deactivate/', AdminSchemeDeactivateToggleView.as_view(), name='admin-scheme-deactivate'),
    path('api/v1/admin/schemes/<str:code>/history/', AdminSchemeHistoryView.as_view(), name='admin-scheme-history'),
    path('api/v1/admin/schemes/<str:code>/re_evaluate_matching/', AdminReRunMatchingView.as_view(), name='admin-scheme-rerun-matching'),

    # AI Intake
    path('api/v1/intake/chat/', IntakeChatView.as_view(), name='intake-chat'),
    path('api/v1/intake/state/', IntakeStateView.as_view(), name='intake-state'),
    path('api/v1/intake/correct/', IntakeCorrectView.as_view(), name='intake-correct'),
    path('api/v1/intake/restart/', IntakeRestartView.as_view(), name='intake-restart'),
]
