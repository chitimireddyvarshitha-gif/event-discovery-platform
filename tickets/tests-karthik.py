from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from events.models import Event, EventCategory
from registrations.models import Registration

from .models import Ticket


class TicketGenerationTests(TestCase):
    def test_ticket_is_created_for_new_registration(self):
        attendee = User.objects.create_user(
            username='ticketattendee',
            email='ticketattendee@example.com',
            password='StrongPass123!',
            role='attendee',
        )
        organizer = User.objects.create_user(
            username='ticketorganizer',
            email='ticketorganizer@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        event = Event.objects.create(
            organizer=organizer,
            event_name='AI Summit',
            description='A practical summit',
            category=EventCategory.BUSINESS,
            date='2026-09-01 19:00:00',
            venue='Remote',
            ticket_price=25.00,
            capacity=50,
        )

        registration = Registration.objects.create(user=attendee, event=event, status='confirmed')
        ticket = Ticket.objects.get(registration=registration)

        self.assertTrue(ticket.ticket_number)
        self.assertEqual(ticket.ticket_type, Ticket.TicketType.GENERAL)

    def test_ticket_list_page_renders_for_attendee(self):
        attendee = User.objects.create_user(
            username='ticketviewer',
            email='ticketviewer@example.com',
            password='StrongPass123!',
            role='attendee',
        )
        self.client.force_login(attendee)

        response = self.client.get(reverse('tickets:list'))

        self.assertEqual(response.status_code, 200)

    def test_organizer_sales_page_renders(self):
        attendee = User.objects.create_user(
            username='salesviewer',
            email='salesviewer@example.com',
            password='StrongPass123!',
            role='attendee',
        )
        organizer = User.objects.create_user(
            username='salesorganizer',
            email='salesorganizer@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        event = Event.objects.create(
            organizer=organizer,
            event_name='Design Meetup',
            description='A design meetup',
            category=EventCategory.EDUCATION,
            date='2026-10-01 19:00:00',
            venue='Remote',
            ticket_price=15.00,
            capacity=30,
        )
        Registration.objects.create(user=attendee, event=event, status='confirmed')
        self.client.force_login(organizer)

        response = self.client.get(reverse('tickets:organizer_sales', kwargs={'event_id': event.id}))

        self.assertEqual(response.status_code, 200)

    def test_organizer_sales_uses_database_vip_and_premium_prices(self):
        """Organizer sales view should use database ticket prices instead of hardcoded multipliers."""
        attendee1 = User.objects.create_user(username='att_sales1', email='att_sales1@example.com', password='password123', role='attendee')
        attendee2 = User.objects.create_user(username='att_sales2', email='att_sales2@example.com', password='password123', role='attendee')
        attendee3 = User.objects.create_user(username='att_sales3', email='att_sales3@example.com', password='password123', role='attendee')
        organizer = User.objects.create_user(username='org_sales', email='org_sales@example.com', password='password123', role='organizer')
        event = Event.objects.create(
            organizer=organizer,
            event_name='Custom Price Concert',
            description='Concert description',
            category=EventCategory.MUSIC,
            date='2026-09-01 20:00:00',
            venue='Symphony Hall',
            ticket_price=10.00,
            ticket_price_vip=35.00,
            ticket_price_premium=45.00,
            capacity=10,
        )
        # Create registrations with different types
        reg1 = Registration.objects.create(user=attendee1, event=event, status='confirmed', ticket_type='general')
        reg2 = Registration.objects.create(user=attendee2, event=event, status='confirmed', ticket_type='vip')
        reg3 = Registration.objects.create(user=attendee3, event=event, status='confirmed', ticket_type='premium')
        
        self.client.force_login(organizer)
        response = self.client.get(reverse('tickets:organizer_sales', kwargs={'event_id': event.id}))
        
        self.assertEqual(response.status_code, 200)
        # Total revenue should be 10 + 35 + 45 = 90.00
        self.assertEqual(response.context['summary']['revenue'], 90.00)

    def test_superuser_can_view_any_event_sales_summary(self):
        """Superuser should be allowed to view event sales summary for events they do not own."""
        superuser = User.objects.create_superuser(username='super_sales', email='super_sales@example.com', password='password123')
        organizer = User.objects.create_user(username='org_sales2', email='org_sales2@example.com', password='password123', role='organizer')
        event = Event.objects.create(
            organizer=organizer,
            event_name='Custom Price Concert 2',
            description='Concert description',
            category=EventCategory.MUSIC,
            date='2026-09-01 20:00:00',
            venue='Symphony Hall',
            ticket_price=10.00,
            capacity=10,
        )
        self.client.force_login(superuser)
        response = self.client.get(reverse('tickets:organizer_sales', kwargs={'event_id': event.id}))
        self.assertEqual(response.status_code, 200)
