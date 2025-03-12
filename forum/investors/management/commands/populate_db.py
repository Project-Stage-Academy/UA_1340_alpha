import random
from django.core.management.base import BaseCommand
from faker import Faker
from users.models import User
from startups.models import StartupProfile, Industry, StartupIndustry
from investors.models import InvestorProfile, InvestorPreferredIndustry, InvestorSavedStartup
from projects.models import Project

fake = Faker()


class Command(BaseCommand):
    help = "Populate database with fake data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database population..."))

        # Create industries

        industry = ["Tech", "Healthcare", "Finance", "Real Estate", "Energy"]
        industries = [Industry.objects.create(name=industry[_]) for _ in range(5)]
        self.stdout.write(self.style.SUCCESS("Industries created."))

        # Create users
        users = []
        for _ in range(10):
            role = random.choice(['startup', 'investor'])
            user = User.objects.create_user(
                email=fake.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=role,
                is_email_confirmed=True
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS("Users created."))

        # Create startup profiles
        startups = []
        for user in [u for u in users if u.role == 'startup']:
            startup = StartupProfile.objects.create(
                user=user,
                company_name=fake.company(),
                description=fake.text(),
                website=fake.url(),
                contact_email=fake.email()
            )
            startup.industries.set(random.sample(industries, k=random.randint(1, 3)))
            startups.append(startup)
        self.stdout.write(self.style.SUCCESS("Startup profiles created."))

        # Create investor profiles
        investors = []
        for user in [u for u in users if u.role == 'investor']:
            investor = InvestorProfile.objects.create(
                user=user,
                company_name=fake.company(),
                investment_focus=fake.word(),
                contact_email=fake.email(),
                investment_range=f"${random.randint(10000, 500000)}"
            )
            investors.append(investor)
        self.stdout.write(self.style.SUCCESS("Investor profiles created."))

        # Assign industries to investors

        for investor in investors:
            selected_industries = random.sample(industries, k=random.randint(1, 3))  # Ensure unique selections
            for industry in selected_industries:
                InvestorPreferredIndustry.objects.get_or_create(
                    investor=investor,
                    industry=industry
                )

        # Investors save startups
        for investor in investors:
            for _ in range(random.randint(1, 3)):
                InvestorSavedStartup.objects.get_or_create(
                    investor=investor,
                    startup=random.choice(startups)
                )
        self.stdout.write(self.style.SUCCESS("Investor saved startups created."))

        # Create projects
        for startup in startups:
            for _ in range(random.randint(1, 3)):
                Project.objects.create(
                    startup=startup,
                    title=fake.sentence(nb_words=4),
                    description=fake.text(),
                    funding_goal=random.uniform(10000, 500000),
                    funding_needed=random.uniform(1000, 100000),
                    status=random.choice(['Seeking Funding', 'In Progress', 'Completed']),
                    duration=random.randint(1, 24)
                )
        self.stdout.write(self.style.SUCCESS("Projects created."))

        self.stdout.write(self.style.SUCCESS("Database population completed."))
