from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from projects.models import Project
from projects.views import ProjectDetailAPIView, ProjectListCreateAPIView
from startups.models import StartupProfile
from users.models import User


class ProjectApiTests(APITestCase):

    def setUp(self):
        """
        Setting up the test environment.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            is_startup="True"
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name="Test Startup",
            description="A test startup.",
            contact_email="teststartup@example.com"
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title="Test Project",
            description="A test project description.",
            funding_goal=100000.00,
            funding_needed=50000.00,
            status="Seeking Funding",
            duration=12
        )

        self.factory = APIRequestFactory()

    def test_get_project_list(self):
        """
        Test: retrieving a list of projects.
        """
        view = ProjectListCreateAPIView.as_view()

        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.project.title)

    def test_create_project(self):
        """
        Test: creating a new project.
        """
        view = ProjectListCreateAPIView.as_view()
        payload = {
            "startup": self.startup.id,
            "title": "New Project",
            "description": "Another test project.",
            "funding_goal": 200000.00,
            "funding_needed": 150000.00,
            "status": "Seeking Funding",
            "duration": 18
        }

        request = self.factory.post('/api/projects/', payload)
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])

    def test_get_project_detail(self):
        """
        Test: retrieving detailed information about a project.
        """
        view = ProjectDetailAPIView.as_view()

        request = self.factory.get(f'/api/projects/{self.project.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.project.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.project.title)

    def test_update_project(self):
        """
        Test: updating an existing project.
        """
        view = ProjectDetailAPIView.as_view()
        payload = {
            "title": "Updated Project Title",
            "description": "Updated description.",
            "funding_goal": 120000.00,
            "funding_needed": 60000.00,
            "status": "In Progress",
            "duration": 10
        }

        request = self.factory.put(f'/api/projects/{self.project.id}/', payload)
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.project.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], payload['title'])
