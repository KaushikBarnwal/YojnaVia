from django.core.management.base import BaseCommand
from apps.notifications.services import NotificationDispatchService


class Command(BaseCommand):
    help = "Scan tracked applications and trigger scheduled WhatsApp, SMS and In-App reminders for approaching deadlines, missing documents, inactivity, grievance resubmission, and annual renewals."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting YojnaVia Scheduled Reminder Scan..."))
        result = NotificationDispatchService.scan_and_generate_reminders()

        self.stdout.write(self.style.SUCCESS(
            f"Scan Complete!\n"
            f"  Applications Scanned: {result['scanned_applications']}\n"
            f"  Notifications Generated: {result['generated_notifications']}\n"
            f"  Suppressed / Opted Out: {result['suppressed_or_opted_out']}\n"
            f"  Timestamp: {result['timestamp']}"
        ))
