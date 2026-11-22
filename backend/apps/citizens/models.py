import hashlib
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.schemes.models import Scheme


class UserProfile(models.Model):
    CASTE_CHOICES = [
        ('GENERAL', 'General'),
        ('OPEN', 'Open / General'),
        ('OBC', 'Other Backward Class'),
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
        ('VJNT', 'Vimukta Jati / Nomadic Tribes'),
        ('SBC', 'Special Backward Class'),
        ('EWS', 'Economically Weaker Section'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        editable=False,
        help_text='SHA-256 hex digest of the owner token. The raw token is never stored.',
    )
    display_label = models.CharField(max_length=100)
    is_sample = models.BooleanField(default=True, help_text='Phase 1 accepts sample data only')
    state = models.CharField(max_length=60, default='Maharashtra')
    district = models.CharField(max_length=80, blank=True)
    age_years = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(120)],
    )
    annual_household_income_inr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    caste_category = models.CharField(max_length=10, choices=CASTE_CHOICES, null=True, blank=True)
    is_maharashtra_domicile = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if not self.is_sample:
            raise ValidationError({'is_sample': 'Only sample profiles are accepted in this phase.'})

    def __str__(self):
        return self.display_label


class HouseholdMember(models.Model):
    RELATION_CHOICES = [
        ('SELF', 'Self'),
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        UserProfile,
        related_name='members',
        on_delete=models.CASCADE,
    )
    relation = models.CharField(max_length=10, choices=RELATION_CHOICES)
    label = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(120)],
    )
    is_student = models.BooleanField(default=False)
    annual_income_inr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ['relation', 'label']
        constraints = [
            models.UniqueConstraint(
                fields=['profile'],
                condition=Q(relation='SELF'),
                name='one_self_member_per_profile',
            ),
        ]

    def __str__(self):
        return f'{self.label} ({self.relation})'


class Conversation(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('mr', 'Marathi'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        UserProfile,
        null=True,
        blank=True,
        related_name='conversations',
        on_delete=models.SET_NULL,
    )
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    extracted_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text='Draft fields only. Raw transcripts are NOT stored in this phase.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Conversation {self.id} ({self.status})'


class Application(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    SUBMITTED_STATUSES = ('SUBMITTED', 'APPROVED', 'REJECTED')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        UserProfile,
        related_name='applications',
        on_delete=models.CASCADE,
    )
    scheme = models.ForeignKey(
        Scheme,
        related_name='citizen_applications',
        on_delete=models.PROTECT,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    reference_note = models.CharField(max_length=100, blank=True)
    submitted_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, validators=[MaxLengthValidator(1000)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'scheme'],
                name='unique_application_per_profile_scheme',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.status in self.SUBMITTED_STATUSES and not self.submitted_on:
            errors['submitted_on'] = 'submitted_on is required once submitted, approved or rejected.'

        if self.scheme_id and not self.scheme.is_active:
            errors['scheme'] = 'Scheme is not active.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.profile_id} -> {self.scheme_id} ({self.status})'


class VerificationLog(models.Model):
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('VERIFIED', 'Verified'),
        ('MARKED_NEEDS_REVIEW', 'Marked Needs Review'),
        ('DEACTIVATED', 'Deactivated'),
        ('REACTIVATED', 'Reactivated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(
        Scheme,
        related_name='verification_logs',
        on_delete=models.CASCADE,
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30, blank=True)
    source_url = models.URLField(blank=True)
    note = models.TextField(blank=True)
    actor = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.scheme_id}: {self.action}'
