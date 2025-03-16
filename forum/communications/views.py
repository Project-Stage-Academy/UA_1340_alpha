from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Communication
from .serializers import CommunicationsSerializer, CreateCommunicationsSerializer


class CommunicationsApiView(APIView):
    """
    API for managing communications.

    Endpoints:
    - GET: Retrieve all communications.
    - POST: Create a new communication.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve all communications",
        operation_description="Get a list of all communications.",
        responses={
            200: CommunicationsSerializer(many=True),
            500: "Internal Server Error: An error occurred while retrieving communications.",
        },
    )
    def get(self, request: Request):
        """
        Retrieve a list of all communications.

        Returns:
            - 200 OK: List of communications.
            - 500 Internal Server Error: An error occurred.
        """
        try:
            communications = Communication.objects.all()
            serializer = CommunicationsSerializer(communications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occurred while retrieving communications."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Create a communication",
        operation_description="Create a new communication by providing a receiver and content.",
        request_body=CreateCommunicationsSerializer,
        responses={
            201: CreateCommunicationsSerializer,
            400: "Bad Request: Invalid or missing data in the request body.",
            500: "Internal Server Error: An error occurred while creating the communication.",
        },
    )
    def post(self, request: Request):
        """
        Create a new communication.

        Request Body:
            - receiver (int): ID of the receiver.
            - content (str): The content of the message.

        Returns:
            - 201 Created: Successfully created the communication.
            - 400 Bad Request: If request data is invalid.
            - 500 Internal Server Error: If an error occurs.
        """
        try:
            serializer = CreateCommunicationsSerializer(
                data=request.data, context={'request': request}
            )
            if not serializer.is_valid():
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CommunicationDetailApiView(APIView):
    """
    API for managing a specific communication by its ID.

    Endpoints:
    - GET: Retrieve a specific communication.
    - PUT: Update a communication.
    - DELETE: Delete a communication.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve a communication",
        operation_description="Retrieve the details of a communication by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'communication_id',
                openapi.IN_PATH,
                description="ID of the communication to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: CommunicationsSerializer,
            404: "Not Found: Communication not found.",
            500: "Internal Server Error: An error occurred while retrieving the communication.",
        },
    )
    def get(self, request: Request, communication_id: int):
        """
        Retrieve the details of a specific communication.

        Path Parameters:
            - communication_id (int): The ID of the communication to retrieve.

        Returns:
            - 200 OK: The communication details.
            - 404 Not Found: If communication is not found.
            - 500 Internal Server Error: If an error occurs.
        """
        try:
            communication = (
                    Communication.objects.filter(
                        id=communication_id, sender=request.user
                    ) | Communication.objects.filter(
                id=communication_id, receiver=request.user
            )
            ).first()

            if not communication:
                return Response(
                    {"error": "Communication not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = CommunicationsSerializer(communication)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occurred while retrieving communication."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Update a communication",
        operation_description="Update the content of an existing communication.",
        manual_parameters=[
            openapi.Parameter(
                'communication_id',
                openapi.IN_PATH,
                description="ID of the communication to update",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=CreateCommunicationsSerializer,
        responses={
            200: CreateCommunicationsSerializer,
            400: "Bad Request: Invalid input data.",
            404: "Not Found: Communication not found.",
            500: "Internal Server Error: An error occurred while updating the communication.",
        },
    )
    def put(self, request: Request, communication_id: int):
        """
        Update a specific communication.

        Path Parameters:
            - communication_id (int): The ID of the communication to update.

        Request Body:
            - Fields to update (e.g., content).

        Returns:
            - 200 OK: Successfully updated the communication.
            - 400 Bad Request: If data is invalid.
            - 404 Not Found: If communication is not found.
            - 500 Internal Server Error: If an error occurs.
        """
        try:
            communication = Communication.objects.filter(
                id=communication_id, sender=request.user
            ).first()

            if not communication:
                return Response(
                    {"error": "Communication not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = CreateCommunicationsSerializer(
                communication, data=request.data, partial=True, context={'request': request}
            )
            if not serializer.is_valid():
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred while updating communication: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Delete a communication",
        operation_description="Delete a specific communication by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'communication_id',
                openapi.IN_PATH,
                description="ID of the communication to delete",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            204: "No Content: Communication successfully deleted.",
            403: "Forbidden: User does not have permission to delete.",
            404: "Not Found: Communication not found.",
            500: "Internal Server Error: An error occurred while deleting the communication.",
        },
    )
    def delete(self, request: Request, communication_id: int):
        """
        Delete a specific communication.

        Path Parameters:
            - communication_id (int): The ID of the communication to delete.

        Returns:
            - 204 No Content: Successfully deleted the communication.
            - 403 Forbidden: User does not have permission to delete.
            - 404 Not Found: If communication is not found.
            - 500 Internal Server Error: If an error occurs.
        """
        try:
            communication = Communication.objects.filter(id=communication_id).first()

            if not communication:
                return Response(
                    {"error": "Communication not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if communication.sender != request.user and communication.receiver != request.user:
                return Response(
                    {"error": "You do not have permission to delete this communication."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            communication.delete()
            return Response(
                {"message": "Communication deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while deleting communication: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
