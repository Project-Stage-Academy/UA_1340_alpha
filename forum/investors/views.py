from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from investors.models import InvestorProfile
from startups.models import StartupProfile
from startups.serializers import StartupProfileSerializer


class SavedStartupsApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(

        operation_description="Retrieve a list of startups saved by the authenticated investor.",
        responses={
            200: StartupProfileSerializer(many=True),
            404: openapi.Response(description="Investor profile not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def get(self, request):
        """
        Retrieve a list of startups saved by the authenticated investor.

        Parameters:
        request (Request): The HTTP request object containing user authentication details.

        Returns:
        Response: A Response object containing serialized data of saved startups with a status code of 200 if successful.
                  If the investor profile is not found, returns a 404 status with an error message.
                  If any other exception occurs, returns a 500 status with the error message.
        """
        try:
            investor_profile = InvestorProfile.objects.get(user=request.user)
            saved_startups = StartupProfile.objects.filter(investor_saves__investor=investor_profile)
            serializer = StartupProfileSerializer(saved_startups, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
