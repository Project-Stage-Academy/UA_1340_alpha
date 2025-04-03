from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message, Room
from .serializers import (
    CreateMessageSerializer,
    CreateRoomSerializer,
    MessageSerializer,
    RoomSerializer,
)


class CreateConversationApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Create a new conversation",
        request_body=CreateRoomSerializer,
        responses={
            201: RoomSerializer,
            400: "Bad Request: Invalid data.",
        },
    )
    def post(self, request):
        """
        Create a new conversation.
        """
        serializer = CreateRoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SendMessageApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Send a message",
        request_body=CreateMessageSerializer,
        responses={
            201: MessageSerializer,
            400: "Bad Request: Invalid input data.",
            404: "Conversation not found.",
        },
    )
    def post(self, request):
        """
        Send a message within a conversation.
        """
        serializer = CreateMessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ListMessagesApiView(APIView):
    @swagger_auto_schema(
        operation_summary="List messages in a conversation",
        manual_parameters=[
            openapi.Parameter(
                "conversation_id",
                openapi.IN_PATH,
                description="ID of the conversation",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: MessageSerializer(many=True),
            404: "Conversation not found.",
        },
    )
    def get(self, request, conversation_id):
        """
        Retrieve all messages for a specific conversation.
        """
        try:
            room = Room.objects.get(id=conversation_id)
        except Room.DoesNotExist:
            return Response(
                {"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND
            )

        messages = Message.objects.filter(room=room).order_by("timestamp")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
