from rest_framework import serializers
from .models import Scheme
from apps.documents.models import SchemeDocumentRequirement

class SchemeDocumentRequirementSerializer(serializers.ModelSerializer):
    document_code = serializers.CharField(source='document.code')
    document_name = serializers.CharField(source='document.name')
    document_name_marathi = serializers.CharField(source='document.name_marathi')
    issuing_authority = serializers.CharField(source='document.issuing_authority')
    procurement_portal = serializers.CharField(source='document.procurement_portal')
    estimated_sla_days = serializers.IntegerField(source='document.estimated_sla_days')

    class Meta:
        model = SchemeDocumentRequirement
        fields = ['document_code', 'document_name', 'document_name_marathi', 'issuing_authority', 'procurement_portal', 'estimated_sla_days', 'is_mandatory', 'specific_purpose']

class SchemeSerializer(serializers.ModelSerializer):
    document_requirements = SchemeDocumentRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Scheme
        fields = '__all__'
