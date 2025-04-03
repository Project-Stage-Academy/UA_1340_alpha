from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsInvestor(BasePermission):
    """
    Allows access only to users with the 'investor' role.
    """
    message = "You must be an investor to access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_investor)

class IsStartup(BasePermission):
    """
    Allows access only to users with the 'startup' role.
    """
    message = "You must be a startup to access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_startup)
