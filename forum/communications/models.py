from datetime import datetime

from django.db import models
from mongoengine import (
    DateTimeField,
    Document,
    EmailField,
    ListField,
    ReferenceField,
    StringField,
)

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


class Room(Document):
    participants = ListField(EmailField(required=True), required=True)  # Зберігаємо email учасників
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def add_participant(self, email):
        if email not in self.participants:
            self.participants.append(email)
            self.updated_at = datetime.now()
            self.save()

    def remove_participant(self, email):
        if email in self.participants:
            self.participants.remove(email)
            self.updated_at = datetime.now()
            self.save()

    def __str__(self):
        return f"Room with {self.participants}"

class Message(Document):
    room = ReferenceField(Room, required=True)
    sender = EmailField(required=True)
    text = StringField(required=True, max_length=1000)
    timestamp = DateTimeField(default=datetime.now)

    def __str__(self):
        return f"[{self.timestamp}] {self.sender}: {self.text}"


