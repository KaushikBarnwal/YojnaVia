import re

from django.db import transaction
from rest_framework import serializers

from apps.citizens.models import Application, HouseholdMember, UserProfile
from apps.schemes.models import EligibilityRule, RequiredDocument, Scheme

AADHAAR_RE = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
AADHAAR_MESSAGE = 'Please do not enter identity numbers such as Aadhaar. Remove them and try again.'

SCHEME_SUMMARY_FIELDS = [
    'code', 'name', 'category', 'jurisdiction', 'state', 'department',
    'benefit_type', 'benefit_amount_text', 'brief_description',
    'official_portal_url', 'official_source_url', 'last_verified_on',
    'verification_status', 'application_deadline', 'is_sample',
]

PROFILE_FIELDS = [
    'display_label', 'state', 'district', 'age_years', 'annual_household_income_inr',
    'caste_category', 'is_maharashtra_domicile', 'is_sample',
]

APPLICATION_FIELDS = [
    'application_ref', 'scheme_code', 'scheme_name', 'status',
    'reference_note', 'submitted_on', 'notes', 'updated_at',
]


def check_no_aadhaar(value):
    if value and AADHAAR_RE.search(value):
        raise serializers.ValidationError(AADHAAR_MESSAGE)
    return value


class SchemeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = SCHEME_SUMMARY_FIELDS


class EligibilityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityRule
        fields = ['code', 'description', 'field', 'operator', 'value', 'is_mandatory']


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ['name', 'description', 'is_mandatory']


class SchemeDetailSerializer(serializers.ModelSerializer):
    eligibility_rules = serializers.SerializerMethodField()
    required_documents = serializers.SerializerMethodField()

    class Meta:
        model = Scheme
        fields = SCHEME_SUMMARY_FIELDS + [
            'statutory_gr', 'version', 'effective_academic_year',
            'application_steps', 'eligibility_rules', 'required_documents',
            'eligibility_criteria',
        ]

    def get_eligibility_rules(self, scheme):
        rules = scheme.eligibility_rules.order_by('sort_order')
        return EligibilityRuleSerializer(rules, many=True).data

    def get_required_documents(self, scheme):
        documents = scheme.required_documents.order_by('sort_order')
        return RequiredDocumentSerializer(documents, many=True).data


class HouseholdMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdMember
        fields = ['relation', 'label', 'age', 'is_student', 'annual_income_inr']

    def validate_label(self, value):
        return check_no_aadhaar(value)


class ProfileSerializer(serializers.ModelSerializer):
    profile_ref = serializers.UUIDField(source='id', read_only=True)
    members = HouseholdMemberSerializer(many=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['profile_ref'] + PROFILE_FIELDS + ['members']

    def validate_caste_category(self, value):
        if value and value.upper() == 'OPEN':
            return 'GENERAL'
        return value

    def validate_display_label(self, value):
        return check_no_aadhaar(value)

    def validate_district(self, value):
        return check_no_aadhaar(value)

    def validate_is_sample(self, value):
        if not value:
            raise serializers.ValidationError('Only sample profiles can be stored in Phase 1.')
        return value

    def validate(self, attrs):
        members = attrs.get('members')
        if members:
            self_count = sum(1 for member in members if member.get('relation') == 'SELF')
            if self_count != 1:
                raise serializers.ValidationError(
                    {'members': 'Exactly one household member must have relation SELF.'}
                )
        return attrs

    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        validated_data['is_sample'] = True
        with transaction.atomic():
            profile = UserProfile.objects.create(**validated_data)
            for member in members_data:
                profile.members.create(**member)
        return profile

    def update(self, instance, validated_data):
        members_data = validated_data.pop('members', None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if members_data is not None:
                instance.members.all().delete()
                for member in members_data:
                    instance.members.create(**member)
        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    application_ref = serializers.UUIDField(source='id', read_only=True)
    scheme_code = serializers.CharField(source='scheme.code', read_only=True)
    scheme_name = serializers.CharField(source='scheme.name', read_only=True)

    class Meta:
        model = Application
        fields = APPLICATION_FIELDS
        extra_kwargs = {
            'status': {'required': False},
            'reference_note': {'required': False},
            'submitted_on': {'required': False},
            'notes': {'required': False},
        }

    def validate_reference_note(self, value):
        return check_no_aadhaar(value)

    def validate_notes(self, value):
        return check_no_aadhaar(value)


class ApplicationCreateSerializer(ApplicationSerializer):
    profile_ref = serializers.UUIDField(write_only=True)
    scheme_code = serializers.CharField(write_only=True)

    class Meta(ApplicationSerializer.Meta):
        fields = ['profile_ref', 'scheme_code'] + [
            field for field in APPLICATION_FIELDS if field != 'scheme_code'
        ]

    def validate(self, attrs):
        scheme = Scheme.objects.filter(code=attrs['scheme_code'], is_active=True).first()
        if scheme is None:
            raise serializers.ValidationError({'scheme_code': 'No active scheme with this code.'})
        attrs['scheme'] = scheme
        return attrs
