# app/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from app.models import MaintenanceSchedule
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Sends maintenance reminders to vehicle owners'

    def handle(self, *args, **options):
        today = date.today()
        for schedule in MaintenanceSchedule.objects.all():
            reminders = []
            if schedule.oil_change_date - today <= timedelta(days=30):
                reminders.append("Oil change")
            if schedule.tire_change_date - today <= timedelta(days=30):
                reminders.append("Tire change")
            if schedule.or_cr_renewal_date - today <= timedelta(days=30):
                reminders.append("OR/CR renewal")
            if schedule.sprocket_change_date - today <= timedelta(days=30):
                reminders.append("Sprocket change")

            if reminders:
                subject = "Vehicle Maintenance Reminders"
                message = f"Your {schedule.vehicle.make} {schedule.vehicle.model} is due for: {', '.join(reminders)}"
                from_email = "noreply@example.com"
                recipient_list = [schedule.vehicle.owner.email]
                send_mail(subject, message, from_email, recipient_list)

        self.stdout.write(self.style.SUCCESS('Successfully sent reminders'))