from django.db import models
import uuid
from users.models import User
from startups.models import StartupProfile, Industry


class InvestorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investor_profile')
    company_name = models.CharField(max_length=255)
    investment_focus = models.CharField(max_length=255)
    contact_email = models.EmailField()
    investment_range = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


    # Doesn't include field for investor_logo.

    def __str__(self):
        return self.company_name


class InvestorPreferredIndustry(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('investor', 'industry')

    def __str__(self):
        return f"{self.investor.company_name} - {self.industry.name}"


class InvestorSavedStartup(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'startup')

    def __str__(self):
        return f"{self.investor.company_name} - {self.startup.company_name}"


class InvestorTrackedProject(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'project')

    def __str__(self):
        return f"{self.investor.company_name} - {self.project.title}"
