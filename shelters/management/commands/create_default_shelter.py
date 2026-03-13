"""
Create a shelter user + shelter for testing. Run once: python manage.py create_default_shelter
Login as shelter1 → Shelter Dashboard appears; edit profile, add pets, CSV import.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from shelters.models import Shelter

User = get_user_model()
SHELTER_USERNAME = "shelter1"
SHELTER_PASSWORD = "ShelterPass123!"
SHELTER_EMAIL = "shelter@example.com"
SHELTER_NAME = "Test Animal Shelter (Latvia)"
SHELTER_ADDRESS = "Riga, Brīvības iela 1"
SHELTER_CITY = "Riga"


class Command(BaseCommand):
    help = "Create user 'shelter1' and a Shelter owned by that user (for testing dashboard & CSV import)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reuse existing shelter1 user and update their shelter.",
        )

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=SHELTER_USERNAME,
            defaults={"email": SHELTER_EMAIL, "is_staff": False, "is_superuser": False},
        )
        if created:
            user.set_password(SHELTER_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{SHELTER_USERNAME}' created."))
        else:
            if options["force"]:
                user.set_password(SHELTER_PASSWORD)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Password reset for '{SHELTER_USERNAME}'."))
            else:
                self.stdout.write(self.style.WARNING(f"User '{SHELTER_USERNAME}' already exists. Use --force to reset password."))

        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"role": UserProfile.ROLE_USER})
        profile.role = UserProfile.ROLE_SHELTER
        profile.save()

        shelter, shelter_created = Shelter.objects.get_or_create(
            owner_user=user,
            defaults={
                "name": SHELTER_NAME,
                "address": SHELTER_ADDRESS,
                "city": SHELTER_CITY,
                "description": "Test shelter for thesis demo.",
            },
        )
        if not shelter_created and options["force"]:
            shelter.name = SHELTER_NAME
            shelter.address = SHELTER_ADDRESS
            shelter.city = SHELTER_CITY
            shelter.save()
            self.stdout.write(self.style.SUCCESS("Shelter updated."))
        elif shelter_created:
            self.stdout.write(self.style.SUCCESS(f"Shelter '{shelter.name}' created and linked to {SHELTER_USERNAME}."))

        self.stdout.write("")
        self.stdout.write("  Login at: http://127.0.0.1:8000/accounts/login/")
        self.stdout.write(f"  Username: {SHELTER_USERNAME}")
        self.stdout.write(f"  Password: {SHELTER_PASSWORD}")
        self.stdout.write("  Then open 'Shelter Dashboard' in the menu → edit profile, add pets, or Import CSV.")
