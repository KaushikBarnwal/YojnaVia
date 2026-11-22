from rest_framework import serializers
from apps.profiles.serializers import StudentProfileSerializer
from .models import (
    ServiceCenter,
    CounselorUser,
    CitizenCase,
    CitizenConsentRecord,
    CaseAccessAuditLog,
    CounselorCaseNote,
)


class ServiceCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCenter
        fields = [
            'id',
            'code',
            'name',
            'vle_id',
            'center_type',
            'district',
            'taluka',
            'pincode',
            'contact_phone',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields


class CounselorUserSerializer(serializers.ModelSerializer):
    center = ServiceCenterSerializer(read_only=True)

    class Meta:
        model = CounselorUser
        fields = [
            'id',
            'username',
            'name',
            'role',
            'center',
            'phone',
            'email',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields


class CitizenConsentRecordSerializer(serializers.ModelSerializer):
    attesting_counselor_name = serializers.ReadOnlyField(source='attesting_counselor.name')

    class Meta:
        model = CitizenConsentRecord
        fields = [
            'id',
            'consent_status',
            'consent_method',
            'scope_description',
            'granted_at',
            'withdrawn_at',
            'withdrawn_reason',
            'attesting_counselor_name',
        ]
        read_only_fields = ['id', 'granted_at', 'withdrawn_at', 'attesting_counselor_name']


class CounselorCaseNoteSerializer(serializers.ModelSerializer):
    counselor_name = serializers.ReadOnlyField(source='counselor.name')
    counselor_role = serializers.ReadOnlyField(source='counselor.role')

    class Meta:
        model = CounselorCaseNote
        fields = [
            'id',
            'note_type',
            'content',
            'is_pinned',
            'created_at',
            'counselor_name',
            'counselor_role',
        ]
        read_only_fields = ['id', 'created_at', 'counselor_name', 'counselor_role']


class CaseAccessAuditLogSerializer(serializers.ModelSerializer):
    counselor_name = serializers.ReadOnlyField(source='counselor.name')

    class Meta:
        model = CaseAccessAuditLog
        fields = [
            'id',
            'action',
            'details',
            'timestamp',
            'counselor_name',
        ]
        read_only_fields = fields


class CitizenCaseListSerializer(serializers.ModelSerializer):
    assigned_counselor_name = serializers.ReadOnlyField(source='assigned_counselor.name')
    center_code = serializers.ReadOnlyField(source='center.code')
    center_name = serializers.ReadOnlyField(source='center.name')
    consent_status = serializers.ReadOnlyField(source='consent.consent_status')
    notes_count = serializers.IntegerField(source='notes.count', read_only=True)

    class Meta:
        model = CitizenCase
        fields = [
            'id',
            'case_number',
            'citizen_name',
            'citizen_mobile',
            'case_status',
            'priority',
            'target_scheme_category',
            'follow_up_date',
            'escalated_to_supervisor',
            'escalation_reason',
            'assigned_counselor_name',
            'center_code',
            'center_name',
            'consent_status',
            'notes_count',
            'created_at',
            'updated_at',
            'closed_at',
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at', 'closed_at']


class CitizenCaseDetailSerializer(serializers.ModelSerializer):
    assigned_counselor_name = serializers.ReadOnlyField(source='assigned_counselor.name')
    center = ServiceCenterSerializer(read_only=True)
    consent = CitizenConsentRecordSerializer(read_only=True)
    notes = CounselorCaseNoteSerializer(many=True, read_only=True)
    audit_logs = serializers.SerializerMethodField()
    profile = StudentProfileSerializer(read_only=True)

    class Meta:
        model = CitizenCase
        fields = [
            'id',
            'case_number',
            'citizen_name',
            'citizen_mobile',
            'case_status',
            'priority',
            'target_scheme_category',
            'follow_up_date',
            'escalated_to_supervisor',
            'escalation_reason',
            'closure_summary',
            'assigned_counselor_name',
            'center',
            'consent',
            'notes',
            'audit_logs',
            'profile',
            'created_at',
            'updated_at',
            'closed_at',
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at', 'closed_at']

    def get_audit_logs(self, obj):
        # Limit to 15 most recent audit records
        logs = obj.audit_logs.all()[:15]
        return CaseAccessAuditLogSerializer(logs, many=True).data
