from django.test import TestCase
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def test_user_can_be_created_with_role_and_interests(self):
        user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='StrongPass123!',
            role='attendee',
            mobile_number='9876543210',
            interests='music,food',
        )

        self.assertEqual(user.role, 'attendee')
        self.assertEqual(user.interests, 'music,food')
        self.assertTrue(user.check_password('StrongPass123!'))


class AuthViewTests(TestCase):
    def test_registration_page_creates_a_new_user(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'full_name': 'Bob Smith',
                'username': 'bob',
                'email': 'bob@example.com',
                'mobile_number': '9000000000',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
                'role': 'organizer',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='bob').exists())

    def test_dashboard_renders_for_attendee(self):
        """Logged in attendee can load dashboard."""
        user = User.objects.create_user(
            username='dashboard_att',
            password='password123',
            role='attendee'
        )
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_renders_for_organizer(self):
        """Logged in approved organizer can load dashboard."""
        user = User.objects.create_user(
            username='dashboard_org',
            password='password123',
            role='organizer',
            is_approved=True
        )
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_password_change_flow(self):
        """Logged in user can load the password change view."""
        user = User.objects.create_user(
            username='pwd_user',
            password='oldpassword123',
            role='attendee'
        )
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)
