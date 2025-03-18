import random

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from faker import Faker
from investors.models import (
    InvestorPreferredIndustry,
    InvestorProfile,
    InvestorSavedStartup,
)
from projects.models import Project
from startups.models import Industry, StartupProfile
from users.models import User

fake = Faker()


class Command(BaseCommand):
    help = "Populate database with fake data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database population..."))

        # Create industries

        industry = ["Tech", "Healthcare", "Finance", "Real Estate", "Energy"]
        industries = [Industry.objects.create(name=name) for name in industry]
        self.stdout.write(self.style.SUCCESS("Industries created."))

        # Create users
        users = [
            User(
                email=fake.email(),
                password=make_password("password123"),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=random.choice(['startup', 'investor']),
                is_email_confirmed=True
            )
            for _ in range(10)
        ]
        User.objects.bulk_create(users)
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

        investor_industries = [
            InvestorPreferredIndustry(investor=investor, industry=industry)
            for investor in investors
            for industry in random.sample(industries, k=random.randint(1, 3))
        ]
        InvestorPreferredIndustry.objects.bulk_create(investor_industries)

        # Investors save startups
        for investor in investors:
            saved_startups = random.sample(startups, k=random.randint(1, 3))
            InvestorSavedStartup.objects.bulk_create([
                InvestorSavedStartup(investor=investor, startup=startup)
                for startup in saved_startups
            ])
        self.stdout.write(self.style.SUCCESS("Investor saved startups created."))

        # Create projects
        projects = [
            Project(
                startup=startup,
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                funding_goal=random.uniform(10000, 500000),
                funding_needed=random.uniform(1000, 100000),
                status=random.choice(['Seeking Funding', 'In Progress', 'Completed']),
                duration=random.randint(1, 24)
            )
            for startup in startups
            for _ in range(random.randint(1, 3))
        ]
        Project.objects.bulk_create(projects)
        self.stdout.write(self.style.SUCCESS("Projects created."))

        self.stdout.write(self.style.SUCCESS("Database population completed."))
