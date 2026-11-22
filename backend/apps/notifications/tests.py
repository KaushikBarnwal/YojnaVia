import hmac
import hashlib
import json
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme
from apps.tracker.models import ApplicationRecord
from apps.notifications.models import NotificationPreference, NotificationLog
from apps.notifications.templates import render_template, NOTIFICATION_TEMPLATES
from apps.notifications.services import NotificationDispatchService
from apps.notifications.providers.whatsapp import WhatsAppWebhookHandler, MetaWhatsAppCloudProvider
from apps.notifications.providers.sms import DLTCompliantSMSInterface


class NotificationSystemTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = StudentProfile.objects.create(
            session_token="test-session-notif-101",
            name="Aarav Sharma",
            caste_category="OBC",
            annual_family_income=120000.00
        )
        self.scheme = Scheme.objects.create(
            code="TEST_SCHEME_01",
            name="Post Matric Scholarship Test",
            portal_name="MahaDBT",
            application_deadline=date.today() + timedelta(days=2)
        )
        self.pref = NotificationPreference.objects.create(
            profile=self.profile,
            mobile_number="+919876543210",
            is_mobile_verified=True,
            whatsapp_enabled=True,
            sms_enabled=True,
            in_app_enabled=True,
            preferred_language='en'
        )

    def test_trilingual_template_rendering(self):
        """Ensure all 6 canonical events render properly in English, Marathi, and Hindi."""
        ctx = {
            "student_name": "Aarav",
            "scheme_name": "Post Matric",
            "portal_name": "MahaDBT",
            "deadline": "25 November 2026",
            "days_left": 2,
            "document_name": "Income Certificate",
            "sla_days": 15,
            "status": "Documents Pending",
            "resubmission_deadline": "05 December 2026",
            "academic_year": "2026-27",
            "channel": "WhatsApp"
        }

        for event in NOTIFICATION_TEMPLATES:
            for lang in ('en', 'mr', 'hi'):
                rendered = render_template(event, lang, ctx)
                self.assertIn("title", rendered)
                self.assertIn("body", rendered)
                self.assertTrue(len(rendered["body"]) > 10, f"Template {event} ({lang}) generated empty body")

    def test_idempotency_prevents_duplicate_messages(self):
        """Calling send_notification twice with identical key must suppress second dispatch."""
        key = f"test_idempotency_{self.profile.id}_event"
        ctx = {"student_name": "Aarav", "channel": "WhatsApp"}

        # First call
        log1 = NotificationDispatchService.send_notification(
            profile=self.profile,
            event_type="TEST_DEMO",
            channel="WHATSAPP",
            context=ctx,
            idempotency_key=key
        )
        self.assertEqual(log1.idempotency_key, key)
        self.assertIn(log1.delivery_status, ("SENT", "DELIVERED", "SIMULATED"))

        # Second call with same idempotency key
        log2 = NotificationDispatchService.send_notification(
            profile=self.profile,
            event_type="TEST_DEMO",
            channel="WHATSAPP",
            context=ctx,
            idempotency_key=key
        )

        # Must return the identical log record without creating duplicates
        self.assertEqual(log1.id, log2.id)
        self.assertEqual(NotificationLog.objects.filter(idempotency_key=key).count(), 1)

    def test_opt_out_enforcement_and_suppression(self):
        """When citizen opts out of SMS or WhatsApp, notifications must be suppressed with OPTED_OUT status."""
        self.pref.sms_enabled = False
        self.pref.opt_out_sms()
        self.pref.refresh_from_db()
        self.assertFalse(self.pref.sms_enabled)
        self.assertIsNotNone(self.pref.sms_opt_out_at)

        key = f"sms_optout_test_{self.profile.id}"
        log = NotificationDispatchService.send_notification(
            profile=self.profile,
            event_type="DEADLINE_APPROACHING",
            channel="SMS",
            context={"student_name": "Aarav", "scheme_name": "Scholarship", "deadline": "Tomorrow", "days_left": 1, "portal_name": "MahaDBT"},
            idempotency_key=key
        )

        self.assertEqual(log.delivery_status, "OPTED_OUT")
        self.assertEqual(log.provider, "NONE")
        self.assertIn("Suppressed", log.title)

    def test_mobile_unverified_suppresses_dispatch(self):
        """Unverified mobile number must suppress dispatch to WhatsApp and SMS."""
        self.pref.is_mobile_verified = False
        self.pref.save()

        key = f"unverified_test_{self.profile.id}"
        log = NotificationDispatchService.send_notification(
            profile=self.profile,
            event_type="TEST_DEMO",
            channel="WHATSAPP",
            context={"student_name": "Aarav", "channel": "WhatsApp"},
            idempotency_key=key
        )

        self.assertEqual(log.delivery_status, "OPTED_OUT")

    def test_phone_number_serializer_validation(self):
        """Serializer must enforce 10-digit Indian mobile number format with +91 prefix."""
        from apps.notifications.serializers import NotificationPreferenceSerializer

        # Valid 10-digit number
        ser1 = NotificationPreferenceSerializer(self.pref, data={"mobile_number": "9876543210"}, partial=True)
        self.assertTrue(ser1.is_valid(), ser1.errors)
        self.assertEqual(ser1.validated_data["mobile_number"], "+919876543210")

        # Valid +91 number
        ser2 = NotificationPreferenceSerializer(self.pref, data={"mobile_number": "+919123456789"}, partial=True)
        self.assertTrue(ser2.is_valid(), ser2.errors)
        self.assertEqual(ser2.validated_data["mobile_number"], "+919123456789")

        # Invalid number (too short / starts with 1)
        ser3 = NotificationPreferenceSerializer(self.pref, data={"mobile_number": "12345"}, partial=True)
        self.assertFalse(ser3.is_valid())
        self.assertIn("mobile_number", ser3.errors)

    def test_webhook_signature_verification(self):
        """Webhook handler must validate Meta HMAC-SHA256 signatures."""
        secret = "meta_test_secret_key_123"
        payload = b'{"object": "whatsapp_business_account", "entry": []}'

        # Compute valid HMAC signature
        expected_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        self.assertTrue(WhatsAppWebhookHandler.verify_signature(payload, expected_sig, secret))

        # Tampered signature
        bad_sig = "sha256=abcdef1234567890badsignature"
        self.assertFalse(WhatsAppWebhookHandler.verify_signature(payload, bad_sig, secret))

    def test_webhook_status_processing(self):
        """Webhook handler must update NotificationLog delivery status to DELIVERED or READ."""
        # Create a notification log with a known provider message ID
        log = NotificationLog.objects.create(
            profile=self.profile,
            event_type="TEST_DEMO",
            channel="WHATSAPP",
            idempotency_key="webhook_test_log_01",
            recipient="+919876543210",
            language="en",
            template_name="TEST_DEMO",
            title="Test",
            message_body="Test message",
            provider="META_WHATSAPP",
            provider_message_id="wamid_test_123456789",
            delivery_status="SENT"
        )

        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "wamid_test_123456789",
                                        "status": "delivered",
                                        "timestamp": "1732260000"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        res = WhatsAppWebhookHandler.process_event(webhook_payload)
        self.assertEqual(res["updated_count"], 1)

        log.refresh_from_db()
        self.assertEqual(log.delivery_status, "DELIVERED")
        self.assertIsNotNone(log.delivered_at)

    def test_scheduled_reminder_scanner(self):
        """Scanner must detect the 2-day scheme deadline and generate a reminder."""
        ApplicationRecord.objects.create(
            profile=self.profile,
            scheme=self.scheme,
            status="NOT_STARTED",
            stage="DISCOVERED"
        )

        result = NotificationDispatchService.scan_and_generate_reminders()
        self.assertGreaterEqual(result["scanned_applications"], 1)
        self.assertGreaterEqual(result["generated_notifications"], 1)

        # Check that a DEADLINE_APPROACHING log was recorded
        logs = NotificationLog.objects.filter(profile=self.profile, event_type="DEADLINE_APPROACHING")
        self.assertTrue(logs.exists())

    def test_api_preferences_endpoint(self):
        """GET and PUT on /api/v1/notifications/preferences/ must read and update settings."""
        # GET
        url = f"/api/v1/notifications/preferences/?session_token={self.profile.session_token}"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["preferences"]["preferred_language"], "en")

        # PUT to change language and opt out of SMS
        put_url = "/api/v1/notifications/preferences/"
        res_put = self.client.put(put_url, {
            "session_token": self.profile.session_token,
            "preferences": {
                "preferred_language": "mr",
                "sms_enabled": False
            }
        }, format='json')
        self.assertEqual(res_put.status_code, 200)
        self.assertEqual(res_put.data["preferences"]["preferred_language"], "mr")
        self.assertFalse(res_put.data["preferences"]["sms_enabled"])

    def test_api_verify_mobile_flow(self):
        """OTP send and verify flow must validate phone and mark it verified."""
        url = "/api/v1/notifications/verify_mobile/"
        
        # 1. Send OTP
        res1 = self.client.post(url, {
            "session_token": self.profile.session_token,
            "action": "send_otp",
            "mobile_number": "9822012345"
        }, format='json')
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.data["success"])
        demo_otp = res1.data["demo_code"]

        # 2. Verify with wrong OTP
        res_wrong = self.client.post(url, {
            "session_token": self.profile.session_token,
            "action": "verify_otp",
            "code": "000000"
        }, format='json')
        self.assertEqual(res_wrong.status_code, 400)

        # 3. Verify with correct OTP
        res_ok = self.client.post(url, {
            "session_token": self.profile.session_token,
            "action": "verify_otp",
            "code": demo_otp
        }, format='json')
        self.assertEqual(res_ok.status_code, 200)
        self.assertTrue(res_ok.data["is_mobile_verified"])

    def test_api_trigger_test_reminder(self):
        """Citizen 1-click test button must return success and notification log."""
        url = "/api/v1/notifications/trigger_test/"
        res = self.client.post(url, {
            "session_token": self.profile.session_token,
            "channel": "WHATSAPP"
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["notification"]["event_type"], "TEST_DEMO")

    def test_api_admin_delivery_console(self):
        """Admin console endpoint must return summary metrics, gateways, and recent logs."""
        url = "/api/v1/notifications/admin/delivery_console/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn("summary", res.data)
        self.assertIn("gateways", res.data)
        self.assertIn("recent_logs", res.data)
