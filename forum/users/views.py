import logging

import jwt
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .utils import (
    send_reset_password_email,
    send_verification_email,
    validate_password_policy,
)

logger = logging.getLogger(__name__)


class ResetPasswordRequestView(APIView):
    """
    API View to handle requests for password reset email generation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info("Requested email: %s", email)

        try:
            user = User.objects.get(email=email)
            logger.info(
                "Queueing password reset email for user %s", user.email)
            success = send_reset_password_email(user, request)

            if not success:
                logger.error(
                    f"Failed to process password reset for {user.email}")
                return Response({'error': 'Failed to process password reset. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # self.send_reset_password_email(user, request)
        except User.DoesNotExist:
            logger.warning(
                "Password reset requested for non-existent email: %s", email)
            return Response({'error': 'Email was not found in the system'}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "If the email is registered, a password reset link will be sent."}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    """
    API View to confirm password reset using UID and token.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

            password = request.data.get("password")
            validation_error = validate_password_policy(password)
            if validation_error:
                return Response({"error": validation_error}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error in ResetPasswordConfirmView")
            return Response({"error": "Failed to reset password."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordCompleteView(APIView):
    """
    API View to confirm that the password reset process has been completed.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Password reset process is complete."}, status=status.HTTP_200_OK)


class SignupView(APIView):

    def post(self, request):
        logger.info("SignupView POST request received with data: %s", request.data)
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    logger.info("User created successfully with id: %s", user.id)
                    send_verification_email(user, request)
                    return Response(
                        {
                            "message": "User created successfully",
                            "user_id": user.id,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    logger.error("Failed to create user")
                    return Response(
                        {"message": "Failed to create user"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            logger.warning("Invalid data provided: %s", serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except IntegrityError as e:
            logger.error("User already exists: %s", str(e))
            return Response(
                {"error": "User already exists", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except DatabaseError as e:
            logger.error("A database error occurred: %s", str(e))
            return Response(
                {"error": "A database error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except ValidationError as e:
            logger.error("Invalid data provided: %s", str(e))
            return Response(
                {"error": "Invalid data provided", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ObjectDoesNotExist as e:
            logger.error("Requested object not found: %s", str(e))
            return Response(
                {"error": "Requested object not found", "details": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        except TypeError as e:
            logger.error("Type error: %s", str(e))
            return Response(
                {"error": "Type mismatch error", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error("Failed to create user. An unexpected error occurred: %s", str(e))
            return Response(
                {
                    "error": "Failed to create user. An unexpected error occurred",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            logger.info("Token is required")
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT["ALGORITHM"])
            user = User.objects.get(id=payload["user_id"])
            user.is_email_confirmed = True
            user.is_active = True
            user.save()

            return Response(
                {"message": "Email verified successfully"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            logger.info("User not found")
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired")
            return Response(
                {"error": "Token has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            logger.info("Invalid token")
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return Response(
                {"error": "Database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response(
                {"error": "Unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"message": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info("Requested email: %s", email)

        try:
            user = User.objects.get(email=email)

            if user.is_email_confirmed:
                logger.info("Email is already verified.")
                return Response(
                    {"message": "Email is already verified."},
                    status=status.HTTP_200_OK
                )

            logger.info("Resending verification email %s", email)
            success = send_verification_email(user, request)

            if success:
                return Response(
                    {"message": "Verification email was sent."},
                    status=status.HTTP_200_OK
                )
            else:
                logger.error(f"Failed to send verification email to {email}")
                return Response(
                    {"error": "Failed to send verification email."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except User.DoesNotExist:
            logger.warning("Email verification requested for non-existent email: %s", email)
            return Response(
                {"error": "Email verification requested for non-existent email"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}")
            return Response(
                {
                    "error": "Failed to send verification email.",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

