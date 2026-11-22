import hashlib
import hmac
import secrets
import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.citizens.models import Application, UserProfile
from apps.citizens.serializers import (
    ApplicationCreateSerializer,
    ApplicationSerializer,
    ProfileSerializer,
    RequiredDocumentSerializer,
    SchemeDetailSerializer,
    SchemeSummarySerializer,
)
from apps.schemes.models import Scheme

TOKEN_HEADER = 'HTTP_X_PROFILE_TOKEN'
APPLICATION_WRITABLE_FIELDS = ('status', 'reference_note', 'notes', 'submitted_on')


def hash_token(raw_token):
    return hashlib.sha256(raw_token.encode()).hexdigest()


def require_token(request, profile):
    """Raise the same 404 for a missing, wrong or unknown token."""
    raw_token = request.META.get(TOKEN_HEADER, '')
    if not raw_token or not hmac.compare_digest(profile.owner_token_hash, hash_token(raw_token)):
        raise Http404


def get_owned_profile(request, profile_ref):
    profile = UserProfile.objects.filter(id=profile_ref).first()
    if profile is None:
        raise Http404
    require_token(request, profile)
    return profile


def run_model_clean(instance):
    try:
        instance.clean()
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages)


class SchemeListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        schemes = Scheme.objects.filter(is_active=True)
        params = request.query_params
        for field in ('category', 'jurisdiction', 'state'):
            value = params.get(field)
            if value:
                schemes = schemes.filter(**{field: value})
        if params.get('include_sample', 'true').lower() in ('false', '0', 'no'):
            schemes = schemes.exclude(is_sample=True)
        return Response({'schemes': SchemeSummarySerializer(schemes, many=True).data})


class SchemeDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        scheme = get_object_or_404(Scheme, code=code, is_active=True)
        return Response(SchemeDetailSerializer(scheme).data)


class SchemeDocumentsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        scheme = get_object_or_404(Scheme, code=code, is_active=True)
        documents = scheme.required_documents.order_by('sort_order')
        return Response({
            'scheme_code': scheme.code,
            'is_sample': scheme.is_sample,
            'required_documents': RequiredDocumentSerializer(documents, many=True).data,
        })


class ProfileCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_token = secrets.token_urlsafe(32)
        profile = serializer.save(owner_token_hash=hash_token(raw_token))
        data = ProfileSerializer(profile).data
        data['owner_token'] = raw_token
        return Response(data, status=201)


class ProfileDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, profile_ref):
        profile = get_owned_profile(request, profile_ref)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request, profile_ref):
        profile = get_owned_profile(request, profile_ref)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(profile).data)


class ApplicationCreateListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        raw_ref = request.query_params.get('profile_ref')
        if not raw_ref:
            raise serializers.ValidationError({'profile_ref': 'This query parameter is required.'})
        try:
            profile_ref = uuid.UUID(raw_ref)
        except ValueError:
            raise Http404
        profile = get_owned_profile(request, profile_ref)
        applications = profile.applications.select_related('scheme')
        return Response({'applications': ApplicationSerializer(applications, many=True).data})

    def post(self, request):
        serializer = ApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        profile = get_owned_profile(request, data['profile_ref'])
        scheme = data['scheme']
        if Application.objects.filter(profile=profile, scheme=scheme).exists():
            raise serializers.ValidationError('An application for this scheme already exists.')

        fields = {key: data[key] for key in APPLICATION_WRITABLE_FIELDS if key in data}
        fields.setdefault('status', 'NOT_STARTED')
        application = Application(profile=profile, scheme=scheme, **fields)
        run_model_clean(application)
        application.save()
        return Response(ApplicationSerializer(application).data, status=201)


class ApplicationDetailView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, application_ref):
        application = get_object_or_404(
            Application.objects.select_related('scheme', 'profile'),
            id=application_ref,
        )
        require_token(request, application.profile)
        serializer = ApplicationSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for attr, value in serializer.validated_data.items():
            setattr(application, attr, value)
        run_model_clean(application)
        application.save()
        return Response(ApplicationSerializer(application).data)
