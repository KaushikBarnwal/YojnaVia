import uuid
from django.db import models
from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme

class ApplicationRecord(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not started'),
        ('DOCUMENTS_PENDING', 'Documents pending'),
        ('DOCUMENTS_READY', 'Documents ready'),
        ('APPLIED', 'Applied'),
        ('UNDER_REVIEW', 'Under review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    STAGE_CHOICES = [
        ('DISCOVERED', 'Discovered & Matched'),
        ('DOCUMENTS_PREPARATION', 'Preparing Documents'),
        ('ONLINE_REGISTRATION', 'Submitted Online on Portal'),
        ('COLLEGE_SCRUTINY', 'College Clerk Scrutiny & Hardcopy Submitted'),
        ('DEPT_APPROVAL', 'Department Approved & Sanctioned'),
        ('DISBURSED', 'Benefit Disbursed into Bank Account (DBT)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(StudentProfile, related_name='applications', on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, related_name='tracked_applications', on_delete=models.CASCADE)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NOT_STARTED')
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='DISCOVERED')
    completed_documents = models.JSONField(default=list, blank=True, help_text="List of document codes verified/gathered")
    
    # Offline and online reference numbers
    application_reference_number = models.CharField(max_length=100, blank=True)
    applied_date = models.DateField(null=True, blank=True)
    submission_mode = models.CharField(max_length=50, default='Online Portal')
    is_user_reported = models.BooleanField(default=True, help_text="Always True: Statuses are self-reported by the citizen")
    
    # Rule change invalidation intelligence
    needs_re_evaluation = models.BooleanField(default=False, help_text="Flagged when statutory rules for this scheme change")
    re_evaluation_reason = models.TextField(blank=True)
    re_evaluation_notified_at = models.DateTimeField(null=True, blank=True)
    
    # Actionable guidance
    next_immediate_action = models.CharField(max_length=255, default='Review required certificates and prepare documents.')
    next_action_deadline = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'scheme')

    def __str__(self):
        return f"{self.profile.name} - {self.scheme.code} ({self.status})"
