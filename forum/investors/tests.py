from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from investors.models import (
    InvestorPreferredIndustry,
    InvestorProfile,
    InvestorTrackedProject,
)
from investors.views import (
    InvestorPreferredIndustryApiView,
    InvestorPreferredIndustryDetailApiView,
    InvestorProfileApiView,
    InvestorProfileDetailApiView,
    InvestorTrackedProjectApiView,
    InvestorTrackedProjectDetailApiView,
)
from projects.models import Project
from startups.models import Industry, StartupProfile
from users.models import User


class InvestorProfileApiTests(APITestCase):

    def setUp(self):
        """
        Set up the test environment.
        """
        # Create test users
        self.user1 = User.objects.create_user(
            first_name="testuser1",
            last_name="testuser1",
            password="password1",
            email="test1@example.com",
            is_investor="True"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2",
            last_name="testuser2",
            password="password2",
            email="test2@example.com",
            is_investor="True"
        )

        # Create an investor profile
        self.investor_profile = InvestorProfile.objects.create(
            user=self.user1,
            company_name="Test Company",
            investment_focus="Technology",
            contact_email="test1@example.com",
            investment_range="100000-500000"
        )

        # Initialize the request factory
        self.factory = APIRequestFactory()

    def test_create_investor_profile(self):
        """
        Test: Create a new investor profile.
        """
        view = InvestorProfileApiView.as_view()
        payload = {
            "company_name": "New Company",
            "investment_focus": "Healthcare",
            "contact_email": "new@example.com",
            "investment_range": "200000-600000",
        }

        # Create a POST request
        request = self.factory.post('/api/investors/investor-profiles/', payload)
        print(request)
        force_authenticate(request, user=self.user2)


        response = view(request)
        # print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company_name'], payload['company_name'])

    def test_get_investor_profiles(self):
        """
        Test: Retrieve a list of investor profiles.
        """
        view = InvestorProfileApiView.as_view()

        # Create a GET request
        request = self.factory.get('/api/investors/investor-profiles/')
        force_authenticate(request, user=self.user1)

        # Call the view
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], self.investor_profile.company_name)

    def test_get_investor_profile_detail(self):
        """
        Test: Retrieve detailed information about a profile.
        """
        view = InvestorProfileDetailApiView.as_view()

        # Create a GET request
        request = self.factory.get(f'/api/investors/investor-profiles/{self.investor_profile.id}/')
        force_authenticate(request, user=self.user1)

        # Call the view
        response = view(request, pk=self.investor_profile.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], self.investor_profile.company_name)

    def test_update_investor_profile(self):
        """
        Test: Update an existing investor profile.
        """
        view = InvestorProfileDetailApiView.as_view()
        payload = {
            "company_name": "Updated Company",
            "investment_focus": "Renewable Energy",
            "contact_email": "updated@example.com",
            "investment_range": "300000-700000",
        }

        # Create a PUT request
        request = self.factory.put(f'/api/investors/investor-profiles/{self.investor_profile.id}/', payload)
        force_authenticate(request, user=self.user1)

        # Call the view
        response = view(request, pk=self.investor_profile.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], payload['company_name'])

    def test_delete_investor_profile(self):
        """
        Test: Delete an existing investor profile.
        """
        view = InvestorProfileDetailApiView.as_view()

        # Create a DELETE request
        request = self.factory.delete(f'/api/investors/investor-profiles/{self.investor_profile.id}/')
        force_authenticate(request, user=self.user1)

        # Call the view
        response = view(request, pk=self.investor_profile.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the profile has been deleted
        self.assertFalse(InvestorProfile.objects.filter(pk=self.investor_profile.id).exists())

class InvestorPreferredIndustryApiTests(APITestCase):

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            is_investor="True"
        )

        self.investor_profile = InvestorProfile.objects.create(
            user=self.user,
            company_name="Test Company",
            investment_focus="Technology",
            contact_email="test@example.com",
            investment_range="100000-500000"
        )

        self.industry = Industry.objects.create(
            name="Technology",
        )

        self.investor_preferred_industry = InvestorPreferredIndustry.objects.create(
            investor=self.investor_profile,
            industry=self.industry
        )

        self.factory = APIRequestFactory()

    def test_get_investor_preferred_industries(self):
        """
        Test: Retrieve a list of industries.
        """
        view = InvestorPreferredIndustryApiView.as_view()

        request = self.factory.get('/api/investors/investor-preferred-industries/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data[0]['industry']['id'], self.industry.id)

    def test_create_investor_preferred_industry(self):
        """
        Test: Create a new industry.
        """
        view = InvestorPreferredIndustryApiView.as_view()
        new_industry = Industry.objects.create(
            name="Healthcare",
        )
        payload = {
            "investor": self.investor_profile.id,
            "industry": new_industry.id
        }

        request = self.factory.post('/api/investors/investor-preferred-industries/', payload)
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['investor'], self.investor_profile.id)
        self.assertEqual(response.data['industry'], new_industry.id)

    def test_get_investor_preferred_industry_detail(self):
        """
        Test: Retrieve detailed information about an industry.
        """
        view = InvestorPreferredIndustryDetailApiView.as_view()

        request = self.factory.get(f'/api/investors/investor-preferred-industries/{self.investor_preferred_industry.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.investor_preferred_industry.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data['industry']['id'], self.industry.id)

    def test_delete_investor_preferred_industry(self):
        """
        Test: Delete an existing industry.
        """
        view = InvestorPreferredIndustryDetailApiView.as_view()

        request = self.factory.delete(f'/api/investors/investor-preferred-industries/{self.investor_preferred_industry.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.investor_preferred_industry.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(InvestorPreferredIndustry.objects.filter(pk=self.investor_preferred_industry.id).exists())

class InvestorTrackedProjectApiTests(APITestCase):

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            is_investor="True"
        )

        self.investor_profile = InvestorProfile.objects.create(
            user=self.user,
            company_name="Test Company",
            investment_focus="Technology",
            contact_email="test@example.com",
            investment_range="100000-500000"
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name="Test Startup",
            description="A test startup.",
            contact_email="teststartup@example.com"
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title="Project One",
            description="A test project.",
            funding_goal=100000.00,
            funding_needed=50000.00,
            status="Seeking Funding",
            duration=12
        )

        self.tracked_project = InvestorTrackedProject.objects.create(
            investor=self.investor_profile,
            project=self.project
        )

        self.factory = APIRequestFactory()

    def test_get_investor_tracked_projects(self):
        """
        Test: Retrieve a list of tracked projects.
        """
        view = InvestorTrackedProjectApiView.as_view()

        request = self.factory.get('/api/investors/investor-tracked-projects/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data[0]['project']['id'], self.project.id)

    def test_create_investor_tracked_project(self):
        """
        Test: Create a new tracked project.
        """
        view = InvestorTrackedProjectApiView.as_view()

        new_project = Project.objects.create(
            startup=self.startup,
            title="Project Two",
            description="Another test project.",
            funding_goal=200000.00,
            funding_needed=150000.00,
            status="Seeking Funding",
            duration=18
        )
        payload = {
            "investor": self.investor_profile.id,
            "project": new_project.id
        }

        request = self.factory.post('/api/investors/investor-tracked-projects/', payload)
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['investor'], self.investor_profile.id)
        self.assertEqual(response.data['project'], new_project.id)

    def test_get_investor_tracked_project_detail(self):
        """
        Test: Retrieve detailed information about a tracked project.
        """
        view = InvestorTrackedProjectDetailApiView.as_view()

        request = self.factory.get(f'/api/investors/investor-tracked-projects/{self.tracked_project.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.tracked_project.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data['project']['id'], self.project.id)

    def test_delete_investor_tracked_project(self):
        """
        Test: Delete an existing tracked project.
        """
        view = InvestorTrackedProjectDetailApiView.as_view()

        request = self.factory.delete(f'/api/investors/investor-tracked-projects/{self.tracked_project.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.tracked_project.id)
        # print(response.data)  # For debugging
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(InvestorTrackedProject.objects.filter(pk=self.tracked_project.id).exists())

