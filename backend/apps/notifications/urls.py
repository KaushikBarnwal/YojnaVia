from django.urls import path
from .views import (
    NotificationPreferencesView,
    VerifyMobileView,
    NotificationHistoryView,
    TriggerTestReminderView,
    AdminDeliveryConsoleView,
    WhatsAppWebhookView
)

urlpatterns = [
    path('preferences/', NotificationPreferencesView.as_view(), name='notification-preferences'),
    path('verify_mobile/', VerifyMobileView.as_view(), name='notification-verify-mobile'),
    path('history/', NotificationHistoryView.as_view(), name='notification-history'),
    path('trigger_test/', TriggerTestReminderView.as_view(), name='notification-trigger-test'),
    path('admin/delivery_console/', AdminDeliveryConsoleView.as_view(), name='notification-admin-console'),
    path('webhook/whatsapp/', WhatsAppWebhookView.as_view(), name='notification-whatsapp-webhook'),
]
