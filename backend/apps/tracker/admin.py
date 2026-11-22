from django.contrib import admin
from .models import ApplicationRecord

@admin.register(ApplicationRecord)
class ApplicationRecordAdmin(admin.ModelAdmin):
    list_display = ('profile', 'scheme', 'status', 'stage', 'application_reference_number', 'applied_date', 'needs_re_evaluation', 'updated_at')
    list_filter = ('status', 'stage', 'needs_re_evaluation', 'is_user_reported')
    search_fields = ('profile__name', 'scheme__code', 'scheme__name', 'application_reference_number')
    readonly_fields = ('created_at', 'updated_at')
