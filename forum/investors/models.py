from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from startups.models import Industry, StartupProfile
from users.models import User


class InvestorProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investor_profile')
    company_name = models.CharField(max_length=255)
    investment_focus = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    investment_range = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    investor_logo = models.ImageField(upload_to='investor_logos/', blank=True, null=True)

    def __str__(self):
        return self.company_name


class InvestorPreferredIndustry(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='preferred_industries')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='investors')

    class Meta:
        unique_together = ('investor', 'industry')

    def __str__(self):
        return f"{self.investor.company_name} - {self.industry.name}"


class InvestorSavedStartup(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='saved_startups')
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='investor_saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'startup')

    def __str__(self):
        return f"{self.investor.company_name} - {self.startup.company_name}"


class InvestorTrackedProject(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='tracked_projects')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='investor_tracks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'project')

    def __str__(self):
        return f"{self.investor.company_name} - {self.project.title}"
