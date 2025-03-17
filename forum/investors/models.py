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
    share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Share of investment in percentage (0 - 100%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'startup')

    def clean(self):
        # Ensure that the sum of all investor shares does not exceed 100% for a specific startup
        total_share = sum(
            investor_share.share for investor_share in InvestorSavedStartup.objects.filter(startup=self.startup)
        ) + self.share

        if total_share > 100:
            raise ValidationError(
                f"The total share of all investors for this startup cannot exceed 100%. Current total: {total_share}%")

    def __str__(self):
        return f"{self.investor.company_name} - {self.startup.company_name} - {self.share}%"


class InvestorTrackedProject(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='tracked_projects')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='investor_tracks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'project')

    def __str__(self):
        return f"{self.investor.company_name} - {self.project.title}"
