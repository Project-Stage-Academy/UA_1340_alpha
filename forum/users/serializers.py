from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken  

from .models import User


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
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        # Генерація токена
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
