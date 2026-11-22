"""
URL configuration for core project - YojnaVia.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from apps.profiles.views import ProfileMeView, LoadPersonaView, PersonasListAPIView
from apps.schemes.views import SchemeListView, SchemeDetailView
from apps.eligibility.views import (
    EvaluateEligibilityView, 
    FamilyEligibilityView, 
    ApplicationPreflightView,
    WhatIfSimulationView,
    WhatIfPresetScenariosView
)
from apps.documents.views import DocumentDependencyGraphView
from apps.tracker.views import (
    TrackerView, 
    AcknowledgeReEvaluationView, 
    RejectionScenariosView, 
    RejectionRecoveryView,
    LifecycleStagesView,
    ApplicationLifecycleRoadmapView,
    CommunityGapReportView
)
from apps.ai_assistant.views import (
    IntakeChatView, 
    IntakeStateView, 
    IntakeCorrectView, 
    IntakeRestartView,
    GrSamplesListView,
    InterpretGrView,
    VoiceIntakeView,
    ConfirmVoiceIntakeView
)
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

def root_health_view(request):
    """Health check & API index endpoint for root /"""
    return JsonResponse({
        "app": "YOJNAVIA Sovereign Benefits API",
        "status": "healthy",
        "jurisdiction": "Maharashtra, India",
        "version": "v1",
        "api_root": "/api/v1/",
        "endpoints": {
            "schemes": "/api/v1/schemes/",
            "intake_chat": "/api/v1/intake/chat/",
            "personas": "/api/v1/profiles/personas/",
            "frontend": "https://yojna-via.vercel.app"
        }
    })


urlpatterns = [
    path('', root_health_view, name='root-health'),
    path('health/', root_health_view, name='health-check'),
    path('admin/', admin.site.urls),

    # Profiles & Personas
    path('api/v1/profiles/me/', ProfileMeView.as_view(), name='profile-me'),
    path('api/v1/profiles/load_persona/', LoadPersonaView.as_view(), name='load-persona'),
    path('api/v1/profiles/personas/', PersonasListAPIView.as_view(), name='personas-list'),

    # Schemes
    path('api/v1/schemes/', SchemeListView.as_view(), name='schemes-list'),
    path('api/v1/schemes/<str:code>/', SchemeDetailView.as_view(), name='scheme-detail'),
    # Notifications & Alerts
    path('api/v1/notifications/', include('apps.notifications.urls')),

    # CSC Counselor Assisted-Service Dashboard
    path('api/v1/counselor/', include('apps.counselor.urls')),
    path('api/v1/ps5/', include('apps.citizens.urls')),
    path('api/v1/ps5/evaluations/', include('apps.eligibility_engine.urls')),

    # Eligibility, Stacking & What-If Simulation Engine
    path('api/v1/eligibility/evaluate/', EvaluateEligibilityView.as_view(), name='evaluate-eligibility'),
    path('api/v1/eligibility/family/', FamilyEligibilityView.as_view(), name='family-eligibility'),
    path('api/v1/eligibility/preflight/', ApplicationPreflightView.as_view(), name='application-preflight'),
    path('api/v1/eligibility/what_if/', WhatIfSimulationView.as_view(), name='what-if-simulate'),
    path('api/v1/eligibility/what_if/presets/', WhatIfPresetScenariosView.as_view(), name='what-if-presets'),

    # Cross-Scheme Document Dependency Graph
    path('api/v1/documents/dependency_graph/', DocumentDependencyGraphView.as_view(), name='document-dependency-graph'),

    # Actionable Application Tracker, Rejection Navigator & Lifecycle Intelligence
    path('api/v1/tracker/', TrackerView.as_view(), name='tracker-list'),
    path('api/v1/tracker/update/', TrackerView.as_view(), name='tracker-update'),
    path('api/v1/tracker/save/', TrackerView.as_view(), name='tracker-save'),
    path('api/v1/tracker/acknowledge_re_evaluation/', AcknowledgeReEvaluationView.as_view(), name='tracker-acknowledge'),
    path('api/v1/tracker/rejection_scenarios/', RejectionScenariosView.as_view(), name='rejection-scenarios'),
    path('api/v1/tracker/rejection_recovery/', RejectionRecoveryView.as_view(), name='rejection-recovery'),
    path('api/v1/tracker/lifecycle/stages/', LifecycleStagesView.as_view(), name='lifecycle-stages'),
    path('api/v1/tracker/lifecycle/roadmap/', ApplicationLifecycleRoadmapView.as_view(), name='lifecycle-roadmap'),
    path('api/v1/tracker/community_intelligence/', CommunityGapReportView.as_view(), name='community-intelligence'),

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
    path('api/v1/intake/voice/', VoiceIntakeView.as_view(), name='intake-voice'),
    path('api/v1/intake/confirm_voice/', ConfirmVoiceIntakeView.as_view(), name='intake-confirm-voice'),
    path('api/v1/intake/state/', IntakeStateView.as_view(), name='intake-state'),
    path('api/v1/intake/correct/', IntakeCorrectView.as_view(), name='intake-correct'),
    path('api/v1/intake/restart/', IntakeRestartView.as_view(), name='intake-restart'),
    path('api/v1/assistant/voice_intake/', VoiceIntakeView.as_view(), name='assistant-voice-intake'),

    # Government Resolution (GR) & Gazette Interpreter
    path('api/v1/assistant/gr_samples/', GrSamplesListView.as_view(), name='gr-samples'),
    path('api/v1/assistant/interpret_gr/', InterpretGrView.as_view(), name='interpret-gr'),
]
