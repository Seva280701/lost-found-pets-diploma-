"""
User profile and role (guest / user / shelter / admin).
Permissions enforced on backend; role stored here for quick checks.
"""
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Extended user data: role for RBAC (guest = no user, not stored)."""
    ROLE_USER = 'user'
    ROLE_SHELTER = 'shelter'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'Registered user'),
        (ROLE_SHELTER, 'Shelter account'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['role'])]

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


def get_user_role(user):
    """Return role string for user: 'user', 'shelter', or 'admin'. Guest = None."""
    if not user or not user.is_authenticated:
        return None
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return UserProfile.ROLE_USER  # default for legacy users

def is_shelter_user(user):
    if not user or not user.is_authenticated:
        return False
    return get_user_role(user) == UserProfile.ROLE_SHELTER

def is_admin_user(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or get_user_role(user) == UserProfile.ROLE_ADMIN
