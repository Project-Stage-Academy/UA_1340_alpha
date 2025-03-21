from django.db import models

from users.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'Follow'),
        ('message', 'Message'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    )

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optimizing query speed by using indexes for searching
    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self) -> str:
        return f'{self.sender} -> {self.recipient} - ({self.notification_type})'

    def mark_notification_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
