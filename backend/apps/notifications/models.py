import uuid
from django.db import models
from django.utils import timezone
from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme
from apps.tracker.models import ApplicationRecord


class NotificationPreference(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('mr', 'मराठी (Marathi)'),
        ('hi', 'हिंदी (Hindi)'),
    ]

    profile = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        primary_key=True
    )

    # Contact details
    mobile_number = models.CharField(max_length=20, blank=True, help_text="Indian mobile number (e.g. +919876543210)")
    is_mobile_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, blank=True)
    verification_sent_at = models.DateTimeField(null=True, blank=True)

    # Channel consent & timestamps
    whatsapp_enabled = models.BooleanField(default=False)
    whatsapp_opt_in_at = models.DateTimeField(null=True, blank=True)
    whatsapp_opt_out_at = models.DateTimeField(null=True, blank=True)

    sms_enabled = models.BooleanField(default=False)
    sms_opt_in_at = models.DateTimeField(null=True, blank=True)
    sms_opt_out_at = models.DateTimeField(null=True, blank=True)

    in_app_enabled = models.BooleanField(default=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

    # Specific reminder subscription toggles
    notify_deadlines = models.BooleanField(default=True)
    notify_missing_docs = models.BooleanField(default=True)
    notify_milestones = models.BooleanField(default=True)
    notify_inactivity = models.BooleanField(default=True)
    notify_grievances = models.BooleanField(default=True)
    notify_renewals = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def opt_in_whatsapp(self):
        self.whatsapp_enabled = True
        self.whatsapp_opt_in_at = timezone.now()
        self.save()

    def opt_out_whatsapp(self):
        self.whatsapp_enabled = False
        self.whatsapp_opt_out_at = timezone.now()
        self.save()

    def opt_in_sms(self):
        self.sms_enabled = True
        self.sms_opt_in_at = timezone.now()
        self.save()

    def opt_out_sms(self):
        self.sms_enabled = False
        self.sms_opt_out_at = timezone.now()
        self.save()

    def is_channel_permitted(self, channel: str) -> bool:
        """Verifies explicit consent before transmitting any message."""
        channel_upper = channel.upper()
        if channel_upper == 'WHATSAPP':
            return bool(self.whatsapp_enabled and self.is_mobile_verified and self.mobile_number)
        if channel_upper == 'SMS':
            return bool(self.sms_enabled and self.is_mobile_verified and self.mobile_number)
        if channel_upper == 'IN_APP':
            return self.in_app_enabled
        return False

    def __str__(self):
        return f"Prefs: {self.profile.name} (WA: {self.whatsapp_enabled}, SMS: {self.sms_enabled})"


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ('WHATSAPP', 'Meta WhatsApp Cloud API'),
        ('SMS', 'Indian SMS Gateway (DLT Compliant)'),
        ('IN_APP', 'In-App Alert Console'),
    ]

    EVENT_CHOICES = [
        ('DEADLINE_APPROACHING', 'Scheme Application Deadline Approaching'),
        ('MISSING_DOCUMENT_REMINDER', 'Pending Mandatory Document Reminder'),
        ('MILESTONE_UPDATED', 'Application Milestone Updated'),
        ('STATUS_INACTIVITY', 'No Status Change in 14 Days'),
        ('GRIEVANCE_RESUBMISSION', '15-Day Scrutiny Resubmission Clock'),
        ('ANNUAL_RENEWAL', 'Annual Academic & March 31 Income Certificate Renewal'),
        ('TEST_DEMO', '1-Click Citizen Test Reminder'),
    ]

    STATUS_CHOICES = [
        ('QUEUED', 'Queued for Delivery'),
        ('SENT', 'Sent to Provider'),
        ('DELIVERED', 'Delivered to Citizen'),
        ('READ', 'Read by Citizen'),
        ('FAILED', 'Delivery Failed'),
        ('OPTED_OUT', 'Suppressed: Citizen Opted Out'),
        ('SIMULATED', 'Simulated Delivery (Demo Mode)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications')
    application = models.ForeignKey(ApplicationRecord, null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    scheme = models.ForeignKey(Scheme, null=True, blank=True, on_delete=models.SET_NULL)

    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    
    # Idempotency key prevents duplicate messages across identical events on the same day
    idempotency_key = models.CharField(max_length=180, unique=True, db_index=True)

    recipient = models.CharField(max_length=50, help_text="Phone number or session token")
    language = models.CharField(max_length=5, default='en')
    template_name = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    message_body = models.TextField()

    # Provider telemetry
    provider = models.CharField(max_length=50, default='SIMULATED')
    provider_message_id = models.CharField(max_length=150, blank=True, db_index=True)
    provider_response_raw = models.JSONField(default=dict, blank=True)
    delivery_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='QUEUED')
    error_message = models.TextField(blank=True)

    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.channel} -> {self.recipient}: {self.event_type} [{self.delivery_status}]"
