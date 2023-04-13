from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

User = get_user_model()

class IsAuthenticatedAdmin(BasePermission):
    """Validates logged in user is an admin"""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.staff or request.user.admin
        return False
