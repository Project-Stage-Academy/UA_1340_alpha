from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from users.models import User
from projects.models import Project
from startups.models import StartupProfile
from investors.models import InvestorProfile


def get_expiration_date():
    return now() + timedelta(days=45)


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('project_follow', 'Project follower changed'),
        ('investor_follow', 'Investor follows startup'),
        ('startup_follow', 'Startup follower changed'),
        ('project_profile_update', 'Project profile update'),
        ('startup_profile_update', 'Startup profile update'),
        ('investor_profile_update', 'Investor profile update'),
        ('system_message', 'System message'),
    ]

    INITIATOR_CHOICES = [
        ('investor', 'Investor'),
        ('startup', 'Startup'),
        ('project', 'Project'),
        ('system', 'System'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, related_name='notifications', null=True)
    startup = models.ForeignKey(
        StartupProfile, on_delete=models.SET_NULL, related_name='notifications', null=True)
    investor = models.ForeignKey(
        InvestorProfile, on_delete=models.SET_NULL, related_name='notifications', null=True)
    trigger = models.CharField(
        max_length=40, choices=NOTIFICATION_TYPES, db_index=True)
    initiator = models.CharField(
        max_length=40, choices=INITIATOR_CHOICES)
    priority = models.CharField(
        max_length=40, choices=PRIORITY_CHOICES, default='low', db_index=True)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_notifications', db_index=True)
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='sent_notifications', null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(default=get_expiration_date)

    # Optimizing query speed by using indexes for searching
    class Meta:
        indexes = [
            models.Index(
                fields=['recipient', 'is_read', 'priority', 'trigger']),
        ]

    def __str__(self) -> str:
        return f'Notification {self.trigger} for {self.initiator} sent by {self.sender}'

    def mark_notification_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
