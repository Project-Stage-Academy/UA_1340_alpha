from django.db import models

from users.models import User


class Communication(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=False, null=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.email} to {self.receiver.email} - {self.content[:50]}"

    def mark_as_read(self):
        """Mark the message as read and save changes."""
        self.is_read = True
        self.save(update_fields=['is_read'])
