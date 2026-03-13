"""Tests for registration and role assignment."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile


class RegistrationTest(TestCase):
    def test_register_creates_user_and_profile(self):
        client = Client()
        response = client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.profile.role, UserProfile.ROLE_USER)


class LoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 't@t.com', 'pass')
        UserProfile.objects.get_or_create(user=self.user, defaults={'role': UserProfile.ROLE_USER})

    def test_login_redirects(self):
        client = Client()
        response = client.post(reverse('accounts:login'), {'username': 'testuser', 'password': 'pass'})
        self.assertEqual(response.status_code, 302)
