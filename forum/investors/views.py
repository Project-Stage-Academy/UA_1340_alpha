from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    InvestorProfile,
    InvestorPreferredIndustry,
    InvestorSavedStartup,
    InvestorTrackedProject
)
from .serializers import (
    InvestorProfileSerializer,
    CreateInvestorProfileSerializer,
    InvestorPreferredIndustrySerializer,
    CreateInvestorPreferredIndustrySerializer,
    InvestorSavedStartupSerializer,
    CreateInvestorSavedStartupSerializer,
    InvestorTrackedProjectSerializer,
    CreateInvestorTrackedProjectSerializer
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class InvestorProfileApiView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing investor profiles.

    Endpoints:
    - GET: Retrieve all investor profiles.
    - POST: Create a new investor profile.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve all investor profiles",
        operation_description="Get a list of all investor profiles in the system.",
        tags=["Investors"],
        responses={200: InvestorProfileSerializer(many=True)}
    )
    def get(self, request):
        """
        Retrieve a list of all investor profiles.

        Responses:
            - 200 OK: Successfully returns a list of investor profiles.
        """
        profiles = InvestorProfile.objects.all()
        serializer = InvestorProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new investor profile",
        operation_description="Create a new investor profile with the required fields.",
        tags=["Investors"],
        request_body=CreateInvestorProfileSerializer,
        responses={
            201: InvestorProfileSerializer,
            400: "Bad Request: Invalid input data.",
        }
    )

    def post(self, request):
        """
        Create a new investor profile.

        Request Body:
            - company_name (str): Name of the investor's company (required).
            - investment_focus (str): Focus areas of the investment (required).
            - contact_email (str): Email address of the investor (required).
            - investment_range (str): Range of investment values (optional).
            - investor_logo (file): Logo of the investor's company (optional).

        Responses:
            - 201 Created: Successfully creates a new investor profile.
            - 400 Bad Request: If the input data is invalid.
        """
        serializer = CreateInvestorProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestorProfileDetailApiView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing a specific investor profile by ID.

    Endpoints:
    - GET: Retrieve a specific investor profile.
    - PUT: Update an investor profile.
    - DELETE: Delete an investor profile.
    """

    def get_object(self, pk):
        """
        Retrieve an investor profile by its ID.

        Args:
            - pk (int): The primary key of the investor profile.

        Returns:
            - InvestorProfile: The investor profile instance if found.
            - Response: A 404 error response if the profile does not exist.
        """
        return get_object_or_404(InvestorProfile, pk=pk)

    @swagger_auto_schema(
        operation_summary="Retrieve an investor profile",
        operation_description="Retrieve the details of a specific investor profile by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="ID of the investor profile", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: InvestorProfileSerializer,
            404: "Profile not found.",
        }
    )
    def get(self, request, pk):
        """
        Retrieve a specific investor profile by ID.

        Path Parameters:
            - pk (int): The ID of the investor profile to retrieve.

        Responses:
            - 200 OK: Successfully retrieves the investor profile details.
            - 404 Not Found: If the investor profile does not exist.
        """
        profile = self.get_object(pk)
        if isinstance(profile, Response):  # Handle case where `get_object` returned a 404 response
            return profile
        serializer = InvestorProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update an investor profile",
        operation_description="Update the details of an investor profile by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="ID of the investor profile", type=openapi.TYPE_INTEGER)
        ],
        request_body=CreateInvestorProfileSerializer,
        responses={
            200: InvestorProfileSerializer,
            400: "Bad Request: Invalid input data.",
            404: "Profile not found.",
        }
    )
    def put(self, request, pk):
        """
        Update a specific investor profile by ID.

        Path Parameters:
            - pk (int): The ID of the investor profile to update.

        Request Body:
            - Fields to update (e.g., company_name, investment_focus, contact_email, etc.).

        Responses:
            - 200 OK: Successfully updates the investor profile.
            - 400 Bad Request: If the input data is invalid.
            - 404 Not Found: If the investor profile does not exist.
        """
        profile = self.get_object(pk)
        if isinstance(profile, Response):  # Handle case where `get_object` returned a 404 response
            return profile
        serializer = CreateInvestorProfileSerializer(profile, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete an investor profile",
        operation_description="Delete a specific investor profile by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="ID of the investor profile", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: "Profile deleted successfully.",
            404: "Profile not found.",
        }
    )
    def delete(self, request, pk):
        """
        Delete a specific investor profile by ID.

        Path Parameters:
            - pk (int): The ID of the investor profile to delete.

        Responses:
            - 204 No Content: Successfully deletes the investor profile.
            - 404 Not Found: If the investor profile does not exist.
        """
        profile = self.get_object(pk)
        if isinstance(profile, Response):  # Handle case where `get_object` returned a 404 response
            return profile
        profile.delete()
        return Response({"message": "Profile deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class InvestorPreferredIndustryApiView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing investor preferred industries.

    Endpoints:
    - GET: Retrieve all preferred industries.
    - POST: Create a new preferred industry.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve all preferred industries",
        operation_description="Get a list of all investor preferred industries.",
        tags=["Investors"],
        responses={200: InvestorPreferredIndustrySerializer(many=True)}
    )
    def get(self, request):
        """
        Retrieve a list of all preferred industries.

        Responses:
            - 200 OK: Successfully returns a list of preferred industries.
        """
        industries = InvestorPreferredIndustry.objects.all()
        serializer = InvestorPreferredIndustrySerializer(industries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a preferred industry",
        operation_description="Create a new preferred industry for an investor by providing the required data.",
        tags=["Investors"],
        request_body=CreateInvestorPreferredIndustrySerializer,
        responses={
            201: InvestorPreferredIndustrySerializer,
            400: "Bad Request: Invalid input data."
        }
    )
    def post(self, request):
        """
        Create a new preferred industry.

        Request Body:
            - investor (int): ID of the investor (required).
            - industry (int): ID of the industry (required).

        Responses:
            - 201 Created: Successfully creates a new preferred industry.
            - 400 Bad Request: If the input data is invalid.
        """
        serializer = CreateInvestorPreferredIndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestorPreferredIndustryDetailApiView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing a specific investor preferred industry by ID.

    Endpoints:
    - GET: Retrieve a specific preferred industry.
    - DELETE: Delete a preferred industry.
    """

    def get_object(self, pk):
        """
        Retrieve a preferred industry by its ID.

        Args:
            - pk (int): The primary key of the preferred industry.

        Returns:
            - InvestorPreferredIndustry: The preferred industry instance if found.
            - Response: A 404 error response if the industry does not exist.
        """
        return get_object_or_404(InvestorPreferredIndustry, pk=pk)

    @swagger_auto_schema(
        operation_summary="Retrieve a preferred industry",
        operation_description="Retrieve the details of a specific preferred industry by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the preferred industry",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: InvestorPreferredIndustrySerializer,
            404: "Industry not found."
        }
    )
    def get(self, request, pk):
        """
        Retrieve a specific preferred industry by ID.

        Path Parameters:
            - pk (int): The ID of the preferred industry to retrieve.

        Responses:
            - 200 OK: Successfully retrieves the preferred industry details.
            - 404 Not Found: If the preferred industry does not exist.
        """
        industry = self.get_object(pk)
        if isinstance(industry, Response):  # Handle case where `get_object` returned a 404 response
            return industry
        serializer = InvestorPreferredIndustrySerializer(industry)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete a preferred industry",
        operation_description="Delete a specific preferred industry by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the preferred industry",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            204: "Industry deleted successfully.",
            404: "Industry not found."
        }
    )
    def delete(self, request, pk):
        """
        Delete a specific preferred industry by ID.

        Path Parameters:
            - pk (int): The ID of the preferred industry to delete.

        Responses:
            - 204 No Content: Successfully deletes the preferred industry.
            - 404 Not Found: If the preferred industry does not exist.
        """
        industry = self.get_object(pk)
        if isinstance(industry, Response):  # Handle case where `get_object` returned a 404 response
            return industry
        industry.delete()
        return Response({"message": "Industry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class InvestorTrackedProjectApiView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing investor-tracked projects.

    Endpoints:
    - GET: Retrieve all tracked projects.
    - POST: Add a new tracked project.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve all tracked projects",
        operation_description="Get a list of all projects tracked by investors.",
        tags=["Investors"],
        responses={200: InvestorTrackedProjectSerializer(many=True)}
    )
    def get(self, request):
        """
        Retrieve a list of all tracked projects.

        Responses:
            - 200 OK: Successfully returns a list of tracked projects.
        """
        tracked_projects = InvestorTrackedProject.objects.all()
        serializer = InvestorTrackedProjectSerializer(tracked_projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Add a tracked project",
        operation_description="Add a new project to the list of tracked projects for an investor.",
        tags=["Investors"],
        request_body=CreateInvestorTrackedProjectSerializer,
        responses={
            201: InvestorTrackedProjectSerializer,
            400: "Bad Request: Invalid input data."
        }
    )
    def post(self, request):
        """
        Add a new project to the tracked projects list.

        Request Body:
            - investor (int): ID of the investor (required).
            - project (int): ID of the project to track (required).

        Responses:
            - 201 Created: Successfully tracks the project.
            - 400 Bad Request: If the input data is invalid.
        """
        serializer = CreateInvestorTrackedProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestorTrackedProjectDetailApiView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing a specific tracked project by ID.

    Endpoints:
    - GET: Retrieve a specific tracked project.
    - DELETE: Remove a tracked project.
    """

    def get_object(self, pk):
        """
        Retrieve a tracked project by its ID.

        Args:
            - pk (int): The primary key of the tracked project.

        Returns:
            - InvestorTrackedProject: The tracked project instance if found.
            - None: If the tracked project does not exist.
        """
        return get_object_or_404(InvestorTrackedProject, pk=pk)

    @swagger_auto_schema(
        operation_summary="Retrieve a tracked project",
        operation_description="Retrieve the details of a specific tracked project by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the tracked project",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: InvestorTrackedProjectSerializer,
            404: "Tracked project not found."
        }
    )
    def get(self, request, pk):
        """
        Retrieve a specific tracked project by ID.

        Path Parameters:
            - pk (int): The ID of the tracked project to retrieve.

        Responses:
            - 200 OK: Successfully retrieves the tracked project details.
            - 404 Not Found: If the tracked project does not exist.
        """
        tracked_project = self.get_object(pk)
        if isinstance(tracked_project, Response):  # Handle case where tracked_project is a 404 Response
            return tracked_project
        serializer = InvestorTrackedProjectSerializer(tracked_project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete a tracked project",
        operation_description="Remove a tracked project from the investor's list by its ID.",
        tags=["Investors"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the tracked project",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            204: "Tracked project deleted successfully.",
            404: "Tracked project not found."
        }
    )
    def delete(self, request, pk):
        """
        Delete a specific tracked project by ID.

        Path Parameters:
            - pk (int): The ID of the tracked project to delete.

        Responses:
            - 204 No Content: Successfully deletes the tracked project.
            - 404 Not Found: If the tracked project does not exist.
        """
        tracked_project = self.get_object(pk)
        if isinstance(tracked_project, Response):  # Handle case where tracked_project is a 404 Response
            return tracked_project
        tracked_project.delete()
        return Response({"message": "Tracked project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

