from rest_framework import serializers
from .models import *
from users.serializers import UserSerializer

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

    def validate(self, data):
        if data['sender'].id == data['receiver'].id:
            raise serializers.ValidationError("The sender and the recipient may not be the same person.")
        return data
