"""
Create a superuser for local/thesis use. Run once: python manage.py create_default_superuser
If user 'admin' already exists, does nothing (or use --force to reset password).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()
DEFAULT_USERNAME = "admin"
DEFAULT_EMAIL = "admin@example.com"
DEFAULT_PASSWORD = "ChangeMe123!"  # Change after first login


class Command(BaseCommand):
    help = "Create superuser 'admin' with password ChangeMe123! (change after first login)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reset password if user already exists.",
        )

    def handle(self, *args, **options):
        if User.objects.filter(username=DEFAULT_USERNAME).exists():
            if not options["force"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"User '{DEFAULT_USERNAME}' already exists. Use --force to reset password."
                    )
                )
                return
            user = User.objects.get(username=DEFAULT_USERNAME)
            user.set_password(DEFAULT_PASSWORD)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Password reset for '{DEFAULT_USERNAME}'."))
        else:
            User.objects.create_superuser(
                username=DEFAULT_USERNAME,
                email=DEFAULT_EMAIL,
                password=DEFAULT_PASSWORD,
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{DEFAULT_USERNAME}' created."))
        self.stdout.write(
            f"  Login: http://127.0.0.1:8000/admin/  —  username: {DEFAULT_USERNAME}  password: {DEFAULT_PASSWORD}"
        )
        self.stdout.write(self.style.WARNING("  Change the password after first login."))
