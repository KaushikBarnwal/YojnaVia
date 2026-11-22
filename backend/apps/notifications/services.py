"""
Notification Dispatch & Scheduled Reminder Service.

Handles:
- Consent verification & opt-out enforcement.
- Idempotency protection to prevent duplicate reminders.
- Trilingual message rendering based on citizen preference.
- Provider selection (Meta WhatsApp Cloud API / Indian DLT SMS / Simulated Demo).
- Automated scanning of tracked applications for deadlines, missing documents,
  inactivity, grievance resubmission, and annual renewals.
"""

from datetime import date, datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone

from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme
from apps.tracker.models import ApplicationRecord
from .models import NotificationPreference, NotificationLog
from .templates import render_template
from .providers.whatsapp import MetaWhatsAppCloudProvider, SimulatedWhatsAppProvider
from .providers.sms import DLTCompliantSMSInterface, SimulatedSMSProvider

logger = logging.getLogger(__name__)


class NotificationDispatchService:

    @classmethod
    def get_or_create_preferences(cls, profile: StudentProfile) -> NotificationPreference:
        """Retrieves or initializes a citizen's notification preferences."""
        pref, _ = NotificationPreference.objects.get_or_create(
            profile=profile,
            defaults={
                "mobile_number": "",
                "is_mobile_verified": False,
                "whatsapp_enabled": False,
                "sms_enabled": False,
                "in_app_enabled": True,
                "preferred_language": "en"
            }
        )
        return pref

    @classmethod
    def send_notification(
        cls,
        profile: StudentProfile,
        event_type: str,
        channel: str,
        context: Dict[str, Any],
        idempotency_key: str,
        application: Optional[ApplicationRecord] = None,
        scheme: Optional[Scheme] = None,
        force_send: bool = False
    ) -> NotificationLog:
        """
        Transmits a single notification with consent checking, idempotency guard,
        and delivery logging.
        """
        pref = cls.get_or_create_preferences(profile)
        channel_upper = channel.upper()

        # 1. Idempotency Check (Prevents duplicate messages)
        existing_log = NotificationLog.objects.filter(idempotency_key=idempotency_key).first()
        if existing_log and not force_send:
            logger.info("Idempotent notification suppressed for key: %s", idempotency_key)
            return existing_log

        # 2. Consent & Verification Enforcement
        if not force_send and not pref.is_channel_permitted(channel_upper):
            logger.info("Channel %s suppressed due to lack of consent/verification for %s", channel_upper, profile.name)
            log = NotificationLog.objects.create(
                profile=profile,
                application=application,
                scheme=scheme,
                event_type=event_type,
                channel=channel_upper,
                idempotency_key=idempotency_key,
                recipient=pref.mobile_number or profile.session_token,
                language=pref.preferred_language,
                template_name=event_type,
                title="Suppressed: No Consent",
                message_body="Delivery skipped because citizen has not opted into this channel.",
                provider="NONE",
                delivery_status="OPTED_OUT"
            )
            return log

        # 3. Render Message in Citizen's Preferred Language
        lang = pref.preferred_language or "en"
        rendered = render_template(event_type, lang, context)

        # 4. Dispatch via Provider Adapter
        recipient_phone = pref.mobile_number
        provider_name = "SIMULATED"
        send_result: Dict[str, Any] = {}

        if channel_upper == "WHATSAPP":
            wa_provider = MetaWhatsAppCloudProvider()
            provider_name = "META_WHATSAPP" if wa_provider.is_configured else "SIMULATED_WHATSAPP"
            send_result = wa_provider.send(
                recipient=recipient_phone,
                title=rendered["title"],
                body=rendered["body"],
                template_name=event_type,
                context=context,
                language=lang
            )
        elif channel_upper == "SMS":
            sms_provider = DLTCompliantSMSInterface()
            provider_name = "INDIAN_SMS_GATEWAY" if sms_provider.is_production_ready else "SIMULATED_SMS"
            send_result = sms_provider.send(
                recipient=recipient_phone,
                title=rendered["title"],
                body=rendered["body"],
                template_name=event_type,
                context=context,
                language=lang
            )
        else:  # IN_APP
            provider_name = "INTERNAL_IN_APP"
            send_result = {
                "success": True,
                "provider_message_id": f"inapp_{int(timezone.now().timestamp())}",
                "status": "DELIVERED",
                "raw_response": {"delivered_to": profile.session_token},
                "is_simulated": False
            }

        status = send_result.get("status", "SENT")
        now = timezone.now()

        # 5. Persist Immutable Notification Delivery History
        log = NotificationLog.objects.create(
            profile=profile,
            application=application,
            scheme=scheme,
            event_type=event_type,
            channel=channel_upper,
            idempotency_key=idempotency_key,
            recipient=recipient_phone or profile.session_token,
            language=lang,
            template_name=event_type,
            title=rendered["title"],
            message_body=rendered["body"],
            provider=provider_name,
            provider_message_id=send_result.get("provider_message_id", ""),
            provider_response_raw=send_result.get("raw_response", {}),
            delivery_status=status,
            error_message=send_result.get("error_message", ""),
            sent_at=now,
            delivered_at=now if status in ("DELIVERED", "SIMULATED") else None
        )

        return log

    @classmethod
    def trigger_test_reminder(cls, profile: StudentProfile, channel: str = "WHATSAPP") -> NotificationLog:
        """Generates an immediate test ping for verifying connectivity and preferences."""
        pref = cls.get_or_create_preferences(profile)
        context = {
            "student_name": profile.name,
            "channel": channel.capitalize(),
        }
        test_key = f"test:{profile.id}:{channel}:{int(timezone.now().timestamp())}"
        return cls.send_notification(
            profile=profile,
            event_type="TEST_DEMO",
            channel=channel,
            context=context,
            idempotency_key=test_key,
            force_send=True
        )

    @classmethod
    def scan_and_generate_reminders(cls) -> Dict[str, Any]:
        """
        Background evaluation job: Scans all active ApplicationRecord instances
        and generates reminders only from verified scheme records and citizen-reported milestones.
        """
        today = date.today()
        current_year = today.year
        apps = ApplicationRecord.objects.select_related("profile", "scheme").all()
        generated_count = 0
        suppressed_count = 0

        for app in apps:
            profile = app.profile
            pref = cls.get_or_create_preferences(profile)
            channels_to_evaluate = []
            if pref.whatsapp_enabled:
                channels_to_evaluate.append("WHATSAPP")
            if pref.sms_enabled:
                channels_to_evaluate.append("SMS")
            if pref.in_app_enabled:
                channels_to_evaluate.append("IN_APP")

            if not channels_to_evaluate:
                continue

            scheme = app.scheme

            # EVENT 1: Scheme Application Deadline Approaching
            if scheme.application_deadline:
                days_left = (scheme.application_deadline - today).days
                if days_left in (7, 2, 0):
                    for ch in channels_to_evaluate:
                        key = f"deadline:{profile.id}:{scheme.code}:{scheme.application_deadline.isoformat()}:{days_left}d:{ch}"
                        ctx = {
                            "student_name": profile.name,
                            "scheme_name": scheme.name,
                            "portal_name": scheme.portal_name,
                            "deadline": scheme.application_deadline.strftime("%d %B %Y"),
                            "days_left": days_left
                        }
                        log = cls.send_notification(
                            profile=profile,
                            event_type="DEADLINE_APPROACHING",
                            channel=ch,
                            context=ctx,
                            idempotency_key=key,
                            application=app,
                            scheme=scheme
                        )
                        if log.delivery_status in ("SENT", "DELIVERED", "SIMULATED"):
                            generated_count += 1
                        else:
                            suppressed_count += 1

            # EVENT 2: Missing Document Still Pending
            if app.status in ("DOCUMENTS_PENDING", "NOT_STARTED"):
                # Check which required documents are missing
                required_docs = scheme.document_requirements.select_related("document").all()
                completed = set(app.completed_documents or [])
                missing = [dr.document for dr in required_docs if dr.document.code not in completed]
                if missing:
                    top_missing = missing[0]
                    # Reminder sent at most once per calendar week
                    current_week = today.strftime("%Y-W%U")
                    for ch in channels_to_evaluate:
                        key = f"missing_doc:{profile.id}:{scheme.code}:{top_missing.code}:{current_week}:{ch}"
                        ctx = {
                            "student_name": profile.name,
                            "scheme_name": scheme.name,
                            "document_name": top_missing.name,
                            "sla_days": top_missing.estimated_sla_days or 15
                        }
                        log = cls.send_notification(
                            profile=profile,
                            event_type="MISSING_DOCUMENT_REMINDER",
                            channel=ch,
                            context=ctx,
                            idempotency_key=key,
                            application=app,
                            scheme=scheme
                        )
                        if log.delivery_status in ("SENT", "DELIVERED", "SIMULATED"):
                            generated_count += 1
                        else:
                            suppressed_count += 1

            # EVENT 3: Citizen-Reported Status Has Not Changed For 14 Days
            if app.updated_at:
                days_since_update = (timezone.now() - app.updated_at).days
                if days_since_update >= 14 and app.status not in ("APPROVED", "REJECTED"):
                    fortnight_bucket = days_since_update // 14
                    for ch in channels_to_evaluate:
                        key = f"inactivity:{profile.id}:{scheme.code}:{fortnight_bucket}:{ch}"
                        ctx = {
                            "student_name": profile.name,
                            "scheme_name": scheme.name,
                            "status": app.get_status_display()
                        }
                        log = cls.send_notification(
                            profile=profile,
                            event_type="STATUS_INACTIVITY",
                            channel=ch,
                            context=ctx,
                            idempotency_key=key,
                            application=app,
                            scheme=scheme
                        )
                        if log.delivery_status in ("SENT", "DELIVERED", "SIMULATED"):
                            generated_count += 1
                        else:
                            suppressed_count += 1

            # EVENT 4: 15-Day Scrutiny Resubmission Clock
            if app.status in ("REJECTED", "UNDER_REVIEW"):
                # Resubmission window is active within 15 days of last update
                days_since = (timezone.now() - app.updated_at).days if app.updated_at else 0
                days_remaining = max(0, 15 - days_since)
                if days_remaining in (10, 5, 2, 1):
                    resub_deadline = (today + timedelta(days=days_remaining)).strftime("%d %B %Y")
                    for ch in channels_to_evaluate:
                        key = f"grievance_resub:{profile.id}:{scheme.code}:{days_remaining}d:{ch}"
                        ctx = {
                            "student_name": profile.name,
                            "scheme_name": scheme.name,
                            "resubmission_deadline": resub_deadline
                        }
                        log = cls.send_notification(
                            profile=profile,
                            event_type="GRIEVANCE_RESUBMISSION",
                            channel=ch,
                            context=ctx,
                            idempotency_key=key,
                            application=app,
                            scheme=scheme
                        )
                        if log.delivery_status in ("SENT", "DELIVERED", "SIMULATED"):
                            generated_count += 1
                        else:
                            suppressed_count += 1

            # EVENT 5: Annual Academic & March 31 Income Renewal
            # Triggered in February and March (within 45 days of March 31)
            if today.month in (2, 3):
                march_31 = date(current_year, 3, 31)
                days_to_march_31 = (march_31 - today).days
                if days_to_march_31 in (30, 15, 5):
                    for ch in channels_to_evaluate:
                        key = f"annual_renewal:{profile.id}:{current_year}:{days_to_march_31}d:{ch}"
                        ctx = {
                            "student_name": profile.name,
                            "academic_year": f"{current_year}-{str(current_year + 1)[-2:]}"
                        }
                        log = cls.send_notification(
                            profile=profile,
                            event_type="ANNUAL_RENEWAL",
                            channel=ch,
                            context=ctx,
                            idempotency_key=key,
                            application=app,
                            scheme=scheme
                        )
                        if log.delivery_status in ("SENT", "DELIVERED", "SIMULATED"):
                            generated_count += 1
                        else:
                            suppressed_count += 1

        return {
            "scanned_applications": apps.count(),
            "generated_notifications": generated_count,
            "suppressed_or_opted_out": suppressed_count,
            "timestamp": timezone.now().isoformat()
        }
