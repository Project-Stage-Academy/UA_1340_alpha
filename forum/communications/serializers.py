from rest_framework import serializers

from .models import Message, Room


class RoomSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    participants = serializers.ListField(
        child=serializers.EmailField(), allow_empty=False
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        room = Room(**validated_data)
        room.save()
        return room


class CreateRoomSerializer(serializers.Serializer):
    participants = serializers.ListField(
        child=serializers.EmailField(), allow_empty=False
    )

    def create(self, validated_data):
        room = Room(**validated_data)
        room.save()
        return room


class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    room = serializers.CharField(source="room.id", read_only=True)
    sender = serializers.EmailField(read_only=True)
    text = serializers.CharField()
    timestamp = serializers.DateTimeField(read_only=True)


class CreateMessageSerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    text = serializers.CharField(max_length=1000)

    def validate_conversation_id(self, value):
        try:
            Room.objects.get(id=value)  # Перевірка існування кімнати
        except Room.DoesNotExist:
            raise serializers.ValidationError("Conversation not found.")
        return value

    def create(self, validated_data):
        room = Room.objects.get(id=validated_data['conversation_id'])
        message = Message(
            room=room,
            sender=self.context['request'].user.email,
            text=validated_data['text']
        )
        message.save()
        return message
