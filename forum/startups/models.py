from django.db import models


class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name


class StartupProfile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='startup_profile')
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    startup_logo = models.ImageField(upload_to='startup_logos/', blank=True, null=True)

    # ForeignKey to Industry
    industries = models.ManyToManyField(Industry, blank=True, related_name='startups')

    def __str__(self):
        return self.company_name


class StartupIndustry(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='industry_links')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='startup_links')

    class Meta:
        unique_together = ('startup', 'industry')

    def __str__(self):
        return f"{self.startup.company_name} - {self.industry.name}"
