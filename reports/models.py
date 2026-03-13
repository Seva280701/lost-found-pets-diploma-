"""
PetReport (lost/found), PetImage, ContactRequest models.
"""
from django.conf import settings
from django.db import models
from shelters.models import Shelter


class PetReport(models.Model):
    """Lost or found pet report."""
    REPORT_LOST = 'LOST'
    REPORT_FOUND = 'FOUND'
    REPORT_TYPE_CHOICES = [(REPORT_LOST, 'Lost'), (REPORT_FOUND, 'Found')]

    STATUS_OPEN = 'OPEN'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_CHOICES = [(STATUS_OPEN, 'Open'), (STATUS_RESOLVED, 'Resolved')]

    SPECIES_DOG = 'dog'
    SPECIES_CAT = 'cat'
    SPECIES_OTHER = 'other'
    SPECIES_CHOICES = [(SPECIES_DOG, 'Dog'), (SPECIES_CAT, 'Cat'), (SPECIES_OTHER, 'Other')]

    SIZE_SMALL = 'small'
    SIZE_MEDIUM = 'medium'
    SIZE_LARGE = 'large'
    SIZE_CHOICES = [(SIZE_SMALL, 'Small'), (SIZE_MEDIUM, 'Medium'), (SIZE_LARGE, 'Large')]

    SEX_MALE = 'male'
    SEX_FEMALE = 'female'
    SEX_UNKNOWN = 'unknown'
    SEX_CHOICES = [(SEX_MALE, 'Male'), (SEX_FEMALE, 'Female'), (SEX_UNKNOWN, 'Unknown')]

    # Breed and color: predefined + "Other" (stored as-is; "Other" = user did not specify)
    BREED_CHOICES = [
        ('', '— Select —'),
        ('Mixed', 'Mixed'),
        ('Labrador Retriever', 'Labrador Retriever'),
        ('German Shepherd', 'German Shepherd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('French Bulldog', 'French Bulldog'),
        ('Beagle', 'Beagle'),
        ('Poodle', 'Poodle'),
        ('Chihuahua', 'Chihuahua'),
        ('Dachshund', 'Dachshund'),
        ('Rottweiler', 'Rottweiler'),
        ('Yorkshire Terrier', 'Yorkshire Terrier'),
        ('Boxer', 'Boxer'),
        ('European Shorthair', 'European Shorthair'),
        ('Maine Coon', 'Maine Coon'),
        ('Persian', 'Persian'),
        ('British Shorthair', 'British Shorthair'),
        ('Siamese', 'Siamese'),
        ('Ragdoll', 'Ragdoll'),
        ('Bengal', 'Bengal'),
        ('Other', 'Other'),
    ]
    COLOR_CHOICES = [
        ('', '— Select —'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Brown', 'Brown'),
        ('Grey', 'Grey'),
        ('Ginger', 'Ginger'),
        ('Cream', 'Cream'),
        ('Tan', 'Tan'),
        ('Spotted', 'Spotted'),
        ('Striped', 'Striped'),
        ('Mixed', 'Mixed'),
        ('Other', 'Other'),
    ]

    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, db_index=True)
    breed = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, choices=SIZE_CHOICES, blank=True)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, blank=True)
    description = models.TextField()
    date_time_reported = models.DateTimeField(null=True, blank=True)
    location_text = models.CharField(max_length=300)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reporter_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pet_reports',
        null=True,
        blank=True,
    )
    linked_shelter = models.ForeignKey(
        Shelter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_reports',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['species']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} — {self.get_species_display()} ({self.created_at.date()})"


class PetImage(models.Model):
    """Image attached to a pet report (1..N)."""
    report = models.ForeignKey(PetReport, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reports/%Y/%m/')
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for report #{self.report_id}"


class ContactRequest(models.Model):
    """Simple contact message: to a report or to a shelter (guest or registered)."""
    from_name = models.CharField(max_length=150)
    from_email = models.EmailField()
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_contact_requests',
    )
    message_text = models.TextField()
    to_report = models.ForeignKey(
        PetReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contact_requests',
    )
    to_shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contact_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.to_report_id or self.to_shelter_id
        return f"Contact from {self.from_email} to {target}"
