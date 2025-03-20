from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import StartupProfile
from .serializers import StartupProfileSerializer, CreateStartupProfileSerializer


class StartupProfileListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing startup profiles.

    Endpoints:
    - GET: Retrieve a list of all startups.
    - POST: Create a new startup profile.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve all startups",
        operation_description="Get a list of all startup profiles available in the system.",
        tags=["Startups"],
        responses={200: StartupProfileSerializer(many=True)}
    )
    def get(self, request):
        """
        Retrieve a list of all startup profiles.

        Responses:
            - 200 OK: Successfully returns a list of startup profiles.
        """
        startups = StartupProfile.objects.all()
        serializer = StartupProfileSerializer(startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a startup profile",
        operation_description="Create a new startup profile by providing the necessary details.",
        request_body=CreateStartupProfileSerializer,
        tags=["Startups"],
        responses={
            201: StartupProfileSerializer,
            400: "Bad Request: Invalid input data."
        }
    )
    def post(self, request):
        """
        Create a new startup profile.

        Request Body:
            - company_name (str): The name of the startup (required).
            - description (str): The description of the startup (required).
            - website (str, optional): The website URL of the startup.
            - contact_email (str): The contact email for the startup (required).
            - industries (list[int]): A list of industry IDs associated with the startup (required).
            - startup_logo (file, optional): The logo of the startup.

        Responses:
            - 201 Created: Successfully creates the startup profile.
            - 400 Bad Request: If the input data is invalid.
        """
        serializer = CreateStartupProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartupProfileDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing a specific startup profile.

    Endpoints:
    - GET: Retrieve details of a specific startup profile.
    - PUT: Update an existing startup profile.
    - DELETE: Delete a specific startup profile.
    """

    def get_object(self, pk):
        """
        Retrieve a startup profile by its ID.

        Args:
            - pk (int): The primary key of the startup profile.

        Returns:
            - StartupProfile: The startup profile instance.
            - None: If the startup profile does not exist.
        """
        return get_object_or_404(StartupProfile, pk=pk)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific startup",
        operation_description="Retrieve the details of a specific startup profile by its ID.",
        tags=["Startups"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the startup profile",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: StartupProfileSerializer,
            404: "Startup not found."
        }
    )
    def get(self, request, pk):
        """
        Retrieve details of a specific startup profile.

        Path Parameters:
            - pk (int): The ID of the startup profile to retrieve.

        Responses:
            - 200 OK: Successfully retrieves the startup profile details.
            - 404 Not Found: If the startup profile does not exist.
        """
        startup = self.get_object(pk)
        if startup is None:
            return Response({"error": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StartupProfileSerializer(startup)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a startup profile",
        operation_description="Update the details of a startup profile by its ID.",
        tags=["Startups"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the startup profile",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=CreateStartupProfileSerializer,
        responses={
            200: StartupProfileSerializer,
            400: "Bad Request: Invalid input data.",
            404: "Startup not found."
        }
    )
    def put(self, request, pk):
        """
        Update a specific startup profile.

        Path Parameters:
            - pk (int): The ID of the startup profile to update.

        Request Body:
            - Fields to update (e.g., company_name, description, website, etc.).

        Responses:
            - 200 OK: Successfully updates the startup profile.
            - 400 Bad Request: If the input data is invalid.
            - 404 Not Found: If the startup profile does not exist.
        """
        startup = self.get_object(pk)
        if startup is None:
            return Response({"error": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CreateStartupProfileSerializer(startup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
