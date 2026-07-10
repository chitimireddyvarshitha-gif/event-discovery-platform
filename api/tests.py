from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from events.models import Event, EventCategory
from registrations.models import Registration
from tickets.models import Ticket
from notifications.models import Notification

User = get_user_model()


class EventHubAPITests(APITestCase):
    def setUp(self):
        # Create attendee user
        self.attendee = User.objects.create_user(
            username='api_attendee',
            password='password123',
            role='attendee',
            email='api_attendee@example.com'
        )
        self.attendee_token = Token.objects.create(user=self.attendee)
        
        # Create organizer user
        self.organizer = User.objects.create_user(
            username='api_organizer',
            password='password123',
            role='organizer',
            email='api_organizer@example.com'
        )
        self.organizer_token = Token.objects.create(user=self.organizer)

        # Create an event
        self.event = Event.objects.create(
            organizer=self.organizer,
            event_name='API Tech Talk',
            description='Let\'s discuss REST API constraints.',
            category=EventCategory.BUSINESS,
            date=timezone.now(),
            venue='Virtual Room A',
            ticket_price=0.00,
            capacity=2
        )

    def test_user_registration_via_api(self):
        """API client can sign up and receive a token."""
        url = reverse('api:register')
        data = {
            'username': 'new_api_user',
            'password': 'StrongPass123!',
            'email': 'new_api@example.com',
            'mobile_number': '1234567890',
            'role': 'attendee',
            'full_name': 'New Api User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'new_api_user')

    def test_user_login_via_api(self):
        """API client receives a token with valid login credentials."""
        url = reverse('api:login')
        data = {
            'username': 'api_attendee',
            'password': 'password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        # Invalid login
        invalid_data = {
            'username': 'api_attendee',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_endpoint_requires_auth(self):
        """Profile view retrieves authenticated credentials or rejects anonymous requests."""
        url = reverse('api:profile')
        
        # Unauthorized
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authorized
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.attendee_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'api_attendee')

    def test_event_create_restricted_by_role(self):
        """Organizers can create events; attendees are forbidden."""
        url = reverse('api:event-list')
        data = {
            'event_name': 'Restricted Session',
            'description': 'Description',
            'category': EventCategory.SPORTS,
            'date': timezone.now().isoformat(),
            'venue': 'Gym',
            'ticket_price': 5.00,
            'capacity': 10
        }

        # Attendee attempt -> 403 Forbidden
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.attendee_token.key)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer attempt -> 201 Created
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.organizer_token.key)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['event_name'], 'Restricted Session')

    def test_registration_flow_and_ticket_type_interceptor(self):
        """Attendees can register, select VIP tier, and receive customized tickets."""
        url = reverse('api:registration-list')
        
        # Organizer cannot register for events
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.organizer_token.key)
        response = self.client.post(url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Attendee registers with VIP selection
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.attendee_token.key)
        response = self.client.post(url, {
            'event': self.event.id,
            'ticket_type': 'vip'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify ticket was issued and interceptor updated it to VIP
        ticket = Ticket.objects.get(registration__id=response.data['id'])
        self.assertEqual(ticket.ticket_type, Ticket.TicketType.VIP)
        self.assertTrue(ticket.ticket_code.endswith('-VIP'))

    def test_duplicate_registration_and_capacity_constraints(self):
        """Registration API prevents double bookings and respects limits."""
        url = reverse('api:registration-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.attendee_token.key)
        
        # Booking 1
        response = self.client.post(url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Booking 2 (Duplicate attempt)
        response = self.client.post(url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

        # Create another attendee to test capacity limits
        other_attendee = User.objects.create_user(
            username='other_attendee',
            password='password123',
            role='attendee'
        )
        other_token = Token.objects.create(user=other_attendee)
        
        # Booking 2 (fills event capacity of 2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token.key)
        response = self.client.post(url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a third attendee (exceeds capacity limit of 2)
        third_attendee = User.objects.create_user(
            username='third_attendee',
            password='password123',
            role='attendee'
        )
        third_token = Token.objects.create(user=third_attendee)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + third_token.key)
        
        response = self.client.post(url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_organizer_registration_and_approval_workflow(self):
        """Organizers register as unapproved and cannot login until approved by super admin."""
        # 1. Register as organizer
        register_url = reverse('api:register')
        data = {
            'username': 'new_org',
            'password': 'StrongPass123!',
            'email': 'org_new@example.com',
            'mobile_number': '1234567890',
            'role': 'organizer',
            'full_name': 'New Organizer'
        }
        response = self.client.post(register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('token', response.data)
        self.assertIn('pending approval', response.data['message'])

        # 2. Attempt login (should fail with 403 Forbidden)
        login_url = reverse('api:login')
        login_data = {
            'username': 'new_org',
            'password': 'StrongPass123!'
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('pending approval', response.data['error'])

        # 3. Super admin approves the organizer
        user = User.objects.get(username='new_org')
        user.is_approved = True
        user.save()

        # 4. Attempt login again (should succeed and return token)
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_paid_event_api_registration_enforces_payment(self):
        """Paid events require card details and fail with 400 if details are missing."""
        # Create a paid event
        paid_event = Event.objects.create(
            organizer=self.organizer,
            event_name='Paid Talk',
            description='Talk description.',
            category=EventCategory.BUSINESS,
            date=timezone.now(),
            venue='Auditorium',
            ticket_price=50.00,
            capacity=10
        )
        url = reverse('api:registration-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.attendee_token.key)
        
        # Try registration without payment details
        response = self.client.post(url, {'event': paid_event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Payment is required', str(response.data))

        # Register with valid card details
        response = self.client.post(url, {
            'event': paid_event.id,
            'card_number': '4242 4242 4242 4242',
            'card_name': 'Alice Smith'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
