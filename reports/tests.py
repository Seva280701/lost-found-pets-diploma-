"""
Functional tests for reports: permissions, create, edit, delete, contact.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from reports.models import PetReport, ContactRequest
from shelters.models import Shelter


class ReportPermissionsTest(TestCase):
    """User can only edit/delete own reports; admin can edit any."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1', 'u1@test.com', 'pass')
        UserProfile.objects.get_or_create(user=self.user1, defaults={'role': UserProfile.ROLE_USER})
        self.user2 = User.objects.create_user('user2', 'u2@test.com', 'pass')
        UserProfile.objects.get_or_create(user=self.user2, defaults={'role': UserProfile.ROLE_USER})
        self.admin = User.objects.create_superuser('admin', 'a@test.com', 'pass')
        self.report = PetReport.objects.create(
            report_type=PetReport.REPORT_LOST,
            status=PetReport.STATUS_OPEN,
            species=PetReport.SPECIES_DOG,
            description='Test',
            location_text='Riga',
            reporter_user=self.user1,
        )

    def test_guest_cannot_create_report(self):
        response = self.client.get(reverse('reports:create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_user_can_create_report(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('reports:create'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_edit_own_report(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('reports:edit', args=[self.report.pk]))
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_others_report(self):
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('reports:edit', args=[self.report.pk]))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_edit_any_report(self):
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('reports:edit', args=[self.report.pk]))
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_own_report(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('reports:delete', args=[self.report.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PetReport.objects.filter(pk=self.report.pk).exists())

    def test_user_cannot_delete_others_report(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(reverse('reports:delete', args=[self.report.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(PetReport.objects.filter(pk=self.report.pk).exists())


class ReportListFilterTest(TestCase):
    """Reports list and filters work."""

    def setUp(self):
        self.client = Client()
        PetReport.objects.create(
            report_type=PetReport.REPORT_LOST,
            status=PetReport.STATUS_OPEN,
            species=PetReport.SPECIES_DOG,
            description='Dog',
            location_text='Riga',
        )
        PetReport.objects.create(
            report_type=PetReport.REPORT_FOUND,
            status=PetReport.STATUS_OPEN,
            species=PetReport.SPECIES_CAT,
            description='Cat',
            location_text='Daugavpils',
        )

    def test_list_returns_both(self):
        response = self.client.get(reverse('reports:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reports']), 2)

    def test_filter_by_type(self):
        response = self.client.get(reverse('reports:list'), {'type': 'LOST'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reports']), 1)
        self.assertEqual(response.context['reports'][0].report_type, PetReport.REPORT_LOST)


class ReportContactTest(TestCase):
    """Contact form for a report creates ContactRequest."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@test.com', 'pass')
        UserProfile.objects.get_or_create(user=self.user, defaults={'role': UserProfile.ROLE_USER})
        self.report = PetReport.objects.create(
            report_type=PetReport.REPORT_LOST,
            status=PetReport.STATUS_OPEN,
            species=PetReport.SPECIES_DOG,
            description='Lost dog',
            location_text='Riga',
            reporter_user=self.user,
        )

    def test_guest_can_submit_contact(self):
        response = self.client.post(
            reverse('reports:contact', args=[self.report.pk]),
            {'from_name': 'Guest', 'from_email': 'g@test.com', 'message_text': 'I saw your pet'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactRequest.objects.filter(to_report=self.report).count(), 1)
        req = ContactRequest.objects.get(to_report=self.report)
        self.assertEqual(req.from_email, 'g@test.com')
        self.assertIsNone(req.from_user_id)

    def test_logged_in_user_contact_has_from_user(self):
        self.client.login(username='u', password='pass')
        response = self.client.post(
            reverse('reports:contact', args=[self.report.pk]),
            {'from_name': 'U', 'from_email': 'u@test.com', 'message_text': 'Hi'},
        )
        self.assertEqual(response.status_code, 302)
        req = ContactRequest.objects.get(to_report=self.report)
        self.assertEqual(req.from_user, self.user)
