from unittest.mock import patch

from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class SignupViewTests(APITestCase):
    def test_signup_with_valid_data_returns_201(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        valid_user_data = {
            'email': 'test@example.com',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'startup'
        }
        response = self.client.post(url, valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['message'], "User created successfully")
        
    def test_signup_with_invalid_data_returns_400(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        invalid_user_data = {
            'email': 'invalid-email',  # Invalid email format
            'password': '123',  # Password too short
            # Missing required fields: 'first_name', 'last_name', 'role'
        }
        response = self.client.post(url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_signup_user_creation_failure_returns_500(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        valid_user_data = {
            'email': 'test@example.com',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'startup'
        }

        # Mock the serializer's save method to return None, simulating a failure
        with patch('users.serializers.UserSerializer.save', return_value=None):
            response = self.client.post(url, valid_user_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['message'], "Failed to create user")
            
    def test_signup_with_missing_required_fields_returns_400(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        missing_fields_data = {
            'email': 'test@example.com',
            'password': 'securepassword123',
            # Missing 'first_name', 'last_name', 'role'
        }
        response = self.client.post(url, missing_fields_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_signup_with_invalid_email_format_returns_400(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        invalid_email_data = {
            'email': 'invalid-email-format',  # Invalid email format
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'startup'
        }
        response = self.client.post(url, invalid_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_with_short_password_returns_400(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        short_password_data = {
            'email': 'test@example.com',
            'password': '123',  # Password too short
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'startup'
        }
        response = self.client.post(url, short_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_with_existing_email_returns_400(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        existing_user_data = {
            'email': 'test@example.com',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'startup'
        }

        # Create a user with the email first
        self.client.post(url, existing_user_data, format='json')

        # Attempt to create another user with the same email
        response = self.client.post(url, existing_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_with_empty_data_returns_400(self):
        url = reverse('signup')  # Assuming the URL pattern name is 'signup'
        empty_data = {}  # Empty request data
        response = self.client.post(url, empty_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('role', response.data)
