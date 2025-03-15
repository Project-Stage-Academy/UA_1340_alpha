from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StartupProfile
from .serializers import (
    StartupProfileSerializer,
    CreateStartupProfileSerializer
)


class StartupProfileListCreateAPIView(APIView):
    """
    View for retrieving a list of startups and creating a new startup.
    """

    def get(self, request):
        """
        Retrieve a list of startups.
        """
        startups = StartupProfile.objects.all()
        serializer = StartupProfileSerializer(startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new startup.
        """
        serializer = CreateStartupProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartupProfileDetailAPIView(APIView):
    """
    View for retrieving, updating, and deleting a specific startup.
    """

    def get_object(self, pk):
        """
        Retrieve a startup by PK or return a 404 error if not found.
        """
        try:
            return StartupProfile.objects.get(pk=pk)
        except StartupProfile.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve detailed information about a startup.
        """
        startup = self.get_object(pk)
        if startup is None:
            return Response({"error": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StartupProfileSerializer(startup)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update information about a startup.
        """
        startup = self.get_object(pk)
        if startup is None:
            return Response({"error": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CreateStartupProfileSerializer(startup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a startup.
        """
        startup = self.get_object(pk)
        if startup is None:
            return Response({"error": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        startup.delete()
        return Response({"message": "Startup deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
