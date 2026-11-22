from rest_framework import serializers
from .models import ApplicationRecord
from apps.schemes.serializers import SchemeSerializer

class ApplicationRecordSerializer(serializers.ModelSerializer):
    scheme_code = serializers.CharField(source='scheme.code', read_only=True)
    scheme_name = serializers.CharField(source='scheme.name', read_only=True)
    scheme_benefit = serializers.CharField(source='scheme.benefit_amount_text', read_only=True)
    portal_name = serializers.CharField(source='scheme.portal_name', read_only=True)
    official_portal_url = serializers.CharField(source='scheme.official_portal_url', read_only=True)

    class Meta:
        model = ApplicationRecord
        fields = [
            'id', 'scheme', 'scheme_code', 'scheme_name', 'scheme_benefit',
            'portal_name', 'official_portal_url', 'status', 'stage', 'completed_documents',
            'application_reference_number', 'applied_date', 'submission_mode',
            'is_user_reported', 'needs_re_evaluation', 're_evaluation_reason',
            're_evaluation_notified_at', 'next_immediate_action',
            'next_action_deadline', 'notes', 'created_at', 'updated_at'
        ]
