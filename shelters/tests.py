"""Tests for shelter CSV import and permissions."""
import csv
import io
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from accounts.models import UserProfile
from shelters.models import Shelter, ShelterPet


class ShelterCsvImportTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('shelter1', 's@test.com', 'pass')
        UserProfile.objects.get_or_create(user=self.user, defaults={'role': UserProfile.ROLE_USER})
        self.shelter = Shelter.objects.create(
            name='Test Shelter',
            address='Riga',
            city='Riga',
            owner_user=self.user,
        )
        UserProfile.objects.filter(user=self.user).update(role=UserProfile.ROLE_SHELTER)

    def test_shelter_user_can_access_import(self):
        self.client = Client()
        self.client.login(username='shelter1', password='pass')
        response = self.client.get(reverse('shelters:csv_import'))
        self.assertEqual(response.status_code, 200)

    def test_import_valid_csv_creates_pets(self):
        self.client = Client()
        self.client.login(username='shelter1', password='pass')
        content = io.StringIO()
        w = csv.writer(content)
        w.writerow(['species', 'description', 'intake_date', 'address'])
        w.writerow(['dog', 'Friendly dog', '2024-01-15', 'Riga, Latvia'])
        csv_bytes = content.getvalue().encode('utf-8')
        response = self.client.post(
            reverse('shelters:csv_import'),
            {'csv_file': SimpleUploadedFile('test.csv', csv_bytes, content_type='text/csv')}
        )
        self.assertEqual(response.status_code, 200)
        # After upload we get preview; then confirm_import to actually import
        response2 = self.client.post(reverse('shelters:csv_import'), {'confirm_import': '1'})
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(ShelterPet.objects.filter(shelter=self.shelter).count(), 1)

    def test_non_shelter_user_cannot_access_dashboard(self):
        """Regular user gets redirected when opening shelter dashboard."""
        user2 = User.objects.create_user('user2', 'u2@test.com', 'pass')
        UserProfile.objects.get_or_create(user=user2, defaults={'role': UserProfile.ROLE_USER})
        client = Client()
        client.login(username='user2', password='pass')
        response = client.get(reverse('shelters:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:home'))
