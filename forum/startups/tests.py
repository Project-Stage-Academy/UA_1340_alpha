from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from users.models import User
from startups.models import StartupProfile, Industry
from startups.views import StartupProfileListCreateAPIView, StartupProfileDetailAPIView


class StartupProfileApiTests(APITestCase):

    def setUp(self):
        """
        Setting up the test environment.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            role="startup"
        )

        # Create a test industry
        self.industry = Industry.objects.create(name="Test Technology")

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name="Test Startup",
            description="A test startup.",
            contact_email="teststartup@example.com"
        )

        # Add the industry to the startup
        self.startup.industries.add(self.industry)

        self.factory = APIRequestFactory()

    def test_get_startup_list(self):
        """
        Test: retrieve a list of startups.
        """
        view = StartupProfileListCreateAPIView.as_view()

        request = self.factory.get('/api/startups/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], self.startup.company_name)

    def test_create_startup(self):
        """
        Test: create a new startup.
        """
        view = StartupProfileListCreateAPIView.as_view()

        # Create a new user
        new_user = User.objects.create_user(
            first_name="newuser",
            last_name="newuser",
            password="newpassword",
            email="newuser@example.com",
            role="startup"
        )

        # Create a new industry
        industry = Industry.objects.create(name="Technology")

        payload = {
            "company_name": "New Startup",
            "description": "Another test startup.",
            "contact_email": "newstartup@example.com",
            "industries": [industry.id],  # Add the required industry
        }

        request = self.factory.post('/api/startups/', payload)
        force_authenticate(request, user=new_user)  # Use the new user

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company_name'], payload['company_name'])

    def test_get_startup_detail(self):
        """
        Test: retrieve detailed information about a specific startup.
        """
        view = StartupProfileDetailAPIView.as_view()

        request = self.factory.get(f'/api/startups/{self.startup.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.startup.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], self.startup.company_name)

    def test_update_startup(self):
        """
        Test: update an existing startup.
        """
        view = StartupProfileDetailAPIView.as_view()
        payload = {
            "company_name": "Updated Startup",
            "description": "Updated startup description.",
            "contact_email": "updated@example.com"
        }

        request = self.factory.put(f'/api/startups/{self.startup.id}/', payload)
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.startup.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], payload['company_name'])

    def test_delete_startup(self):
        """
        Test: delete an existing startup.
        """
        view = StartupProfileDetailAPIView.as_view()

        request = self.factory.delete(f'/api/startups/{self.startup.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.startup.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProfile.objects.filter(pk=self.startup.id).exists())
