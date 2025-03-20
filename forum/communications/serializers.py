from rest_framework import serializers
from .models import Communication
from users.serializers import UserSerializer


class CommunicationsSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Communication
        fields = '__all__'
        read_only_fields = ('id', 'is_read', 'created_at')


class CreateCommunicationsSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Communication
        fields = ['id', 'sender', 'receiver', 'content']
        read_only_fields = ('id',)

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request object is required.")

        sender = request.user
        receiver = data.get('receiver')

        if not receiver:
            raise serializers.ValidationError({"receiver": "Receiver is required."})
        if sender == receiver:
            raise serializers.ValidationError({"receiver": "The sender and the recipient may not be the same person."})
        return data

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

