from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with event platform roles and profile fields."""

    ROLE_CHOICES = (
        ('attendee', 'Attendee'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    )

    full_name = models.CharField(max_length=150, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    interests = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.role == 'organizer' and not self.is_superuser:
            self.is_approved = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username or self.email or self.full_name
