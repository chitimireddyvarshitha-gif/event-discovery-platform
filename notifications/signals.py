from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from tickets.models import Ticket
from .models import Notification


@receiver(post_save, sender=Ticket)
def send_ticket_confirmation(sender, instance, created, **kwargs):
    """Notify user via in-app notification and email when a ticket is issued."""
    if not created:
        return

    registration = instance.registration
    user = registration.user
    event = registration.event

    title = f"Ticket Confirmed: {event.event_name}"
    event_date = event.date
    if hasattr(event_date, 'strftime'):
        date_str = event_date.strftime('%B %d, %Y at %I:%M %p')
    else:
        date_str = str(event_date)

    message = (
        f"Your registration is confirmed! Your ticket pass (Code: {instance.ticket_code}) "
        f"has been successfully issued for {event.event_name}.\n\n"
        f"Event details:\n"
        f"Date & Time: {date_str}\n"
        f"Venue: {event.venue}\n"
        f"Ticket Type: {instance.get_ticket_type_display()}\n\n"
        f"You can view your ticket inside your Ticket Pass Dashboard."
    )

    # 1. Create in-app notification
    Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    # 2. Dispatch email notification
    if user.email:
        email_subject = f"Your Ticket is Ready: {event.event_name}"
        email_body = (
            f"Hi {user.full_name or user.username},\n\n"
            f"{message}\n\n"
            f"Thank you for using EventHub!\n"
            f"EventHub Team"
        )
        try:
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=getattr(settings, 'EMAIL_FROM_USER', 'no-reply@eventhub.com'),
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            pass
