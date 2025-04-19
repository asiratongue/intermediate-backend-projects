# order_service/permissions.py
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import jwt

class InternalOrJWTAuthentication(permissions.BasePermission):
    """
    Allows access to authenticated users (via JWT) or if the request
    contains a valid internal authentication key.
    """

    def has_permission(self, request, view):
        # Check for JWT authentication first
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(' ')[1]
                jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                return True
            except jwt.ExpiredSignatureError:
                pass  # Let the internal key check happen
            except jwt.InvalidTokenError:
                pass  # Let the internal key check happen

        # Check for internal authentication key
        internal_key = request.META.get('HTTP_X_INTERNAL_KEY')
        return internal_key == settings.INTERNAL_API_KEY