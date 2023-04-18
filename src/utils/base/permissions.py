from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.models import TokenUser


class IsAuthenticated(BasePermission):
    """
    This is a permission class to validate
    that the user is authenticated
    """

    def set_request_set(self, request: HttpRequest):
        """
        if the request is a TokenUser, set the request.user to the
        actual user object
        """

        User = get_user_model()
        if isinstance(request.user, TokenUser):
            user = User.objects.get(id=request.user.id)
            request.user = user

    def has_permission(self, request: HttpRequest, view):
        self.set_request_set(request)
        return request.user.is_active


class IsAuthenticatedAdmin(IsAuthenticated):
    """Validates logged in user is an admin"""

    def has_permission(self, request: HttpRequest, view):
        if super().has_permission(request, view):
            if request.user.is_authenticated:
                return request.user.is_personnel
