from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from events.models import Event, EventCategory
from registrations.models import Registration
from tickets.models import Ticket


class AnalyticsTests(TestCase):
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
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
            email='admin@example.com'
        )
        
        # Create event
        self.event = Event.objects.create(
            organizer=self.organizer,
            event_name='Grand Concert',
            description='This is going to be epic.',
            category=EventCategory.MUSIC,
            date=timezone.now(),
            venue='Symphony Hall',
            ticket_price=20.00,
            capacity=100
        )
        
        # Create registration & tickets
        self.registration = Registration.objects.create(
            user=self.attendee,
            event=self.event,
            status='confirmed'
        )
        # Ticket is auto-created in signal; let's configure it as VIP
        self.ticket = Ticket.objects.get(registration=self.registration)
        self.ticket.ticket_type = Ticket.TicketType.VIP
        self.ticket.save()

    def test_organizer_reports_dashboard_context(self):
        """Organizer reports dashboard retrieves the correct count and revenue aggregates."""
        self.client.login(username='org_user', password='password123')
        response = self.client.get(reverse('analytics:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], 'organizer')
        self.assertEqual(response.context['total_events'], 1)
        self.assertEqual(response.context['total_registrations'], 1)
        # VIP is 2x price (20 * 2 = 40)
        self.assertEqual(response.context['total_revenue'], Decimal('40.00'))

    def test_attendee_reports_dashboard_context(self):
        """Attendee reports dashboard retrieves correct attendee expenditures."""
        self.client.login(username='attendee_user', password='password123')
        response = self.client.get(reverse('analytics:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], 'attendee')
        self.assertEqual(response.context['total_registrations'], 1)
        self.assertEqual(response.context['total_spent'], Decimal('40.00'))

    def test_admin_reports_dashboard_context(self):
        """Admin reports dashboard retrieves platform-wide statistics."""
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('analytics:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], 'admin')
        self.assertEqual(response.context['total_users'], 3)
        self.assertEqual(response.context['total_events'], 1)

    def test_organizer_chart_data_api(self):
        """Organizer chart api returns registrations and ticket type datasets."""
        self.client.login(username='org_user', password='password123')
        response = self.client.get(reverse('analytics:chart_data'))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('bar', json_data)
        self.assertIn('doughnut', json_data)
        self.assertEqual(json_data['doughnut']['labels'], ['General', 'Premium', 'VIP'])
        # Generates ticket as general by default, then we saved as VIP in setUp
        self.assertEqual(json_data['doughnut']['datasets'][0]['data'], [0, 0, 1])

    def test_attendee_chart_data_api(self):
        """Attendee chart api returns category spend and month tracking datasets."""
        self.client.login(username='attendee_user', password='password123')
        response = self.client.get(reverse('analytics:chart_data'))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('doughnut', json_data)
        self.assertIn('line', json_data)
        # Spent 40.0 on Music category, others 0.0
        self.assertEqual(json_data['doughnut']['datasets'][0]['data'][0], 40.0)

    def test_admin_chart_data_api(self):
        """Admin chart api returns user growth and popular events list."""
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('analytics:chart_data'))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('line', json_data)
        self.assertIn('bar', json_data)
        self.assertEqual(json_data['bar']['labels'][0], 'Grand Concert')
        self.assertEqual(json_data['bar']['datasets'][0]['data'][0], 1)

    def test_superuser_with_attendee_role_gets_admin_reports(self):
        """A user with is_superuser=True but role='attendee' should still get admin reports."""
        superuser = User.objects.create_superuser(
            username='super_attendee',
            password='password123',
            email='superatt@example.com'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, 'attendee')
        
        self.client.force_login(superuser)
        response = self.client.get(reverse('analytics:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], 'admin')
        self.assertIn('total_attendees', response.context)
        self.assertIn('total_organizers', response.context)

        response_chart = self.client.get(reverse('analytics:chart_data'))
        self.assertEqual(response_chart.status_code, 200)
        json_data = response_chart.json()
        self.assertIn('line', json_data)
        self.assertIn('bar', json_data)
