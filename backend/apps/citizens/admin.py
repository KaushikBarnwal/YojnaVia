from django.contrib import admin
from apps.citizens.models import (
    UserProfile,
    HouseholdMember,
    Application,
    Conversation,
    VerificationLog
)

class HouseholdMemberInline(admin.TabularInline):
    model = HouseholdMember
    extra = 0
    fields = ('relation', 'label', 'age', 'is_student', 'annual_income_inr')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'display_label', 'caste_category', 'state', 'district',
        'age_years', 'annual_household_income_inr', 'is_sample', 'created_at'
    )
    list_filter = ('caste_category', 'state', 'is_sample', 'created_at')
    search_fields = ('display_label', 'district')
    readonly_fields = ('id', 'owner_token_hash', 'created_at', 'updated_at')
    inlines = [HouseholdMemberInline]

@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ('label', 'profile', 'relation', 'age', 'is_student', 'annual_income_inr')
    list_filter = ('relation', 'is_student')
    search_fields = ('label', 'profile__display_label')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'scheme', 'status', 'submitted_on', 'updated_at')
    list_filter = ('status', 'scheme')
    search_fields = ('profile__display_label', 'scheme__name', 'scheme__code', 'reference_note')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'language', 'status', 'created_at')
    list_filter = ('status', 'language')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'scheme', 'action', 'previous_status', 'new_status', 'actor', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('scheme__name', 'scheme__code', 'note', 'actor')
    readonly_fields = (
        'id', 'scheme', 'action', 'previous_status',
        'new_status', 'source_url', 'note', 'actor', 'created_at'
    )

    def has_add_permission(self, request):
        return False  # VerificationLogs are created by system/actions only
