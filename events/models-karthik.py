from django.db import models

from accounts.models import User


class EventCategory(models.TextChoices):
    MUSIC = 'music', 'Music'
    CULTURAL = 'cultural', 'Cultural'
    BUSINESS = 'business', 'Business'
    EDUCATION = 'education', 'Education'
    SPORTS = 'sports', 'Sports'
    FOOD = 'food', 'Food Festivals'


class Event(models.Model):
    """A public event created by an organizer."""

    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    event_name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=EventCategory.choices, default=EventCategory.MUSIC)
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ticket_price_vip = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ticket_price_premium = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    capacity = models.PositiveIntegerField(default=100)
    banner_image = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    agenda = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        if (self.ticket_price_vip is None or self.ticket_price_vip == 0) and self.ticket_price > 0:
            self.ticket_price_vip = Decimal(str(self.ticket_price)) * 2
        if (self.ticket_price_premium is None or self.ticket_price_premium == 0) and self.ticket_price > 0:
            self.ticket_price_premium = Decimal(str(self.ticket_price)) * Decimal('1.5')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.event_name
