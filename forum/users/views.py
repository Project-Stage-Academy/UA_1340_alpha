from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.db import IntegrityError, DatabaseError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from forum.tasks import send_email_task


class SignupView(APIView):

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    # send email here
                    return Response(
                        {
                            "message": "User created successfully",
                            "user_id": user.id,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"message": "Failed to create user"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except IntegrityError as e:
            return Response(
                {"error": "User already exists", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except DatabaseError as e:
            return Response(
                {"error": "A database error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except ValidationError as e:
            return Response(
                {"error": "Invalid data provided", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ObjectDoesNotExist as e:
            return Response(
                {"error": "Requested object not found", "details": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        except TypeError as e:
            return Response(
                {"error": "Type mismatch error", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response({
                    "error": "Failed to create user. An unexpected error occurred",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
          
class SendEmailAPIView(APIView):
    def post(self, request):
        subject = request.data.get("subject")
        message = request.data.get("message")  # Plain text version
        html_message = request.data.get("html_message")  # HTML version
        recipient = request.data.get("recipient")  # List of emails

        if not subject or not message or not recipient:
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_list = []
        if isinstance(recipient, str):
            recipient_list.append(recipient)
        else:
            Response(
                {"error": "recipient must be a string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for email in recipient_list:
            try:
                validate_email(email)
            except ValidationError:
                return Response(
                    {"error": f"Invalid email: {email}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        send_email_task.delay(subject, message, recipient_list, html_message)

        return Response({"success": "HTML Email is being sent"}, status=status.HTTP_202_ACCEPTED)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutAPIView(APIView):
    """
    API endpoint that allows users to log out by blacklisting their refresh token.
    Requires the user to be authenticated.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Handle POST request to blacklist the provided refresh token.

        Args:
            request: The HTTP request object containing the refresh token in the request data.

        Returns:
            A Response object with status 205 if successful, or 400 if an error occurs.
        """
        
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        