from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from django.core.management import call_command

from accounts.models import User
from events.models import Event, EventCategory
from registrations.models import Registration
from tickets.models import Ticket
from notifications.models import Notification


class NotificationTests(TestCase):
    def setUp(self):
        # Create users
        self.organizer = User.objects.create_user(
            username='org_user',
            password='password123',
            role='organizer',
            email='org@example.com'
        )
        self.attendee = User.objects.create_user(
            username='attendee_user',
            password='password123',
            role='attendee',
            email='attendee@example.com'
        )
        
        # Create event
        self.event = Event.objects.create(
            organizer=self.organizer,
            event_name='Awesome Concert',
            description='This is going to be epic.',
            category=EventCategory.MUSIC,
            date=timezone.now() + timedelta(days=5),
            venue='Madison Square Garden',
            ticket_price=10.00,
            capacity=100
        )

    def test_ticket_issuance_creates_notification_and_email(self):
        """Creating a registration (and subsequent ticket) triggers notification signals."""
        mail.outbox.clear()
        
        # Create registration
        registration = Registration.objects.create(
            user=self.attendee,
            event=self.event,
            status='confirmed'
        )
        
        # Signal creates ticket -> notifications signal creates notification and email
        self.assertTrue(Ticket.objects.filter(registration=registration).exists())
        
        # Assert Notification created
        notifs = Notification.objects.filter(user=self.attendee)
        self.assertEqual(notifs.count(), 1)
        self.assertIn("Ticket Confirmed", notifs.first().title)
        
        # Assert Email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Your Ticket is Ready", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.attendee.email])

    def test_event_edit_notifies_attendees(self):
        """Editing an event triggers notifications to all registered attendees."""
        # Register attendee
        Registration.objects.create(
            user=self.attendee,
            event=self.event,
            status='confirmed'
        )
        
        # Authenticate organizer
        self.client.login(username='org_user', password='password123')
        
        # Clear previous notifications (e.g. from ticket creation)
        Notification.objects.all().delete()
        
        # Post event edit
        url = reverse('events:edit', kwargs={'event_id': self.event.id})
        data = {
            'event_name': 'Super Awesome Concert',
            'description': 'Updated description.',
            'category': EventCategory.MUSIC,
            'date': (timezone.now() + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M'),
            'venue': 'Vembley Arena',
            'ticket_price': 15.00,
            'ticket_price_vip': 30.00,
            'ticket_price_premium': 50.00,
            'capacity': 150
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        
        # Check attendee notifications
        notifs = Notification.objects.filter(user=self.attendee)
        self.assertEqual(notifs.count(), 1)
        self.assertIn("Event Updated", notifs.first().title)

    def test_notification_apis_and_unread_count(self):
        """API endpoints retrieve correct counts and mark items read."""
        # Create notification
        notif = Notification.objects.create(
            user=self.attendee,
            title='Sample notification',
            message='Hello there'
        )
        
        self.client.login(username='attendee_user', password='password123')
        
        # Test count API
        count_url = reverse('notifications:unread_api')
        response = self.client.get(count_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 1)
        self.assertEqual(len(response.json()['recent_notifications']), 1)
        
        # Test mark read API
        read_url = reverse('notifications:mark_read', kwargs={'notification_id': notif.id})
        response = self.client.post(read_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify read state in database
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_send_event_reminders_command(self):
        """Reminders command processes events in 24 hours, creates notifications, and avoids duplicates."""
        # Move event date to occur in 12 hours
        self.event.date = timezone.now() + timedelta(hours=12)
        self.event.save()
        
        # Register attendee
        Registration.objects.create(
            user=self.attendee,
            event=self.event,
            status='confirmed'
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        mail.outbox.clear()
        
        # Call command
        call_command('send_event_reminders')
        
        # Assert reminder notification was sent
        notifs = Notification.objects.filter(user=self.attendee, title__icontains="Reminder")
        self.assertEqual(notifs.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        
        # Run command again to assert duplicate prevention
        call_command('send_event_reminders')
        notifs_again = Notification.objects.filter(user=self.attendee, title__icontains="Reminder")
        self.assertEqual(notifs_again.count(), 1) # Still 1!
