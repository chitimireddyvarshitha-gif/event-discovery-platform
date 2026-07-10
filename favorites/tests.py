from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from events.models import Event, EventCategory

from .models import Favorite


class FavoriteTests(TestCase):
    def test_favorite_can_be_added_and_listed(self):
        attendee = User.objects.create_user(
            username='favuser',
            email='favuser@example.com',
            password='StrongPass123!',
            role='attendee',
        )
        organizer = User.objects.create_user(
            username='favorganizer',
            email='favorganizer@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        event = Event.objects.create(
            organizer=organizer,
            event_name='Design Sprint',
            description='A test event',
            category=EventCategory.EDUCATION,
            date='2026-11-01 19:00:00',
            venue='Remote',
            ticket_price=20.00,
            capacity=40,
        )

        self.client.force_login(attendee)
        response = self.client.post(reverse('favorites:toggle', kwargs={'event_id': event.id}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=attendee, event=event).exists())

        list_response = self.client.get(reverse('favorites:list'))
        self.assertEqual(list_response.status_code, 200)
