from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.citizens.views import get_owned_profile
from apps.schemes.models import Scheme

from .evaluator import evaluate_scheme
from .fields import build_facts


class EvaluationInputSerializer(serializers.Serializer):
    profile_ref = serializers.UUIDField()
    scheme_codes = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        allow_empty=True,
        max_length=50,
    )


class EvaluationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = EvaluationInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        profile = get_owned_profile(request, data['profile_ref'])
        facts = build_facts(profile)

        qs = Scheme.objects.filter(is_active=True)
        codes = data.get('scheme_codes')
        if codes:
            found = set(qs.filter(code__in=codes).values_list('code', flat=True))
            missing = [code for code in codes if code not in found]
            if missing:
                raise DRFValidationError(
                    {'scheme_codes': ['Unknown or inactive scheme codes: ' + ', '.join(missing)]}
                )
            qs = qs.filter(code__in=codes)

        results = [
            evaluate_scheme(
                scheme.eligibility_criteria,
                facts,
                {
                    'code': scheme.code,
                    'name': scheme.name,
                    'is_sample': scheme.is_sample,
                    'verification_status': scheme.verification_status,
                    'official_source_url': scheme.official_source_url,
                    'last_verified_on': (
                        scheme.last_verified_on.isoformat() if scheme.last_verified_on else None
                    ),
                },
            )
            for scheme in qs.order_by('code')
        ]
        return Response({'profile_ref': str(profile.id), 'results': results}, status=200)
