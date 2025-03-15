from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from startups.models import Industry, StartupProfile
from users.models import User
from projects.models import Project
from investors.models import InvestorProfile, InvestorPreferredIndustry, InvestorSavedStartup, InvestorTrackedProject
from investors.views import *

class InvestorProfileApiTests(APITestCase):

    def setUp(self):
        """
        Налаштування тестового середовища.
        """
        # Створення тестових користувачів
        self.user1 = User.objects.create_user(
            first_name="testuser1",
            last_name="testuser1",
            password="password1",
            email="test1@example.com",
            role="investor"
        )
        self.user2 = User.objects.create_user(
            first_name="testuser2",
            last_name="testuser2",
            password="password2",
            email="test2@example.com",
            role="investor"
        )

        # Створення профілю інвестора
        self.investor_profile = InvestorProfile.objects.create(
            user=self.user1,
            company_name="Test Company",
            investment_focus="Technology",
            contact_email="test1@example.com",
            investment_range="100000-500000"
        )

        # Ініціалізація фабрики запитів
        self.factory = APIRequestFactory()

    def test_get_investor_profiles(self):
        """
        Тест: отримання списку інвесторських профілів.
        """
        view = InvestorProfileApiView.as_view()

        # Створюємо GET-запит
        request = self.factory.get('/api/investors/investor-profiles/')
        force_authenticate(request, user=self.user1)

        # Викликаємо view
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], self.investor_profile.company_name)

    def test_create_investor_profile(self):
        """
        Тест: створення нового інвесторського профілю.
        """
        view = InvestorProfileApiView.as_view()
        payload = {
            "company_name": "New Company",
            "investment_focus": "Healthcare",
            "contact_email": "new@example.com",
            "investment_range": "200000-600000",
        }

        # Створюємо POST-запит
        request = self.factory.post('/api/investors/investor-profiles/', payload)
        force_authenticate(request, user=self.user2)

        # Викликаємо view
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company_name'], payload['company_name'])

    def test_get_investor_profile_detail(self):
        """
        Тест: отримання детальної інформації про профіль.
        """
        view = InvestorProfileDetailApiView.as_view()

        # Створюємо GET-запит
        request = self.factory.get(f'/api/investors/investor-profiles/{self.investor_profile.id}/')
        force_authenticate(request, user=self.user1)

        # Викликаємо view
        response = view(request, pk=self.investor_profile.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], self.investor_profile.company_name)

    def test_update_investor_profile(self):
        """
        Тест: оновлення існуючого інвесторського профілю.
        """
        view = InvestorProfileDetailApiView.as_view()
        payload = {
            "company_name": "Updated Company",
            "investment_focus": "Renewable Energy",
            "contact_email": "updated@example.com",
            "investment_range": "300000-700000",
        }

        # Створюємо PUT-запит
        request = self.factory.put(f'/api/investors/investor-profiles/{self.investor_profile.id}/', payload)
        force_authenticate(request, user=self.user1)

        # Викликаємо view
        response = view(request, pk=self.investor_profile.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], payload['company_name'])

    def test_delete_investor_profile(self):
        """
        Тест: видалення існуючого інвесторського профілю.
        """
        view = InvestorProfileDetailApiView.as_view()

        # Створюємо DELETE-запит
        request = self.factory.delete(f'/api/investors/investor-profiles/{self.investor_profile.id}/')
        force_authenticate(request, user=self.user1)

        # Викликаємо view
        response = view(request, pk=self.investor_profile.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Перевіряємо, чи профіль справді видалено
        self.assertFalse(InvestorProfile.objects.filter(pk=self.investor_profile.id).exists())

class InvestorPreferredIndustryApiTests(APITestCase):

    def setUp(self):
        """
        Налаштування тестового середовища.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            role="investor"
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
        Тест: отримання списку індустрій.
        """
        view = InvestorPreferredIndustryApiView.as_view()

        request = self.factory.get('/api/investors/investor-preferred-industries/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data[0]['industry']['id'], self.industry.id)

    def test_create_investor_preferred_industry(self):
        """
        Тест: створення нової індустрії.
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
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['investor'], self.investor_profile.id)
        self.assertEqual(response.data['industry'], new_industry.id)

    def test_get_investor_preferred_industry_detail(self):
        """
        Тест: отримання детальної інформації про індустрію.
        """
        view = InvestorPreferredIndustryDetailApiView.as_view()

        request = self.factory.get(f'/api/investors/investor-preferred-industries/{self.investor_preferred_industry.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.investor_preferred_industry.id)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data['industry']['id'], self.industry.id)

    def test_delete_investor_preferred_industry(self):
        """
        Тест: видалення існуючої індустрії.
        """
        view = InvestorPreferredIndustryDetailApiView.as_view()

        request = self.factory.delete(f'/api/investors/investor-preferred-industries/{self.investor_preferred_industry.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.investor_preferred_industry.id)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(InvestorPreferredIndustry.objects.filter(pk=self.investor_preferred_industry.id).exists())

class InvestorSavedStartupApiTests(APITestCase):

    def setUp(self):
        """
        Налаштування тестового середовища.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            role="investor"
        )

        self.investor_profile = InvestorProfile.objects.create(
            user=self.user,
            company_name="Test Company",
            investment_focus="Technology",
            contact_email="test@example.com",
            investment_range="100000-500000"
        )

        self.startup_profile = StartupProfile.objects.create(
            user=self.user,
            company_name="Startup One",
            description="An innovative startup.",
            contact_email="test@example.com",
        )

        self.saved_startup = InvestorSavedStartup.objects.create(
            investor=self.investor_profile,
            startup=self.startup_profile
        )

        self.factory = APIRequestFactory()

    def test_get_investor_saved_startups(self):
        """
        Тест: отримання списку збережених стартапів.
        """
        view = InvestorSavedStartupApiView.as_view()

        request = self.factory.get('/api/investors/investor-saved-startups/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data[0]['startup']['id'], self.startup_profile.id)

    def test_create_investor_saved_startup(self):
        """
        Тест: створення нового збереженого стартапу.
        """
        view = InvestorSavedStartupApiView.as_view()

        new_user = User.objects.create_user(
            first_name="newuser",
            last_name="newuser",
            password="newpassword",
            email="newuser@example.com",
            role="startup"
        )

        new_startup = StartupProfile.objects.create(
            user=new_user,
            company_name="Startup Two",
            description="Another innovative startup.",
            contact_email="startuptwo@example.com"
        )

        payload = {
            "investor": self.investor_profile.id,
            "startup": new_startup.id
        }

        request = self.factory.post('/api/investors/investor-saved-startups/', payload)
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['investor'], self.investor_profile.id)
        self.assertEqual(response.data['startup'], new_startup.id)

    def test_get_investor_saved_startup_detail(self):
        """
        Тест: отримання детальної інформації про збережений стартап.
        """
        view = InvestorSavedStartupDetailApiView.as_view()

        request = self.factory.get(f'/api/investors/investor-saved-startups/{self.saved_startup.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.saved_startup.id)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data['startup']['id'], self.startup_profile.id)

    def test_delete_investor_saved_startup(self):
        """
        Тест: видалення існуючого збереженого стартапу.
        """
        view = InvestorSavedStartupDetailApiView.as_view()

        request = self.factory.delete(f'/api/investors/investor-saved-startups/{self.saved_startup.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.saved_startup.id)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(InvestorSavedStartup.objects.filter(pk=self.saved_startup.id).exists())

class InvestorTrackedProjectApiTests(APITestCase):

    def setUp(self):
        """
        Налаштування тестового середовища.
        """
        self.user = User.objects.create_user(
            first_name="testuser",
            last_name="testuser",
            password="testpassword",
            email="test@example.com",
            role="investor"
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
        Тест: отримання списку відстежуваних проектів.
        """
        view = InvestorTrackedProjectApiView.as_view()

        request = self.factory.get('/api/investors/investor-tracked-projects/')
        force_authenticate(request, user=self.user)

        response = view(request)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data[0]['project']['id'], self.project.id)

    def test_create_investor_tracked_project(self):
        """
        Тест: створення нового відстежуваного проекту.
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
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['investor'], self.investor_profile.id)
        self.assertEqual(response.data['project'], new_project.id)

    def test_get_investor_tracked_project_detail(self):
        """
        Тест: отримання детальної інформації про відстежуваний проект.
        """
        view = InvestorTrackedProjectDetailApiView.as_view()

        request = self.factory.get(f'/api/investors/investor-tracked-projects/{self.tracked_project.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.tracked_project.id)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['investor']['id'], self.investor_profile.id)
        self.assertEqual(response.data['project']['id'], self.project.id)

    def test_delete_investor_tracked_project(self):
        """
        Тест: видалення існуючого відстежуваного проекту.
        """
        view = InvestorTrackedProjectDetailApiView.as_view()

        request = self.factory.delete(f'/api/investors/investor-tracked-projects/{self.tracked_project.id}/')
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.tracked_project.id)
        # print(response.data)  # Для діагностики
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(InvestorTrackedProject.objects.filter(pk=self.tracked_project.id).exists())
