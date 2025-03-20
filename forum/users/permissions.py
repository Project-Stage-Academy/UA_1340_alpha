from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class IsInvestor(BasePermission):
    """
    Allows access only to users with the 'investor' role.
    """

    def has_permission(self, request, view):
        auth = JWTAuthentication()
        user_token = auth.get_validated_token(request.headers.get('Authorization', '').split('Bearer ')[-1])

        return user_token.get("role") == "investor"


class IsStartup(BasePermission):
    """
    Allows access only to users with the 'startup' role.
    """

    def has_permission(self, request, view):
        auth = JWTAuthentication()
        user_token = auth.get_validated_token(request.headers.get('Authorization', '').split('Bearer ')[-1])

        return user_token.get("role") == "startup"
