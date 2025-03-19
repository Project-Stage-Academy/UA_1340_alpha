import logging

from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            "is_investor",
            "is_startup",
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'validators': [
                    MinLengthValidator(8),
                    MaxLengthValidator(50),
                    RegexValidator(
                        regex=r'^(?=.*[A-Z])(?=.*\d).+$',
                        message="Password must contain at least one uppercase letter and one number."
                    ),
                ],
            },
        }

    def validate(self, attrs):
        """
        Validate that at least one of 'is_investor' or 'is_startup' is True.

        This method checks the provided attributes to ensure that the user 
        is either an investor or a startup. If both fields are False, 
        a ValidationError is raised.

        Args:
            attrs (dict): The validated attributes from the serializer.

        Returns:
            dict: The validated attributes if the validation passes.

        Raises:
            ValidationError: If neither 'is_investor' nor 'is_startup' is True.
        """
        if not attrs.get('is_investor') and not attrs.get('is_startup'):
            raise ValidationError("At least one of 'is_investor' or 'is_startup' must be True.")
        return attrs


    def create(self, validated_data):

        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens where a user selects a role.

    The following user attributes are included in the token:
    - email: User's email address.
    - id: User's unique identifier.
    - role: The selected role for authentication ('startup' or 'investor').

    Logging:
    - Logs the token issuance with the user's email and selected role.

    Args:
        user (User): The user object.
        attrs (dict): Authentication attributes.

    Returns:
        dict: A JWT token containing additional user fields.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        assert isinstance(self.user, User)
        user = self.user
        selected_role = self.context["request"].data.get("role")

        if selected_role not in ["startup", "investor"]:
            raise ValidationError({"role": "Invalid role. Choose 'startup' or 'investor'."})

        if selected_role == "startup" and not user.is_startup:
            raise ValidationError({"role": "You are not registered as a startup."})

        if selected_role == "investor" and not user.is_investor:
            raise ValidationError({"role": "You are not registered as an investor."})

        refresh = RefreshToken.for_user(user)

        refresh.payload["email"] = user.email
        refresh.payload["role"] = selected_role

        data["access"] = str(refresh.access_token)
        data["refresh"] = str(refresh)

        logger.info("Token issued for user: %s with selected role: %s", user.email, selected_role)

        return data
