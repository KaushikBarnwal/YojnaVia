from decimal import Decimal
from rest_framework import serializers
from .models import StudentProfile

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

    def validate_age(self, value):
        if value is not None and (value < 5 or value > 120):
            raise serializers.ValidationError("Age must be between 5 and 120 years.")
        return value

    def validate_annual_family_income(self, value):
        if value is not None and (value < Decimal('0') or value > Decimal('100000000')):
            raise serializers.ValidationError("Annual family income must be non-negative and under ₹10 Crore.")
        return value

    def validate_parent_land_acres(self, value):
        if value is not None and (value < Decimal('0') or value > Decimal('5000')):
            raise serializers.ValidationError("Land holding must be a non-negative number of acres.")
        return value

    def validate_previous_year_percentage(self, value):
        if value is not None and (value < Decimal('0') or value > Decimal('100')):
            raise serializers.ValidationError("Percentage must be between 0.00 and 100.00.")
        return value

    def validate_name(self, value):
        if value:
            cleaned = value.strip().replace("<", "").replace(">", "")
            return cleaned[:100] if cleaned else "Student"
        return value
