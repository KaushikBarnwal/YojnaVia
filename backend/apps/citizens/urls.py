from django.urls import path

from apps.citizens.views import (
    ApplicationCreateListView,
    ApplicationDetailView,
    ProfileCreateView,
    ProfileDetailView,
    SchemeDetailView,
    SchemeDocumentsView,
    SchemeListView,
)

urlpatterns = [
    path('schemes/', SchemeListView.as_view(), name='ps5-scheme-list'),
    path('schemes/<str:code>/', SchemeDetailView.as_view(), name='ps5-scheme-detail'),
    path('schemes/<str:code>/documents/', SchemeDocumentsView.as_view(), name='ps5-scheme-documents'),
    path('profiles/', ProfileCreateView.as_view(), name='ps5-profile-create'),
    path('profiles/<uuid:profile_ref>/', ProfileDetailView.as_view(), name='ps5-profile-detail'),
    path('applications/', ApplicationCreateListView.as_view(), name='ps5-application-list'),
    path('applications/<uuid:application_ref>/', ApplicationDetailView.as_view(), name='ps5-application-detail'),
]
