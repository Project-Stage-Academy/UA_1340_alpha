from unittest.mock import patch

from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
