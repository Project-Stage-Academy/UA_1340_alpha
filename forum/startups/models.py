from django.db import models
import uuid


class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name


class StartupProfile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='startup_profile')
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Doesn't include field for startup_logo.

    # ForeignKey to Industry
    industries = models.ManyToManyField(Industry, related_name='startups', blank=True)

    def __str__(self):
        return self.company_name


class StartupIndustry(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('startup', 'industry')
