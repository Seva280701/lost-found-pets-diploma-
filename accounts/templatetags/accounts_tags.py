from django import template
from accounts.models import get_user_role

register = template.Library()


@register.simple_tag
def user_role(user):
    """Return role string for user: 'user', 'shelter', 'admin', or None for guest."""
    return get_user_role(user)
