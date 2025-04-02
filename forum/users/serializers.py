import logging

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
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

    Args:
        user (User): The user object.
        attrs (dict): Authentication attributes.

    Returns:
        dict: A JWT token containing additional user fields.
    """
    role = serializers.ChoiceField(choices=["startup", "investor"], required=True)

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

        if not user.is_email_confirmed:
            raise ValidationError({"email": "Email not verified. Verify your email and try again."})

        if user.status == 'banned':
            raise ValidationError({"status": "Your account has been banned. You cannot log in."})

        if not user.is_active:
            raise ValidationError({"status": "Your account is inactive. Please contact support."})

        refresh = RefreshToken.for_user(user)
        refresh.payload["email"] = user.email
        refresh.payload["role"] = selected_role

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class CustomRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["startup", "investor", ], required=True)

    def validate(self, attrs):
        user = self.context["request"].user
        assert isinstance(user, User)
        selected_role = attrs.get("role")

        if selected_role not in ["startup", "investor"]:
            raise serializers.ValidationError({"role": "Invalid role. Choose 'startup' or 'investor'."})

        if selected_role == "startup" and not user.is_startup:
            raise serializers.ValidationError({"role": "You are not registered as a startup."})

        if selected_role == "investor" and not user.is_investor:
            raise serializers.ValidationError({"role": "You are not registered as an investor."})

        if not user.is_email_confirmed:
            raise serializers.ValidationError({"email": "Email not verified. Verify your email and try again."})

        if user.status == 'banned':
            raise serializers.ValidationError({"status": "Your account has been banned."})

        if not user.is_active:
            raise serializers.ValidationError({"status": "Your account is inactive."})

        # Генерація токенів
        refresh = RefreshToken.for_user(user)
        refresh.payload["email"] = user.email
        refresh.payload["role"] = selected_role

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    

class SetRoleSerializer(serializers.Serializer):
    roles = serializers.MultipleChoiceField(
        choices=["startup", "investor"],
        required=True,
        help_text="Select one or both roles: 'startup', 'investor'."
    )

    def validate(self, attrs):
        request = self.context["request"]
        selected_roles = attrs.get("roles")

        if not selected_roles:
            raise serializers.ValidationError({"roles": "At least one role must be selected."})

        sociallogin_data = request.session.get('sociallogin')
        if not sociallogin_data:
            raise serializers.ValidationError({"error": "No social login data found. Please start signup again."})

        sociallogin = SocialLogin.deserialize(sociallogin_data)
        from allauth.socialaccount.helpers import complete_social_login
        complete_social_login(request, sociallogin)

        user = sociallogin.user
        if not isinstance(user, User):
            raise ValidationError({"error": "Failed to create user."})

        if "startup" in selected_roles:
            user.is_startup = True
        if "investor" in selected_roles:
            user.is_investor = True

        if not user.is_email_confirmed:
            user.is_email_confirmed = True

        if user.status == 'banned':
            raise serializers.ValidationError({"status": "Your account has been banned."})

        if not user.is_active:
            raise serializers.ValidationError({"status": "Your account is inactive."})

        user.save()

        primary_role = list(selected_roles)[0]

        refresh = RefreshToken.for_user(user)
        refresh.payload["email"] = user.email
        refresh.payload["role"] = primary_role

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    