import datetime
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint


class Scheme(models.Model):
    BENEFIT_TYPE_CHOICES = [
        ('TUITION_FEE_WAIVER', 'Tuition & Exam Fee Waiver'),
        ('HOSTEL_ALLOWANCE', 'Hostel Maintenance Allowance'),
        ('MAINTENANCE_STIPEND', 'Monthly Maintenance Allowance / Stipend'),
        ('LODGING_BOARDING', 'Lodging & Boarding Allowance'),
        ('BOOK_STATIONERY', 'Book & Equipment Allowance'),
    ]

    CATEGORY_CHOICES = [
        ('EDUCATION', 'Education'),
        ('AGRICULTURE', 'Agriculture'),
        ('HEALTH', 'Health'),
        ('HOUSING', 'Housing'),
        ('WOMEN_CHILD', 'Women & Child'),
        ('SKILL_EMPLOYMENT', 'Skill & Employment'),
        ('OTHER', 'Other'),
    ]

    JURISDICTION_CHOICES = [
        ('STATE', 'State'),
        ('CENTRAL', 'Central'),
    ]

    VERIFICATION_CHOICES = [
        ('UNVERIFIED', 'Unverified'),
        ('VERIFIED', 'Verified'),
        ('NEEDS_REVIEW', 'Needs Review'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True)
    version = models.CharField(max_length=20, default='2024.1')
    effective_academic_year = models.CharField(max_length=30, default='2024-2025')
    name = models.CharField(max_length=255)
    name_marathi = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='OTHER')
    jurisdiction = models.CharField(max_length=10, choices=JURISDICTION_CHOICES, default='STATE')
    state = models.CharField(max_length=60, default='Maharashtra', blank=True)

    # Statutory authority & legal transparency
    statutory_gr = models.CharField(max_length=255, help_text="Official Government Resolution reference")
    official_portal_url = models.URLField(blank=True)
    official_source_url = models.URLField(blank=True, help_text='Official notification/GR link')
    portal_name = models.CharField(max_length=100, default='MahaDBT')

    benefit_type = models.CharField(max_length=40, choices=BENEFIT_TYPE_CHOICES)
    benefit_amount_text = models.CharField(max_length=255)
    estimated_annual_value = models.IntegerField(default=0, help_text="Estimated annual rupee value for stacking calculation")
    brief_description = models.TextField()

    # Rule definition (JSONB AST with boundary checking rules and conditions)
    rules = models.JSONField(default=dict)
    eligibility_criteria = models.JSONField(default=dict, blank=True, help_text='Nested eligibility tree validated by apps.eligibility_engine.schema. Source of truth for the eligibility engine.')

    # Stacking logic: which other benefit types can this be combined with?
    stackable_with_benefit_types = models.JSONField(default=list, blank=True)

    application_steps = models.JSONField(default=list, blank=True)
    application_deadline = models.DateField(null=True, blank=True, help_text='Only if officially specified')

    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='UNVERIFIED')
    last_verified_on = models.DateField(null=True, blank=True)
    is_sample = models.BooleanField(default=False, help_text='True marks TEST DATA, never a verified record')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(
                name='scheme_verified_needs_source_and_date',
                condition=~Q(verification_status='VERIFIED') | (Q(last_verified_on__isnull=False) & ~Q(official_source_url='')),
            ),
            CheckConstraint(
                name='scheme_sample_not_verified',
                condition=~Q(is_sample=True) | ~Q(verification_status='VERIFIED'),
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.eligibility_criteria:
            from apps.eligibility_engine.schema import validate_criteria, InvalidRuleError
            try:
                validate_criteria(self.eligibility_criteria)
            except InvalidRuleError as exc:
                raise ValidationError({'eligibility_criteria': str(exc)})

        if self.verification_status == 'VERIFIED':
            if not self.last_verified_on:
                errors['last_verified_on'] = 'A verified scheme must have a last_verified_on date.'
            if not self.official_source_url:
                errors['official_source_url'] = 'A verified scheme must have an official_source_url.'

        if self.is_sample and self.verification_status == 'VERIFIED':
            errors['verification_status'] = 'Sample (test) data can never be marked VERIFIED.'

        if self.application_deadline and self.application_deadline < datetime.date(2000, 1, 1):
            errors['application_deadline'] = 'Application deadline must be on or after 2000-01-01.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def record_rule_change(self, new_rules, changed_by='Department Officer', change_summary='Revised statutory eligibility rules', new_criteria=None):
        from apps.tracker.models import ApplicationRecord
        import datetime

        old_rules = dict(self.rules or {})
        old_version = self.version

        # Calculate new version e.g. 2024.1 -> 2024.2
        try:
            parts = old_version.split('.')
            if len(parts) >= 2 and parts[-1].isdigit():
                new_ver = '.'.join(parts[:-1]) + '.' + str(int(parts[-1]) + 1)
            else:
                new_ver = f"{old_version}.1"
        except Exception:
            new_ver = f"{old_version}-rev"

        self.version = new_ver
        self.rules = new_rules
        if new_criteria:
            self.eligibility_criteria = new_criteria
        self.save()

        from django.utils import timezone

        # Identify saved applications and flag re-evaluation
        apps = ApplicationRecord.objects.filter(scheme=self)
        affected_count = apps.count()
        apps.update(
            needs_re_evaluation=True,
            re_evaluation_reason=f"Eligibility criteria updated to v{new_ver} by {changed_by}: {change_summary}",
            re_evaluation_notified_at=timezone.now()
        )

        version_rec = SchemeRuleVersion.objects.create(
            scheme=self,
            version=new_ver,
            changed_by=changed_by,
            change_type='RULE_UPDATE',
            change_summary=change_summary,
            previous_rules=old_rules,
            new_rules=new_rules,
            affected_applications_count=affected_count
        )
        return version_rec, affected_count


class RequiredDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(
        'Scheme',
        related_name='required_documents',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        constraints = [
            UniqueConstraint(fields=['scheme', 'name'], name='unique_required_document_per_scheme'),
        ]

    def __str__(self):
        return self.name


class EligibilityRule(models.Model):
    OPERATOR_CHOICES = [
        ('eq', 'equals'),
        ('neq', 'not equals'),
        ('gte', 'greater than or equal'),
        ('lte', 'less than or equal'),
        ('in', 'in'),
        ('not_in', 'not in'),
        ('exists', 'exists'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(
        'Scheme',
        related_name='eligibility_rules',
        on_delete=models.CASCADE,
    )
    code = models.CharField(max_length=20, help_text="Rule code, e.g. 'R1'")
    description = models.TextField()
    field = models.CharField(
        max_length=64,
        validators=[RegexValidator(r'^[a-z][a-z0-9_]*$', 'Use a snake_case field key.')],
    )
    operator = models.CharField(max_length=10, choices=OPERATOR_CHOICES)
    value = models.JSONField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'code']
        constraints = [
            UniqueConstraint(fields=['scheme', 'code'], name='unique_rule_code_per_scheme'),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.operator != 'exists' and self.value is None:
            errors['value'] = 'A value is required for this operator.'
        elif self.operator in ('in', 'not_in') and not isinstance(self.value, list):
            errors['value'] = 'Operators in/not_in require a list value.'
        elif self.operator in ('gte', 'lte') and (
            isinstance(self.value, bool) or not isinstance(self.value, (int, float))
        ):
            errors['value'] = 'Operators gte/lte require a numeric value.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.code}: {self.field} {self.operator}"

class SchemeRuleVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(
        'Scheme',
        related_name='rule_versions',
        on_delete=models.CASCADE,
    )
    version = models.CharField(max_length=30)
    changed_by = models.CharField(max_length=100, default='Department Officer')
    changed_at = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(
        max_length=30,
        choices=[
            ('CREATED', 'Created Scheme'),
            ('RULE_UPDATE', 'Rule Criteria Revised'),
            ('METADATA_UPDATE', 'Metadata / Verification Updated'),
            ('DOCUMENTS_UPDATE', 'Document Requirements Updated'),
            ('DEACTIVATED', 'Scheme Deactivated'),
            ('REACTIVATED', 'Scheme Reactivated'),
        ],
        default='RULE_UPDATE',
    )
    change_summary = models.TextField(help_text="Clear explanation of statutory changes")
    previous_rules = models.JSONField(default=dict, blank=True)
    new_rules = models.JSONField(default=dict, blank=True)
    affected_applications_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.scheme.code} v{self.version} ({self.change_type}) by {self.changed_by}"

