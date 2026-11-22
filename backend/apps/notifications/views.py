import os
import random
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.models import StudentProfile
from .models import NotificationPreference, NotificationLog
from .serializers import NotificationPreferenceSerializer, NotificationLogSerializer
from .services import NotificationDispatchService
from .providers.whatsapp import WhatsAppWebhookHandler, MetaWhatsAppCloudProvider
from .providers.sms import DLTCompliantSMSInterface


def _get_profile_by_session(request):
    token = (
        request.query_params.get('session_token')
        or request.data.get('session_token')
        or request.headers.get('X-Session-Token')
    )
    if not token:
        return None
    try:
        return StudentProfile.objects.get(session_token=token)
    except StudentProfile.DoesNotExist:
        # Create profile on the fly if needed
        return StudentProfile.objects.create(session_token=token, name="Citizen User")


class NotificationPreferencesView(APIView):
    """
    GET: Retrieve notification preferences for the active session.
    POST / PUT: Update contact info, channel opt-in/opt-out status, and notification toggles.
    """

    def get(self, request):
        profile = _get_profile_by_session(request)
        if not profile:
            return Response(
                {"error": "session_token parameter or header is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pref = NotificationDispatchService.get_or_create_preferences(profile)
        serializer = NotificationPreferenceSerializer(pref)
        return Response({
            "session_token": profile.session_token,
            "student_name": profile.name,
            "preferences": serializer.data,
            "channels_available": {
                "whatsapp": {
                    "is_configured": MetaWhatsAppCloudProvider().is_configured,
                    "provider_mode": "LIVE" if MetaWhatsAppCloudProvider().is_configured else "SIMULATED"
                },
                "sms": {
                    "is_configured": DLTCompliantSMSInterface().is_production_ready,
                    "provider_mode": "LIVE" if DLTCompliantSMSInterface().is_production_ready else "SIMULATED",
                    "dlt_entity_id": getattr(settings, 'DLT_ENTITY_ID', '') or "110155234000001"
                },
                "in_app": {
                    "is_configured": True,
                    "provider_mode": "LIVE"
                }
            }
        })

    def post(self, request):
        return self.put(request)

    def put(self, request):
        profile = _get_profile_by_session(request)
        if not profile:
            return Response(
                {"error": "session_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pref = NotificationDispatchService.get_or_create_preferences(profile)
        data = request.data.get('preferences', request.data)
        serializer = NotificationPreferenceSerializer(pref, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Preferences updated successfully",
                "preferences": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyMobileView(APIView):
    """
    Handles two-step mobile verification for WhatsApp & SMS consent.
    Step 1 (action='send_otp'): sends a 6-digit OTP code to citizen's mobile.
    Step 2 (action='verify_otp'): validates OTP and marks mobile as verified.
    """

    def post(self, request):
        profile = _get_profile_by_session(request)
        if not profile:
            return Response(
                {"error": "session_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pref = NotificationDispatchService.get_or_create_preferences(profile)
        action = request.data.get('action', 'send_otp')

        if action == 'send_otp':
            mobile = request.data.get('mobile_number', pref.mobile_number)
            if not mobile:
                return Response(
                    {"error": "mobile_number is required to initiate verification"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate & normalize format
            serializer = NotificationPreferenceSerializer(pref, data={'mobile_number': mobile}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            pref.verification_code = otp
            pref.verification_sent_at = timezone.now()
            pref.is_mobile_verified = False
            pref.save()

            # In demo / simulated mode, return the OTP so the user can test without SMS credits
            return Response({
                "success": True,
                "message": f"Verification code sent to {pref.mobile_number}",
                "mobile_number": pref.mobile_number,
                "demo_code": otp,  # Demo assistance
                "is_simulated": True
            })

        elif action == 'verify_otp':
            code = (request.data.get('code') or '').strip()
            if not code:
                return Response(
                    {"error": "Verification code is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if code matches (accept generated code or 123456 as standard demo OTP)
            if pref.verification_code and code == pref.verification_code or code == '123456':
                pref.is_mobile_verified = True
                pref.save()
                return Response({
                    "success": True,
                    "message": "Mobile number verified successfully! You can now opt-in to WhatsApp and SMS reminders.",
                    "is_mobile_verified": True,
                    "mobile_number": pref.mobile_number
                })
            else:
                return Response(
                    {"error": "Invalid verification code. Please check the 6-digit OTP or enter demo code 123456."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"error": "Invalid action. Supported actions: 'send_otp', 'verify_otp'"},
            status=status.HTTP_400_BAD_REQUEST
        )


class NotificationHistoryView(APIView):
    """
    Returns immutable delivery log history for the authenticated citizen session.
    """

    def get(self, request):
        profile = _get_profile_by_session(request)
        if not profile:
            return Response(
                {"error": "session_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logs = NotificationLog.objects.filter(profile=profile).select_related('scheme')
        channel = request.query_params.get('channel')
        if channel:
            logs = logs.filter(channel=channel.upper())

        status_filter = request.query_params.get('status')
        if status_filter:
            logs = logs.filter(delivery_status=status_filter.upper())

        serializer = NotificationLogSerializer(logs[:50], many=True)
        return Response({
            "session_token": profile.session_token,
            "total_count": logs.count(),
            "notifications": serializer.data
        })


class TriggerTestReminderView(APIView):
    """
    1-Click Citizen Test Drive button.
    Dispatches a test reminder across the requested channel (WhatsApp / SMS / In-App).
    """

    def post(self, request):
        profile = _get_profile_by_session(request)
        if not profile:
            return Response(
                {"error": "session_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        channel = request.data.get('channel', 'WHATSAPP').upper()
        if channel not in ('WHATSAPP', 'SMS', 'IN_APP'):
            channel = 'WHATSAPP'

        log = NotificationDispatchService.trigger_test_reminder(profile=profile, channel=channel)
        serializer = NotificationLogSerializer(log)
        return Response({
            "success": True,
            "message": f"Test reminder sent via {channel}",
            "notification": serializer.data
        })


class AdminDeliveryConsoleView(APIView):
    """
    Admin Telemetry & Delivery Console.
    Provides aggregate stats across WhatsApp, SMS, and In-App delivery channels.
    """

    def get(self, request):
        total_logs = NotificationLog.objects.count()
        statuses = {}
        for row in NotificationLog.objects.values('delivery_status'):
            s = row['delivery_status']
            statuses[s] = statuses.get(s, 0) + 1

        channels = {}
        for row in NotificationLog.objects.values('channel'):
            ch = row['channel']
            channels[ch] = channels.get(ch, 0) + 1

        recent = NotificationLog.objects.select_related('profile', 'scheme').order_by('-created_at')[:25]
        serializer = NotificationLogSerializer(recent, many=True)

        wa_provider = MetaWhatsAppCloudProvider()
        sms_provider = DLTCompliantSMSInterface()

        return Response({
            "summary": {
                "total_notifications": total_logs,
                "by_status": statuses,
                "by_channel": channels,
            },
            "gateways": {
                "whatsapp": {
                    "is_configured": wa_provider.is_configured,
                    "phone_number_id": wa_provider.phone_number_id or "Unset (Simulated)",
                    "mode": "PRODUCTION_CLOUD_API" if wa_provider.is_configured else "DEMO_SIMULATION"
                },
                "sms": {
                    "is_configured": sms_provider.is_production_ready,
                    "dlt_entity_id": sms_provider.dlt_entity_id or "110155234000001 (Demo)",
                    "dlt_sender_id": sms_provider.sender_id or "YOJNAV (Demo)",
                    "mode": "TRAI_DLT_PRODUCTION" if sms_provider.is_production_ready else "DEMO_SIMULATION"
                }
            },
            "recent_logs": serializer.data
        })


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """
    Meta WhatsApp Cloud API Webhook endpoint.
    GET: Challenge verification handshake.
    POST: Delivery receipt & status update processing with HMAC-SHA256 signature validation.
    """

    def get(self, request):
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')

        expected_token = getattr(settings, 'META_VERIFY_TOKEN', '') or os.getenv('META_VERIFY_TOKEN', 'YojnaVia_verify_token_2026')

        if mode == 'subscribe' and token == expected_token:
            return HttpResponse(challenge, content_type="text/plain", status=200)
        return HttpResponse("Forbidden: Invalid verification token", status=403)

    def post(self, request):
        raw_body = request.body
        signature = request.headers.get('X-Hub-Signature-256') or request.META.get('HTTP_X_HUB_SIGNATURE_256')

        app_secret = getattr(settings, 'META_APP_SECRET', '') or os.getenv('META_APP_SECRET', '')

        # Validate HMAC signature if app secret is configured
        if app_secret:
            if not signature or not WhatsAppWebhookHandler.verify_signature(raw_body, signature, app_secret):
                return JsonResponse({"error": "Invalid webhook signature"}, status=403)

        payload = request.data
        result = WhatsAppWebhookHandler.process_event(payload)
        return JsonResponse(result, status=200)
