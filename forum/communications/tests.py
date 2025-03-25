from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from .models import Communication


class CommunicationsViewTests(APITestCase):

    def setUp(self):
        """
        Set up test data with users and communications.
        """
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password1", first_name="User", last_name="One", is_startup="True"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password2", first_name="User", last_name="Two", is_investor="True"
        )

        self.user3 = User.objects.create_user(
            email="user3@example.com", password="password3", first_name="User", last_name="Three", is_investor="True"
        )

        self.client.force_authenticate(user=self.user1)

        self.communication = Communication.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello from user1 to user2"
        )
        self.communication2 = Communication.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Hello back from user2 to user1"
        )

        self.list_url = reverse('communications-list-create')  # Fixed URL name
        self.detail_url = lambda comm_id: reverse('communication-detail', args=[comm_id])

    def test_get_communications_list(self):
        """Test fetching the list of communications"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_create_communication(self):
        """Test creating a new communication"""
        data = {
            "receiver": self.user2.id,
            "content": "New message to user2"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "New message to user2")
        self.assertEqual(response.data['receiver'], self.user2.id)

    def test_create_communication_self_receiver(self):
        """Test attempting to create a communication to self"""
        data = {
            "receiver": self.user1.id,
            "content": "Message to self"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("receiver", response.data['error'])

    def test_get_communication_detail(self):
        """Test fetching a specific communication"""
        response = self.client.get(self.detail_url(self.communication.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], self.communication.content)

    def test_update_communication(self):
        """Test updating the content of a communication"""
        data = {
            "receiver": self.user2.id,
            "content": "Updated content"
        }
        response = self.client.put(self.detail_url(self.communication.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Updated content")

    def test_delete_communication(self):
        """Test deleting a communication"""
        response = self.client.delete(self.detail_url(self.communication.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Communication.objects.filter(id=self.communication.id).exists())

    def test_permission_denied_delete(self):
        """Test attempting to delete a communication as another user"""
        self.client.force_authenticate(user=self.user3)  # Switch user
        response = self.client.delete(self.detail_url(self.communication.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission", response.data['error'])
