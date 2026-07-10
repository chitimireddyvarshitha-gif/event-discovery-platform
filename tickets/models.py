import copy

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from registrations.models import Registration


class Ticket(models.Model):
    """Represents a ticket issued for a confirmed registration."""

    class TicketType(models.TextChoices):
        GENERAL = 'general', 'General'
        VIP = 'vip', 'VIP'
        PREMIUM = 'premium', 'Premium'

    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='ticket')
    ticket_code = models.CharField(max_length=50, unique=True)
    ticket_number = models.CharField(max_length=30, unique=True, blank=True)
    ticket_type = models.CharField(max_length=20, choices=TicketType.choices, default=TicketType.GENERAL)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return self.ticket_code


@receiver(post_save, sender=Registration)
def create_ticket_for_registration(sender, instance, created, **kwargs):
    """Create a ticket only when a registration is confirmed."""
    if instance.status == 'confirmed':
        if not hasattr(instance, 'ticket'):
            ticket_number = f'TKT-{instance.event.id}-{instance.id:04d}'
            suffix = 'VIP' if instance.ticket_type == 'vip' else ('PREM' if instance.ticket_type == 'premium' else 'GEN')
            Ticket.objects.get_or_create(
                registration=instance,
                defaults={
                    'ticket_code': f'{ticket_number}-{suffix}',
                    'ticket_number': ticket_number,
                    'ticket_type': instance.ticket_type if instance.ticket_type in Ticket.TicketType.values else Ticket.TicketType.GENERAL,
                },
            )
