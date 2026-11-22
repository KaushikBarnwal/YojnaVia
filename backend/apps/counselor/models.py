import uuid
from django.db import models
from django.utils import timezone
from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme
from apps.tracker.models import ApplicationRecord


class ServiceCenter(models.Model):
    CENTER_TYPES = [
        ('CSC_DIGITAL_SEVA', 'CSC Digital Seva Kendra'),
        ('AAPLE_SARKAR_KENDRA', 'Aaple Sarkar Seva Kendra (ASSK)'),
        ('GRAM_PANCHAYAT_SEVA', 'Gram Panchayat Sangram Kendra'),
        ('COLLEGE_FACILITATION', 'College Student Facilitation Cell'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    vle_id = models.CharField(max_length=100, help_text="Village Level Entrepreneur Registration ID")
    center_type = models.CharField(max_length=40, choices=CENTER_TYPES, default='AAPLE_SARKAR_KENDRA')
    district = models.CharField(max_length=50)
    taluka = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.code}] - {self.district}"


class CounselorUser(models.Model):
    ROLE_CHOICES = [
        ('COUNSELOR', 'Service Counselor / Kendra Operator'),
        ('SUPERVISOR', 'Center Supervisor / Lead VLE'),
        ('ADMIN', 'Platform Administrator'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='COUNSELOR')
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE, related_name='staff')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.center.code}"


class CitizenCase(models.Model):
    STATUS_CHOICES = [
        ('INTAKE_PENDING', 'Intake Pending'),
        ('ELIGIBILITY_DISCOVERED', 'Eligibility Discovered'),
        ('DOCUMENTS_PENDING', 'Documents Pending'),
        ('READY_FOR_APPLICATION', 'Ready for Application'),
        ('APPLIED_TRACKING', 'Applied & In Tracking'),
        ('ESCALATED_SUPERVISOR', 'Escalated to Supervisor'),
        ('CLOSED_HANDOVER', 'Closed & Handed Over to Citizen'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent Cutoff (<7 Days)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_number = models.CharField(max_length=50, unique=True, db_index=True)
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE, related_name='cases')
    assigned_counselor = models.ForeignKey(CounselorUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='assisted_cases')

    # Basic Contact / Identity for the Kendra desk
    citizen_name = models.CharField(max_length=150)
    citizen_mobile = models.CharField(max_length=20, blank=True)
    case_status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='INTAKE_PENDING')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    target_scheme_category = models.CharField(max_length=100, default='Higher Education & Scholarships')

    # Follow-up and Escalation
    follow_up_date = models.DateField(null=True, blank=True)
    escalated_to_supervisor = models.BooleanField(default=False)
    escalation_reason = models.TextField(blank=True)

    # Handover / Closure
    closure_summary = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.case_number} - {self.citizen_name} [{self.case_status}]"


class CitizenConsentRecord(models.Model):
    CONSENT_STATUS_CHOICES = [
        ('ACTIVE', 'Active Consent'),
        ('WITHDRAWN', 'Consent Withdrawn'),
        ('EXPIRED', 'Consent Expired'),
    ]

    METHOD_CHOICES = [
        ('IN_PERSON_VERBAL', 'In-Person Verbal Consent (Counselor Attested)'),
        ('PHYSICAL_SLIP', 'Physical Signature Slip on File'),
        ('DIGITAL_ACK', 'Digital Acknowledgment on Terminal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.OneToOneField(CitizenCase, on_delete=models.CASCADE, related_name='consent')
    consent_status = models.CharField(max_length=20, choices=CONSENT_STATUS_CHOICES, default='ACTIVE')
    consent_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='IN_PERSON_VERBAL')
    scope_description = models.TextField(default=(
        "Citizen explicitly authorizes the CSC Counselor to access and review demographic details, "
        "income band, civil document requirements, and portal application statuses solely for welfare "
        "scheme discovery and application readiness assistance. Aadhaar numbers, OTPs, and bank passwords "
        "will NEVER be requested or recorded."
    ))
    granted_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    withdrawn_reason = models.TextField(blank=True)
    attesting_counselor = models.ForeignKey(CounselorUser, on_delete=models.CASCADE)

    def withdraw(self, reason: str):
        self.consent_status = 'WITHDRAWN'
        self.withdrawn_at = timezone.now()
        self.withdrawn_reason = reason
        self.save()

    def __str__(self):
        return f"Consent {self.case.case_number}: {self.consent_status}"


class CaseAccessAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CASE_CREATED', 'Case Registered'),
        ('CONSENT_RECORDED', 'Consent Recorded'),
        ('PROFILE_VIEWED', 'Citizen Profile Viewed'),
        ('PROFILE_UPDATED', 'Citizen Profile Updated'),
        ('ELIGIBILITY_EVALUATED', 'Eligibility Engine Evaluated'),
        ('PREFLIGHT_RUN', 'Application Preflight Audit Executed'),
        ('DOCUMENTS_CHECKED', 'Document Checklist Updated'),
        ('CASE_NOTE_ADDED', 'Case Note Added'),
        ('CASE_ESCALATED', 'Escalated to Center Supervisor'),
        ('CONSENT_WITHDRAWN', 'Citizen Consent Withdrawn'),
        ('CASE_CLOSED', 'Case Closed & Handed Over'),
        ('UNAUTHORIZED_ACCESS_BLOCKED', 'Unauthorized Cross-Center Access Blocked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(CitizenCase, on_delete=models.CASCADE, related_name='audit_logs')
    counselor = models.ForeignKey(CounselorUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.CharField(max_length=45, blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.counselor.username} -> {self.case.case_number}: {self.action}"


class CounselorCaseNote(models.Model):
    NOTE_TYPES = [
        ('GENERAL', 'General Case Note'),
        ('DOCUMENT_FOLLOWUP', 'Document Procurement Follow-Up'),
        ('GRIEVANCE_ASSISTANCE', 'Scrutiny Query / Grievance Assistance'),
        ('SUPERVISOR_REMARK', 'Supervisor Guidance / Escalation Remark'),
        ('HANDOVER_SUMMARY', 'Handover Summary to Citizen'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(CitizenCase, on_delete=models.CASCADE, related_name='notes')
    counselor = models.ForeignKey(CounselorUser, on_delete=models.CASCADE)
    note_type = models.CharField(max_length=30, choices=NOTE_TYPES, default='GENERAL')
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.case.case_number} Note by {self.counselor.name} ({self.note_type})"
