from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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

class InvestorProfileApiView(APIView):

    def get(self, request):
        profiles = InvestorProfile.objects.all()
        serializer = InvestorProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateInvestorProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestorProfileDetailApiView(APIView):

    def get_object(self, pk):
        try:
            return InvestorProfile.objects.get(pk=pk)
        except InvestorProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        profile = self.get_object(pk)
        serializer = InvestorProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        profile = self.get_object(pk)
        serializer = CreateInvestorProfileSerializer(profile, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = self.get_object(pk)
        profile.delete()
        return Response({"message": "Profile deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class InvestorPreferredIndustryApiView(APIView):

    def get(self, request):
        industries = InvestorPreferredIndustry.objects.all()
        serializer = InvestorPreferredIndustrySerializer(industries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateInvestorPreferredIndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestorPreferredIndustryDetailApiView(APIView):

    def get_object(self, pk):
        try:
            return InvestorPreferredIndustry.objects.get(pk=pk)
        except InvestorPreferredIndustry.DoesNotExist:
            return Response({"error": "Industry not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        industry = self.get_object(pk)
        serializer = InvestorPreferredIndustrySerializer(industry)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        industry = self.get_object(pk)
        industry.delete()
        return Response({"message": "Industry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class InvestorSavedStartupApiView(APIView):

    def get(self, request):
        saved_startups = InvestorSavedStartup.objects.all()
        serializer = InvestorSavedStartupSerializer(saved_startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateInvestorSavedStartupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestorSavedStartupDetailApiView(APIView):

    def get_object(self, pk):
        try:
            return InvestorSavedStartup.objects.get(pk=pk)
        except InvestorSavedStartup.DoesNotExist:
            return Response({"error": "Saved startup not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        saved_startup = self.get_object(pk)
        serializer = InvestorSavedStartupSerializer(saved_startup)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        saved_startup = self.get_object(pk)
        saved_startup.delete()
        return Response({"message": "Saved startup deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Investor Tracked Project Views
class InvestorTrackedProjectApiView(APIView):

    def get(self, request):
        tracked_projects = InvestorTrackedProject.objects.all()
        serializer = InvestorTrackedProjectSerializer(tracked_projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateInvestorTrackedProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestorTrackedProjectDetailApiView(APIView):

    def get_object(self, pk):
        try:
            return InvestorTrackedProject.objects.get(pk=pk)
        except InvestorTrackedProject.DoesNotExist:
            return Response({"error": "Tracked project not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        tracked_project = self.get_object(pk)
        serializer = InvestorTrackedProjectSerializer(tracked_project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        tracked_project = self.get_object(pk)
        tracked_project.delete()
        return Response({"message": "Tracked project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
