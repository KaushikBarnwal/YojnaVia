import re
from rest_framework import serializers
from django.utils import timezone
from .models import NotificationPreference, NotificationLog


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'mobile_number',
            'is_mobile_verified',
            'whatsapp_enabled',
            'whatsapp_opt_in_at',
            'whatsapp_opt_out_at',
            'sms_enabled',
            'sms_opt_in_at',
            'sms_opt_out_at',
            'in_app_enabled',
            'preferred_language',
            'notify_deadlines',
            'notify_missing_docs',
            'notify_milestones',
            'notify_inactivity',
            'notify_grievances',
            'notify_renewals',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'is_mobile_verified',
            'whatsapp_opt_in_at',
            'whatsapp_opt_out_at',
            'sms_opt_in_at',
            'sms_opt_out_at',
            'created_at',
            'updated_at',
        ]

    def validate_mobile_number(self, value):
        if not value:
            return ""
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        # Validate format: either 10 digits or starting with +91/91 followed by 10 digits
        if not re.match(r'^(\+91|91)?[6-9]\d{9}$', cleaned):
            raise serializers.ValidationError(
                "Please enter a valid 10-digit Indian mobile number (e.g., +919876543210 or 9876543210)."
            )
        if not cleaned.startswith('+91'):
            if cleaned.startswith('91') and len(cleaned) == 12:
                cleaned = '+' + cleaned
            else:
                cleaned = '+91' + cleaned[-10:]
        return cleaned

    def update(self, instance, validated_data):
        now = timezone.now()

        # Track WhatsApp opt-in / opt-out timestamps
        if 'whatsapp_enabled' in validated_data:
            new_wa = validated_data['whatsapp_enabled']
            if new_wa and not instance.whatsapp_enabled:
                instance.whatsapp_opt_in_at = now
            elif not new_wa and instance.whatsapp_enabled:
                instance.whatsapp_opt_out_at = now

        # Track SMS opt-in / opt-out timestamps
        if 'sms_enabled' in validated_data:
            new_sms = validated_data['sms_enabled']
            if new_sms and not instance.sms_enabled:
                instance.sms_opt_in_at = now
            elif not new_sms and instance.sms_enabled:
                instance.sms_opt_out_at = now

        # If phone number changed, require re-verification
        if 'mobile_number' in validated_data:
            new_phone = validated_data['mobile_number']
            if new_phone != instance.mobile_number:
                instance.is_mobile_verified = False

        return super().update(instance, validated_data)


class NotificationLogSerializer(serializers.ModelSerializer):
    scheme_name = serializers.ReadOnlyField(source='scheme.name')
    scheme_code = serializers.ReadOnlyField(source='scheme.code')

    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'event_type',
            'channel',
            'idempotency_key',
            'recipient',
            'language',
            'template_name',
            'title',
            'message_body',
            'provider',
            'provider_message_id',
            'delivery_status',
            'error_message',
            'retry_count',
            'sent_at',
            'delivered_at',
            'created_at',
            'scheme_name',
            'scheme_code',
        ]
        read_only_fields = fields
