from django.db import models

from accounts.models import User
from events.models import Event


class Registration(models.Model):
    """Represents an attendee booking for an event."""

    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ticket_type = models.CharField(max_length=20, default='general')
    payment_details = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f'{self.user.username} -> {self.event.event_name}'
