from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Project
from .serializers import ProjectSerializer, CreateProjectSerializer, UpdateProjectSerializer

class ProjectListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing projects.

    Endpoints:
    - GET: Retrieve all projects.
    - POST: Create a new project.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve all projects",
        operation_description="Get a list of all projects available in the system.",
        tags=["Projects"],
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request):
        """
        Retrieve a list of all projects.

        Responses:
            - 200 OK: Successfully returns a list of all projects.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new project",
        operation_description="Create a new project by providing the necessary details.",
        tags=["Projects"],
        request_body=CreateProjectSerializer,
        responses={
            201: ProjectSerializer,
            400: "Bad Request: Invalid input data."
        }
    )
    def post(self, request):
        """
        Create a new project.

        Request Body:
            - startup (int): ID of the startup associated with the project (required).
            - title (str): Title of the project (required).
            - description (str): Description of the project (required).
            - funding_goal (float): Target funding goal for the project (required).
            - funding_needed (float): Current funding needed (required).
            - status (str): Project status (e.g., Seeking Funding, In Progress, Completed) (optional).
            - duration (int): Duration of the project in months (optional).
            - business_plan (file): Upload a business plan document (optional).
            - media_files (file): Upload associated media files (optional).

        Responses:
            - 201 Created: Successfully creates the project.
            - 400 Bad Request: If the input data is invalid.
        """
        serializer = CreateProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    API for managing a specific project.

    Endpoints:
    - GET: Retrieve details of a specific project.
    - PUT: Update an existing project.
    - DELETE: Delete a project.
    """

    def get_object(self, pk):
        """
        Retrieve a project by its ID.

        Args:
            - pk (int): The primary key of the project.

        Returns:
            - Project: The project instance if found.
            - None: If the project does not exist.
        """
        return get_object_or_404(Project, pk=pk)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific project",
        operation_description="Retrieve the details of a specific project by its ID.",
        tags=["Projects"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the project",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: ProjectSerializer,
            404: "Project not found."
        }
    )
    def get(self, request, pk):
        """
        Retrieve details of a specific project.

        Path Parameters:
            - pk (int): The ID of the project to retrieve.

        Responses:
            - 200 OK: Successfully retrieves the project details.
            - 404 Not Found: If the project does not exist.
        """
        project = self.get_object(pk)
        if project is None:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a project",
        operation_description="Update the details of a project by its ID.",
        tags=["Projects"],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the project",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=UpdateProjectSerializer,
        responses={
            200: ProjectSerializer,
            400: "Bad Request: Invalid input data.",
            404: "Project not found."
        }
    )
    def put(self, request, pk):
        """
        Update a specific project.

        Path Parameters:
            - pk (int): The ID of the project to update.

        Request Body:
            - Fields to update (e.g., title, description, funding_goal, funding_needed, status, etc.).

        Responses:
            - 200 OK: Successfully updates the project.
            - 400 Bad Request: If the input data is invalid.
            - 404 Not Found: If the project does not exist.
        """
        project = self.get_object(pk)
        if project is None:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

