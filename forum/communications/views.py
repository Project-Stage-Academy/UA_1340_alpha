from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Communication
from .serializers import CommunicationsSerializer, CreateCommunicationsSerializer


class CommunicationsApiView(APIView):
    """
    Handles listing all communications (GET) and creating a new communication (POST).
    """
    def get(self, request: Request):
        try:
            communications = Communication.objects.all()

            serializer = CommunicationsSerializer(communications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "An error occurred while retrieving communications."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request):
        try:
            if not request.data:
                err_msg = "Empty request body"
                return Response({"error": err_msg}, status=status.HTTP_400_BAD_REQUEST)

            serializer = CreateCommunicationsSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            # Save the communication with sender as the authenticated user
            serializer.save(sender=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommunicationDetailApiView(APIView):
    """
    Handles retrieving (GET), updating (PUT), and deleting (DELETE) a specific communication by ID.
    """
    def get(self, request: Request, communication_id: int):
        try:
            # Fetch communication by ID, ensuring the user is either the sender or receiver
            communication = Communication.objects.filter(
                id=communication_id, sender=request.user
            ) | Communication.objects.filter(id=communication_id, receiver=request.user)

            communication = communication.first()

            if not communication:
                return Response({"error": "Communication not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = CommunicationsSerializer(communication)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "An error occurred while retrieving communication."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request: Request, communication_id: int):
        try:
            communication = Communication.objects.filter(
                id=communication_id, sender=request.user
            ).first()

            if not communication:
                return Response(
                    {"error": "Communication not found or you do not have permission to edit it."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CreateCommunicationsSerializer(communication, data=request.data, partial=True, context={'request': request})
            if not serializer.is_valid():
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred while updating communication: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request: Request, communication_id: int):
        try:
            communication = Communication.objects.filter(id=communication_id).first()

            if not communication:
                return Response(
                    {"error": "Communication not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check delete permission
            if communication.sender != request.user and communication.receiver != request.user:
                return Response(
                    {"error": "You do not have permission to delete this communication."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Delete the communication
            communication.delete()
            return Response({"message": "Communication deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"error": f"An error occurred while deleting communication: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
