from django.db import models
import uuid
from startups.models import StartupProfile

class Project(models.Model):
    STATUS_CHOICES = [
        ('Seeking Funding', 'Seeking Funding'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    funding_goal = models.DecimalField(max_digits=10, decimal_places=2)
    funding_needed = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Doesn't include fields for business_plan, media_files.

    def __str__(self):
        return self.title
