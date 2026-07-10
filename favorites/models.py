from django.db import models

from accounts.models import User
from events.models import Event


class Favorite(models.Model):
    """Represents an event saved by an attendee for later."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} -> {self.event.event_name}'
