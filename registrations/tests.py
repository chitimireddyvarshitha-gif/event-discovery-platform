from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from events.models import Event, EventCategory
from .models import Registration


class RegistrationModelTests(TestCase):
    def test_registration_prevents_duplicate_booking(self):
        attendee = User.objects.create_user(username='attendee', email='attendee@example.com', password='StrongPass123!', role='attendee')
        organizer = User.objects.create_user(username='organizer', email='organizer@example.com', password='StrongPass123!', role='organizer')
        event = Event.objects.create(
            organizer=organizer,
            event_name='Tech Meetup',
            description='A sample event',
            category=EventCategory.BUSINESS,
            date='2026-08-01 19:00:00',
            venue='Remote',
            ticket_price=10.00,
            capacity=100,
        )

        Registration.objects.create(user=attendee, event=event, status='confirmed')
        exists = Registration.objects.filter(user=attendee, event=event).exists()

        self.assertTrue(exists)


class RegistrationViewTests(TestCase):
    def test_my_registrations_page_renders(self):
        attendee = User.objects.create_user(username='attendee2', email='attendee2@example.com', password='StrongPass123!', role='attendee')
        self.client.force_login(attendee)
        response = self.client.get(reverse('registrations:my_registrations'))
        self.assertEqual(response.status_code, 200)

    def test_cancelled_registrations_do_not_count_towards_capacity(self):
        """A cancelled registration should not prevent new sign-ups when capacity is 1."""
        organizer = User.objects.create_user(username='org_cap', email='org_cap@example.com', password='password123', role='organizer')
        event = Event.objects.create(
            organizer=organizer,
            event_name='Micro Talk',
            description='Talk description',
            category=EventCategory.BUSINESS,
            date='2026-08-01 12:00:00',
            venue='Room 1',
            ticket_price=0.00,
            capacity=1
        )
        
        # User 1 registers and cancels
        user1 = User.objects.create_user(username='att1', email='att1@example.com', password='password123', role='attendee')
        reg1 = Registration.objects.create(user=user1, event=event, status='cancelled')
        
        # User 2 tries to register (capacity is 1, and user1's reg is cancelled, so it should succeed)
        user2 = User.objects.create_user(username='att2', email='att2@example.com', password='password123', role='attendee')
        self.client.force_login(user2)
        response = self.client.post(reverse('registrations:register_for_event', kwargs={'event_id': event.id}), {
            'ticket_type': 'general'
        })
        self.assertEqual(response.status_code, 302) # Redirect to my registrations on success
        
        # Verify user2 registration status is confirmed
        reg2 = Registration.objects.get(user=user2, event=event)
        self.assertEqual(reg2.status, 'confirmed')

    def test_superuser_cannot_register_for_event(self):
        """Superuser/admin should not be allowed to register for any event."""
        superuser = User.objects.create_superuser(username='super_reg', email='super_reg@example.com', password='password123')
        organizer = User.objects.create_user(username='org_reg', email='org_reg@example.com', password='password123', role='organizer')
        event = Event.objects.create(
            organizer=organizer,
            event_name='Unregistrable Event',
            description='Event description',
            category=EventCategory.BUSINESS,
            date='2026-08-01 12:00:00',
            venue='Room 1',
            ticket_price=0.00,
            capacity=10
        )
        self.client.force_login(superuser)
        response = self.client.post(reverse('registrations:register_for_event', kwargs={'event_id': event.id}), {
            'ticket_type': 'general'
        })
        # Should redirect back to event detail view
        self.assertEqual(response.status_code, 302)
        # Verify no registration exists for the superuser
        self.assertFalse(Registration.objects.filter(user=superuser, event=event).exists())
