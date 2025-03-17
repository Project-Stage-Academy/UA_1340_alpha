import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InvestorProfile, InvestorSavedStartup
from .serializers import CreateInvestorSavedStartupSerializer
from startups.models import StartupProfile
from startups.serializers import StartupProfileSerializer


logger = logging.getLogger(__name__)


class SavedStartupsApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["investors"],
        operation_summary="Retrieve all investor profiles",
        operation_description="Retrieve a list of startups saved by the authenticated investor with optional filtering.",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search term to filter startups by name or description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search_field',
                openapi.IN_QUERY,
                description="Field to search by (e.g., 'company_name', 'description')",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'sort',
                openapi.IN_QUERY,
                description="Sort startups by a specific field (e.g., 'name', '-name' for descending)",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: StartupProfileSerializer(many=True),
            404: openapi.Response(description="Investor profile not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def get(self, request):
        """
        Retrieve a list of startups saved by the authenticated investor with optional filtering.

        Parameters:
        request (Request): The HTTP request object containing user authentication details.

        Returns:
        Response: A Response object containing serialized data of saved startups with a status code of 200 if successful.
                  If the investor profile is not found, returns a 404 status with an error message.
                  If any other exception occurs, returns a 500 status with the error message.
        """
        try:
            logger.info(f"Retrieving saved startups for user: {request.user}")
            investor_profile = InvestorProfile.objects.get(user=request.user)
            saved_startups = StartupProfile.objects.filter(investor_saves__investor=investor_profile)

            search_field = request.query_params.get('search_field', 'company_name')  # Default to 'name'
            search_term = request.query_params.get('search', None)

            if search_term:
                filter_kwargs = {f"{search_field}__icontains": search_term}
                saved_startups = saved_startups.filter(**filter_kwargs)

            sort_field = request.query_params.get('sort', None)
            if sort_field:
                saved_startups = saved_startups.order_by(sort_field)

            serializer = StartupProfileSerializer(saved_startups, many=True)
            logger.info(f"Successfully retrieved {len(saved_startups)} saved startups for user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except InvestorProfile.DoesNotExist:
            logger.warning(f"Investor profile not found for user: {request.user}")
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving saved startups for user {request.user}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class CreateDeleteSavedStartupApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["investors"],
        operation_summary="Save startup to the saved startups list",
        operation_description="Save a startup to the authenticated investor's saved startups list.",
        manual_parameters=[
            openapi.Parameter(
                'startup_id',
                openapi.IN_PATH,
                description="ID of the startup to be saved.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            201: CreateInvestorSavedStartupSerializer,
            400: openapi.Response(description="Startup is already saved by the investor"),
            404: openapi.Response(description="Investor or Startup profile not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def post(self, request, startup_id):
        """
        Save a startup to the authenticated investor's saved startups list.

        Parameters:
        request (Request): The HTTP request object containing user authentication details.
        startup_id (int): The ID of the startup to be saved.

        Returns:
        Response: A Response object containing serialized data of the saved startup with a status code of 201 if successful.
                  If the investor or startup profile is not found, returns a 404 status with an error message.
                  If the data is invalid, returns a 400 status with validation errors.
                  If any other exception occurs, returns a 500 status with the error message.
        """
        try:
            logger.info(f"Attempting to save startup {startup_id} for user {request.user}")
            investor_profile = InvestorProfile.objects.get(user=request.user)
            startup_profile = StartupProfile.objects.get(id=startup_id)

            saved_startup, created = InvestorSavedStartup.objects.get_or_create(
                investor=investor_profile,
                startup=startup_profile
            )

            if not created:
                logger.warning(f"Startup {startup_id} is already saved by investor {request.user}")
                return Response(
                    {"error": "Startup is already saved by the investor"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Startup {startup_id} successfully saved by investor {request.user}")
            serializer = CreateInvestorSavedStartupSerializer(saved_startup)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except InvestorProfile.DoesNotExist:
            logger.error(f"Investor profile not found for user {request.user}")
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except StartupProfile.DoesNotExist:
            logger.error(f"Startup profile {startup_id} not found")
            return Response(
                {"error": "Startup profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error saving startup {startup_id} for user {request.user}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        tags=["investors"],
        operation_summary="Delete startup from saved startups list",
        operation_description="Delete a startup from the authenticated investor's saved startups list.",
        manual_parameters=[
            openapi.Parameter(
                'startup_id',
                openapi.IN_PATH,
                description="ID of the startup to be deleted",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            204: openapi.Response(description="Startup successfully deleted from saved list"),
            404: openapi.Response(description="Investor or Startup profile not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def delete(self, request, startup_id):
        """
        Delete a startup from the authenticated investor's saved startups list.
    
        Parameters:
        request (Request): The HTTP request object containing user authentication details.
        startup_id (int): The ID of the startup to be deleted.
    
        Returns:
        Response: A Response object with a status code of 204 if successful.
                  If the investor or startup profile is not found, returns a 404 status with an error message.
                  If any other exception occurs, returns a 500 status with the error message.
        """
        try:
            logger.info(f"Attempting to delete startup {startup_id} from saved list for user {request.user}")
            investor_profile = InvestorProfile.objects.get(user=request.user)
            startup_profile = StartupProfile.objects.get(id=startup_id)
    
            saved_startup = InvestorSavedStartup.objects.get(
                investor=investor_profile,
                startup=startup_profile
            )
            saved_startup.delete()
            logger.info(f"Startup {startup_id} successfully deleted from saved list for user {request.user}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvestorProfile.DoesNotExist:
            logger.error(f"Investor profile not found for user {request.user}")
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except StartupProfile.DoesNotExist:
            logger.error(f"Startup profile {startup_id} not found")
            return Response(
                {"error": "Startup profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except InvestorSavedStartup.DoesNotExist:
            logger.error(f"Saved startup {startup_id} not found for user {request.user}")
            return Response(
                {"error": "Saved startup not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting startup {startup_id} for user {request.user}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
