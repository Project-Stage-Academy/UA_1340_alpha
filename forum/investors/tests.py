from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from investors.models import (
    InvestorPreferredIndustry,
    InvestorProfile,
    InvestorSavedStartup,
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


class BaseSavedStartupsAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email='investor1@example.com',
            password='SecurePassword123',
            first_name="John1",
            last_name="Doe1",
            is_investor=True,
            is_startup=True,
        )

        cls.user2 = User.objects.create_user(
            email='investor2@example.com',
            password='SecurePassword123',
            first_name="John2",
            last_name="Doe2",
            is_investor=True,
            is_startup=True,
        )

        cls.user3 = User.objects.create_user(
            email='startup1@example.com',
            password='SecurePassword123',
            first_name="John3",
            last_name="Doe3",
            is_startup=True,
        )

        cls.user4 = User.objects.create_user(
            email='startup2@example.com',
            password='SecurePassword123',
            first_name="John4",
            last_name="Doe4",
            is_startup=True,
        )

        cls.investor_profile1 = InvestorProfile.objects.create(
            user=cls.user1,
            company_name="Test Company",
            investment_focus="Technology",
            contact_email="investor1@example.com",
            investment_range="100000-500000"
        )

        cls.investor_profile2 = InvestorProfile.objects.create(
            user=cls.user2,
            company_name="Test Company 2",
            investment_focus="Finance",
            contact_email="investor2@example.com",
            investment_range="500000-1000000"
        )

        cls.startup1 = StartupProfile.objects.create(
            user=cls.user2,
            company_name="HealthTech Startup",
            description="A healthcare technology startup.",
            contact_email="healthtech@example.com"
        )

        cls.startup2 = StartupProfile.objects.create(
            user=cls.user3,
            company_name="EduTech Startup",
            description="An educational technology startup.",
            contact_email="edutech@example.com"
        )

        cls.startup3 = StartupProfile.objects.create(
            user=cls.user4,
            company_name="Untracked Startup",
            description="A startup not saved by the investor.",
            contact_email="untracked@example.com"
        )

        InvestorSavedStartup.objects.create(
            investor=cls.investor_profile1,
            startup=cls.startup1,
        )

        InvestorSavedStartup.objects.create(
            investor=cls.investor_profile1,
            startup=cls.startup2,
        )


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
        # print(request)
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


class SavedStartupsApiViewTests(BaseSavedStartupsAPITestCase):

    def setUp(self):
        self.url = reverse('saved-startups')

    def test_get_saved_startups_with_no_saved_startups_returns_200(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_saved_startups_with_no_investor_profile_returns_404(self):
        self.client.force_authenticate(user=self.user3)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Investor profile not found")

    def test_get_saved_startups_unexpected_exception_returns_500(self):
        self.client.force_authenticate(user=self.user1)
        with patch(
            "investors.models.InvestorProfile.objects.get",
            side_effect=Exception("Unexpected error"),
        ):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data["error"], "Unexpected error")

    def test_get_saved_startups_with_valid_search_term_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            self.url,
            {"search": "HealthTech", "search_field": "company_name"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")

    def test_get_saved_startups_sorted_descending_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            self.url,
            {"sort": "-company_name"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")
        self.assertEqual(response.data[1]["company_name"], "EduTech Startup")

    def test_get_saved_startups_with_default_search_field_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            self.url,
            {"search": "HealthTech"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")

    def test_get_saved_startups_filtered_by_description_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            self.url,
            {"search": "healthcare technology", "search_field": "description"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["description"], "A healthcare technology startup.")

    def test_get_saved_startups_without_search_or_sort_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")
        self.assertEqual(response.data[1]["company_name"], "EduTech Startup")

    def test_get_saved_startups_with_invalid_search_field_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            self.url,
            {"search": "HealthTech", "search_field": "invalid_field"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return all startups since the search field is invalid
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")
        self.assertEqual(response.data[1]["company_name"], "EduTech Startup")

    def test_get_saved_startups_with_invalid_sort_field_returns_200(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            self.url,
            {"sort": "invalid_field"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")
        self.assertEqual(response.data[1]["company_name"], "EduTech Startup")


class CreateDeleteSavedStartupApiViewTests(BaseSavedStartupsAPITestCase):

    def setUp(self):
        self.get_url = reverse('saved-startups')

    def test_save_already_saved_startup_returns_400(self):
        self.client.force_authenticate(user=self.user2)

        saved_startup = InvestorSavedStartup.objects.create(
            investor=self.investor_profile2,
            startup=self.startup1,
        )

        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["company_name"], "HealthTech Startup")

        url = reverse('save-delete-startup', kwargs={'startup_id': self.startup1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Startup is already saved by the investor")

        saved_startup.delete()
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_save_non_existent_startup_profile_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        non_existent_startup_id = 9999

        url = reverse('save-delete-startup', kwargs={'startup_id': non_existent_startup_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Startup profile not found")

    def test_delete_non_existent_startup_profile_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        non_existent_startup_id = 9999

        url = reverse('save-delete-startup', kwargs={'startup_id': non_existent_startup_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Startup profile not found")

    def test_delete_unsaved_startup_returns_404(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse('save-delete-startup', kwargs={'startup_id': self.startup3.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Saved startup not found")

    def test_save_startup_unexpected_exception_returns_500(self):
        self.client.force_authenticate(user=self.user1)

        with patch(
                "investors.models.InvestorProfile.objects.get",
                side_effect=Exception("Unexpected error")
        ):
            url = reverse('save-delete-startup', kwargs={'startup_id': self.startup1.id})
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error'], "Unexpected error")

    def test_delete_startup_unexpected_exception_returns_500(self):
        self.client.force_authenticate(user=self.user1)

        with patch(
                "investors.models.InvestorProfile.objects.get",
                side_effect=Exception("Unexpected error")
        ):
            url = reverse('save-delete-startup', kwargs={'startup_id': self.startup1.id})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error'], "Unexpected error")

    def test_delete_startup_with_non_existent_investor_profile_returns_404(self):
        self.client.force_authenticate(user=self.user3)

        url = reverse('save-delete-startup', kwargs={'startup_id': self.startup1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Investor profile not found")

    def test_save_startup_with_non_existent_investor_profile_returns_404(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('save-delete-startup', kwargs={'startup_id': self.startup1.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Investor profile not found")

    def test_delete_saved_startup_returns_204(self):
        self.client.force_authenticate(user=self.user1)

        saved_startup = InvestorSavedStartup.objects.create(
            investor=self.investor_profile1,
            startup=self.startup3
        )
        self.assertTrue(InvestorSavedStartup.objects.filter(pk=saved_startup.id).exists())

        url = reverse('save-delete-startup', kwargs={'startup_id': self.startup3.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(InvestorSavedStartup.objects.filter(pk=saved_startup.id).exists())

    def test_save_new_startup_returns_201(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse('save-delete-startup', kwargs={'startup_id': self.startup3.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['startup'], self.startup3.id)
        self.assertTrue(
            InvestorSavedStartup.objects.filter(
                investor=self.investor_profile1,
                startup=self.startup3
            ).exists()
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            InvestorSavedStartup.objects.filter(
                investor=self.investor_profile1,
                startup=self.startup3
            ).exists()
        )
