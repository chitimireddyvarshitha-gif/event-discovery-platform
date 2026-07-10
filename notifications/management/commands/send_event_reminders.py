from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from events.models import Event
from registrations.models import Registration
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Send upcoming event reminders (24 hours prior) to registered attendees.'

    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)
        
        # Query events occurring between now and tomorrow (24 hours ahead)
        upcoming_events = Event.objects.filter(date__gte=now, date__lte=tomorrow)
        
        self.stdout.write(f"Checking reminders for {upcoming_events.count()} upcoming events...")
        
        reminder_count = 0
        for event in upcoming_events:
            # Get confirmed registrations
            registrations = Registration.objects.filter(event=event, status='confirmed').select_related('user')
            
            for reg in registrations:
                attendee = reg.user
                reminder_title = f"Reminder: {event.event_name} is tomorrow!"
                
                # Check for existing reminder notification to prevent duplicates
                if Notification.objects.filter(user=attendee, title=reminder_title).exists():
                    continue
                
                message = (
                    f"Hi {attendee.full_name or attendee.username},\n\n"
                    f"This is a friendly reminder that the event \"{event.event_name}\" is happening tomorrow!\n\n"
                    f"Details:\n"
                    f"Date & Time: {event.date.strftime('%B %d, %Y at %I:%M %p')}\n"
                    f"Venue: {event.venue}\n\n"
                    f"Don't forget to have your ticket pass ready. See you there!\n\n"
                    f"Warm regards,\n"
                    f"EventHub Team"
                )
                
                # 1. Dispatch in-app notification
                Notification.objects.create(
                    user=attendee,
                    title=reminder_title,
                    message=message
                )
                
                # 2. Dispatch email
                if attendee.email:
                    try:
                        send_mail(
                            subject=reminder_title,
                            message=message,
                            from_email=getattr(settings, 'EMAIL_FROM_USER', 'no-reply@eventhub.com'),
                            recipient_list=[attendee.email],
                            fail_silently=True
                        )
                    except Exception as e:
                        self.stderr.write(f"Email failed for {attendee.username}: {e}")
                
                reminder_count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Successfully processed and sent {reminder_count} reminders."))
