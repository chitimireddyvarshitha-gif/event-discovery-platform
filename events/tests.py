from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Event, EventCategory


class EventModelTests(TestCase):
    def test_event_can_be_created_with_category_and_organizer(self):
        organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        event = Event.objects.create(
            organizer=organizer,
            event_name='Summer Jam',
            description='A fun event',
            category=EventCategory.MUSIC,
            date='2026-08-01',
            venue='Downtown Hall',
            ticket_price=25.00,
            capacity=100,
        )

        self.assertEqual(event.organizer, organizer)
        self.assertEqual(event.category, EventCategory.MUSIC)


class EventViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_attendee',
            email='attendee@example.com',
            password='StrongPass123!',
            role='attendee'
        )

    def test_event_list_renders_unauthenticated(self):
        """Unauthenticated requests can browse the event list."""
        response = self.client.get(reverse('events:list'))
        self.assertEqual(response.status_code, 200)

    def test_event_list_page_renders_when_authenticated(self):
        """Logged-in users can browse the event list."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('events:list'))
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_view_any_event_participants(self):
        """Superuser should be allowed to view participants list for events they do not own."""
        superuser = User.objects.create_superuser(username='super_part', email='super_part@example.com', password='password123')
        organizer = User.objects.create_user(
            username='organizer_part',
            email='organizer_part@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        event = Event.objects.create(
            organizer=organizer,
            event_name='Grand Symphony',
            description='A classic event',
            category=EventCategory.MUSIC,
            date='2026-08-01 19:00:00',
            venue='Downtown Hall',
            ticket_price=25.00,
            capacity=100,
        )
        self.client.force_login(superuser)
        response = self.client.get(reverse('events:participants', kwargs={'event_id': event.id}))
        self.assertEqual(response.status_code, 200)
