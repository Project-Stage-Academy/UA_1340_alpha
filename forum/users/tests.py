import logging
from unittest.mock import ANY, patch

import jwt
from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from .models import User

logger = logging.getLogger(__name__)


class SignupViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.valid_user_data = {
            'email': 'test@example.com',
            'password': 'SecurePassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'startup'
        }

    def test_signup_with_valid_data_returns_201(self):
        response = self.client.post(self.url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['message'], "User created successfully")
        
    def test_signup_with_invalid_data_returns_400(self):
        invalid_user_data = {
            'email': 'invalid-email',  # Invalid email format
            'password': 'S123',  # Password too short
            # Missing required fields: 'first_name', 'last_name', 'role'
        }
        response = self.client.post(self.url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_signup_user_creation_failure_returns_500(self):
        # Mock the serializer's save method to return None, simulating a failure
        with patch('users.serializers.UserSerializer.save', return_value=None):
            response = self.client.post(self.url, self.valid_user_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['message'], "Failed to create user")
            
    def test_signup_with_missing_required_fields_returns_400(self):
        missing_fields_data = {
            'email': 'test@example.com',
            'password': 'SecurePassword123',
            # Missing 'first_name', 'last_name', 'role'
        }
        response = self.client.post(self.url, missing_fields_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_signup_with_invalid_email_format_returns_400(self):
        invalid_email_data = self.valid_user_data.copy()
        invalid_email_data['email'] = 'invalid-email'  # Invalid email format
        response = self.client.post(self.url, invalid_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_with_short_password_returns_400(self):
        short_password_data = self.valid_user_data.copy()
        short_password_data['password'] = 'S123'  # Password too short
        response = self.client.post(self.url, short_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_with_existing_email_returns_400(self):
        # Create a user with the email first
        self.client.post(self.url, self.valid_user_data, format='json')
        # Attempt to create another user with the same email
        response = self.client.post(self.url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_with_empty_data_returns_400(self):
        empty_data = {}  # Empty request data
        response = self.client.post(self.url, empty_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('role', response.data)

    def test_signup_with_long_password_returns_400(self):
        long_password_data = self.valid_user_data.copy()
        long_password_data['password'] = 'A' * 51 + '1'  # Password longer than 50 characters
        response = self.client.post(self.url, long_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        
    def test_signup_with_password_missing_uppercase_returns_400(self):
        password_missing_uppercase_data = self.valid_user_data.copy()
        password_missing_uppercase_data['password'] = 'securepassword123'  # No uppercase letter
        response = self.client.post(self.url, password_missing_uppercase_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_with_password_missing_number_returns_400(self):
        password_missing_number_data = self.valid_user_data.copy()
        password_missing_number_data['password'] = 'SecurePassword'  # No number
        response = self.client.post(self.url, password_missing_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_with_password_only_numbers_returns_400(self):
        password_only_numbers_data = self.valid_user_data.copy()
        password_only_numbers_data['password'] = '12345678'  # Only numbers
        response = self.client.post(self.url, password_only_numbers_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_with_password_missing_returns_400(self):
        password_missing_data = self.valid_user_data.copy()
        del password_missing_data['password']  # Remove password field from data
        response = self.client.post(self.url, password_missing_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_with_invalid_role_returns_400(self):
        invalid_role_data = self.valid_user_data.copy()
        invalid_role_data['role'] = 'invalid_role'  # Invalid role
        response = self.client.post(self.url, invalid_role_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)


class VerifyEmailViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('verify-email')

    def test_verify_email_without_token_returns_400(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Token is required")

    def test_verify_email_with_expired_token_returns_400(self):
        expired_token = 'expired_token_example'

        with patch("jwt.decode", side_effect=jwt.ExpiredSignatureError):
            response = self.client.get(self.url, {'token': expired_token})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error'], "Token has expired")

    def test_verify_email_with_malformed_token_returns_400(self):
        malformed_token = 'malformed_token_example'

        with patch("jwt.decode", side_effect=jwt.InvalidTokenError):
            response = self.client.get(self.url, {'token': malformed_token})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error'], "Invalid token")

    def test_verify_email_with_valid_token_returns_200(self):
        user = User.objects.create(email='test@example.com', is_email_confirmed=False, is_active=False)
        valid_token = AccessToken.for_user(user)

        response = self.client.get(self.url, {'token': str(valid_token)})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Email verified successfully")

        user.refresh_from_db()
        self.assertTrue(user.is_email_confirmed)
        self.assertTrue(user.is_active)

    def test_verify_email_with_valid_token_user_not_found_returns_404(self):
        valid_token = 'valid_token_example'

        with patch("jwt.decode", return_value={"user_id": 999999}):
            response = self.client.get(self.url, {'token': valid_token})
            print(response)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data['error'], "User not found")

    def test_verify_email_unexpected_exception_returns_500(self):
        valid_token = 'valid_token_example'

        with patch("jwt.decode", return_value={"user_id": 1}), \
                patch('users.models.User.objects.get', side_effect=Exception("Unexpected error")):
            response = self.client.get(self.url, {'token': valid_token})
            print(response)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error'], "Unexpected error occurred")

    def test_verify_email_database_error_returns_500(self):
        valid_token = 'valid_token_example'

        with patch("jwt.decode", return_value={"user_id": 1}), \
                patch('users.models.User.objects.get', side_effect=DatabaseError("Database connection failed")):
            response = self.client.get(self.url, {'token': valid_token})
            print(response)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error'], "Database error occurred")


class ResendVerificationEmailViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('resend-verification-email')
        self.email = 'test@example.com'
        self.user = User.objects.create(email=self.email, is_email_confirmed=False)

    def test_resend_verification_email_with_valid_email_returns_200(self):
        with patch('users.views.send_verification_email', return_value=True) as mock_send_email:
            response = self.client.post(self.url, {'email': self.email}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Verification email was sent.')
            mock_send_email.assert_called_once_with(self.user, ANY)

    def test_resend_verification_email_missing_email_returns_400(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Email is required')

    def test_resend_verification_email_non_existent_user_returns_404(self):
        non_existent_email_data = {'email': 'nonexistent@example.com'}

        response = self.client.post(self.url, non_existent_email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Email verification requested for non-existent email")

    def test_resend_verification_email_unexpected_exception_returns_500(self):
        with patch('users.models.User.objects.get', side_effect=Exception("Unexpected error")):
            response = self.client.post(self.url, {'email': self.email}, format='json')

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error'], "Failed to send verification email.")
            self.assertIn('details', response.data)

    def test_resend_verification_email_service_failure_returns_500(self):
        with patch('users.views.send_verification_email', return_value=False):
            response = self.client.post(self.url, {'email': self.email}, format='json')
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error'], "Failed to send verification email.")

    def test_resend_verification_email_confirmed_user_returns_200(self):
        self.user.is_email_confirmed = True
        self.user.save()

        with patch('users.views.send_verification_email', return_value=True) as mock_send_email:
            response = self.client.post(self.url, {'email': self.email}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Email is already verified.')
