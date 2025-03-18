from django.core.exceptions import ValidationError
from django.db import models

from startups.models import StartupProfile


class Project(models.Model):
    STATUS_CHOICES = [
        ('Seeking Funding', 'Seeking Funding'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    id = models.AutoField(primary_key=True)
    startup = models.ForeignKey(
        StartupProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField()
    funding_goal = models.DecimalField(max_digits=10, decimal_places=2)
    funding_needed = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business_plan = models.FileField(
        upload_to='project_business_plans/', blank=True, null=True)
    media_files = models.FileField(
        upload_to='project_media/', blank=True, null=True)

    def clean(self):
        """Ensure funding_needed is not greater than funding_goal"""
        if self.funding_needed > self.funding_goal:
            raise ValidationError("Funding needed cannot exceed funding goal.")

    def __str__(self):
        return f"{self.title} | {self.startup.company_name} | {self.get_status_display()}"
