from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum

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
    share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=Decimal('0.00'),
        help_text="Share of investment in percentage (0 - 100%)"
    )

    class Meta:
        unique_together = ('investor', 'startup')

    def __str__(self):
        return f"{self.investor.company_name} - {self.startup.company_name}"


class InvestorTrackedProject(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='tracked_projects')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='investor_tracks')
    share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=Decimal('0.00'),
        help_text="Share of investment in percentage (0 - 100%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['investor', 'project'], name='unique_investor_project')
        ]

    def clean(self):
        total_share = (
            InvestorTrackedProject.objects.filter(project=self.project)
            .exclude(pk=self.pk)
            .aggregate(total=Sum('share'))['total'] or Decimal('0.00')
        ) + self.share

        if total_share > 100:
            raise ValidationError(
                f"The total share of all investors for this project cannot exceed 100%. Current total: {total_share}%"
            )

    def __str__(self):
        return f"{self.investor.company_name} - {self.project.title} - {self.share}%"
