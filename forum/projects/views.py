from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer, CreateProjectSerializer, UpdateProjectSerializer


class ProjectListCreateAPIView(APIView):
    """
    View for retrieving a list of projects and creating a new project.
    """

    def get(self, request):
        """
        Retrieve a list of projects.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new project.
        """
        serializer = CreateProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):
    """
    View for retrieving, updating, or deleting a specific project.
    """

    def get_object(self, pk):
        """
        Retrieve a project by PK or return a 404 error.
        """
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve detailed information about a project.
        """
        project = self.get_object(pk)
        if project is None:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update information about a project.
        """
        project = self.get_object(pk)
        if project is None:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a project.
        """
        project = self.get_object(pk)
        if project is None:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        project.delete()
        return Response({"message": "Project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
