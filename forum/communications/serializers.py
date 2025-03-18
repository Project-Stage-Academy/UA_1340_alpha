from rest_framework import serializers
from users.serializers import UserSerializer

from .models import *


class CommunicationsSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Communication
        fields = '__all__'
        read_only_fields = ('id', 'is_read', 'created_at')


class CreateCommunicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
        fields = ['id', 'sender', 'receiver', 'content']
        read_only_fields = ('id',)

    def validate(self, data):
        sender = data.get('sender')
        receiver = data.get('receiver')

        if not sender or not receiver:
            raise serializers.ValidationError("Both sender and receiver are required.")

        if sender.id == receiver.id:
            raise serializers.ValidationError("The sender and the recipient may not be the same person.")

        return data

