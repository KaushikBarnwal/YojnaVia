import datetime
from django.contrib import admin
from django.contrib import messages
from apps.schemes.models import Scheme, RequiredDocument, EligibilityRule, SchemeRuleVersion
from apps.citizens.models import VerificationLog

class RequiredDocumentInline(admin.TabularInline):
    model = RequiredDocument
    extra = 1
    fields = ('name', 'description', 'is_mandatory', 'sort_order')

class EligibilityRuleInline(admin.TabularInline):
    model = EligibilityRule
    extra = 1
    fields = ('code', 'field', 'operator', 'value', 'is_mandatory', 'sort_order', 'description')

@admin.action(description="Deactivate selected schemes")
def deactivate_schemes(modeladmin, request, queryset):
    count = 0
    for scheme in queryset:
        if scheme.is_active:
            scheme.is_active = False
            scheme.save(update_fields=['is_active'])
            VerificationLog.objects.create(
                scheme=scheme,
                action='DEACTIVATED',
                previous_status=scheme.verification_status,
                new_status=scheme.verification_status,
                note='Deactivated via Django admin action',
                actor=request.user.username or 'admin'
            )
            count += 1
    messages.success(request, f"Successfully deactivated {count} scheme(s).")

@admin.action(description="Mark selected schemes as Needs Review")
def mark_needs_review(modeladmin, request, queryset):
    count = 0
    for scheme in queryset:
        prev = scheme.verification_status
        scheme.verification_status = 'NEEDS_REVIEW'
        scheme.save(update_fields=['verification_status'])
        VerificationLog.objects.create(
            scheme=scheme,
            action='MARKED_NEEDS_REVIEW',
            previous_status=prev,
            new_status='NEEDS_REVIEW',
            note='Flagged for review via Django admin action',
            actor=request.user.username or 'admin'
        )
        count += 1
    messages.success(request, f"Marked {count} scheme(s) as Needs Review.")

@admin.action(description="Mark non-sample schemes as Verified")
def verify_schemes(modeladmin, request, queryset):
    count = 0
    skipped = 0
    for scheme in queryset:
        if scheme.is_sample:
            skipped += 1
            continue
        if not scheme.official_source_url:
            skipped += 1
            continue
        prev = scheme.verification_status
        scheme.verification_status = 'VERIFIED'
        scheme.last_verified_on = datetime.date.today()
        scheme.save(update_fields=['verification_status', 'last_verified_on'])
        VerificationLog.objects.create(
            scheme=scheme,
            action='VERIFIED',
            previous_status=prev,
            new_status='VERIFIED',
            source_url=scheme.official_source_url,
            note='Verified via Django admin action',
            actor=request.user.username or 'admin'
        )
        count += 1
    if count:
        messages.success(request, f"Successfully verified {count} scheme(s).")
    if skipped:
        messages.warning(request, f"Skipped {skipped} scheme(s) because sample records or records without source URLs cannot be marked VERIFIED.")

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'category', 'jurisdiction', 'state',
        'benefit_type', 'verification_status', 'is_sample', 'is_active', 'last_verified_on'
    )
    list_filter = (
        'category', 'jurisdiction', 'verification_status',
        'is_sample', 'is_active', 'state'
    )
    search_fields = ('code', 'name', 'name_marathi', 'department')
    inlines = [RequiredDocumentInline, EligibilityRuleInline]
    actions = [deactivate_schemes, mark_needs_review, verify_schemes]
    fieldsets = (
        ('Basic Identification', {
            'fields': ('code', 'name', 'name_marathi', 'category', 'jurisdiction', 'state', 'department')
        }),
        ('Benefit & Official Links', {
            'fields': ('benefit_type', 'benefit_amount_text', 'estimated_annual_value', 'brief_description', 'official_portal_url', 'official_source_url', 'portal_name')
        }),
        ('Rules & Steps', {
            'fields': ('rules', 'stackable_with_benefit_types', 'application_steps', 'application_deadline')
        }),
        ('Verification & Status', {
            'fields': ('verification_status', 'last_verified_on', 'is_sample', 'is_active', 'statutory_gr', 'version', 'effective_academic_year')
        }),
    )

@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'scheme', 'is_mandatory', 'sort_order')
    list_filter = ('is_mandatory', 'scheme')
    search_fields = ('name', 'scheme__name', 'scheme__code')

@admin.register(EligibilityRule)
class EligibilityRuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'scheme', 'field', 'operator', 'value', 'is_mandatory', 'sort_order')
    list_filter = ('operator', 'is_mandatory', 'scheme')
    search_fields = ('code', 'field', 'scheme__name', 'scheme__code')

@admin.register(SchemeRuleVersion)
class SchemeRuleVersionAdmin(admin.ModelAdmin):
    list_display = ('scheme', 'version', 'change_type', 'changed_by', 'changed_at', 'affected_applications_count')
    list_filter = ('change_type', 'changed_by')
    search_fields = ('scheme__code', 'scheme__name', 'change_summary')
    readonly_fields = ('changed_at',)
