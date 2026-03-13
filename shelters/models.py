"""
Shelter and ShelterPet models.
Centralized shelter integration for Latvian animal shelters.
"""
from django.conf import settings
from django.db import models


def _set_shelter_role(sender, instance, **kwargs):
    """When a Shelter has owner_user, set that user's profile role to shelter."""
    if instance.owner_user_id:
        from accounts.models import UserProfile
        UserProfile.objects.update_or_create(
            user_id=instance.owner_user_id,
            defaults={'role': UserProfile.ROLE_SHELTER}
        )


class Shelter(models.Model):
    """Animal shelter — one per organization; owner is a User with shelter role."""
    owner_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_shelter',
        null=True,
        blank=True,
        help_text='User account that owns this shelter (shelter role).',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=100, blank=True, db_index=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['verified']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.owner_user_id:
            _set_shelter_role(Shelter, self)


class ShelterPet(models.Model):
    """Pet currently or formerly in shelter care (importable via CSV)."""
    STATUS_IN_CARE = 'IN_CARE'
    STATUS_ADOPTED = 'ADOPTED'
    STATUS_REUNITED = 'REUNITED'
    STATUS_UNKNOWN = 'UNKNOWN'
    STATUS_CHOICES = [
        (STATUS_IN_CARE, 'In care'),
        (STATUS_ADOPTED, 'Adopted'),
        (STATUS_REUNITED, 'Reunited'),
        (STATUS_UNKNOWN, 'Unknown'),
    ]

    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets')
    external_id = models.CharField(max_length=100, blank=True, db_index=True, help_text='From CSV; used to prevent duplicates.')
    name = models.CharField(max_length=100, blank=True)
    species = models.CharField(max_length=50, db_index=True)  # dog, cat, other
    breed = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    intake_date = models.DateField(null=True, blank=True)
    intake_location_text = models.CharField(max_length=300, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_CARE, db_index=True)
    image = models.ImageField(upload_to='shelter_pets/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-intake_date', '-created_at']
        indexes = [
            models.Index(fields=['shelter', 'species']),
            models.Index(fields=['external_id']),
        ]
        # Duplicate prevention by external_id is handled in CSV import (per shelter).

    def __str__(self):
        return f"{self.species} ({self.shelter.name})" + (f" — {self.name}" if self.name else "")
