import logging

from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
            'role',
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
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        token['email'] = user.email
        token['role'] = user.role
        token['is_active'] = user.is_active

        logger.info(f"Token issued for user: {user.email} with role: {user.role}")

        return token

