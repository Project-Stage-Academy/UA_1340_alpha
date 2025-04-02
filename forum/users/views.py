import logging

import jwt
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import (
    CustomRoleSerializer,
    CustomTokenObtainPairSerializer,
    SetRoleSerializer,
    UserSerializer,
)
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

    @swagger_auto_schema(
        operation_summary="Request Password Reset",
        operation_description="Send a password reset email if the user exists.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's email"
                ),
            },
            required=["email"],
        ),
        responses={
            200: openapi.Response(description="If the email exists, a reset link is sent."),
            400: openapi.Response(description="Bad request, missing email."),
            404: openapi.Response(description="Email not found."),
            500: openapi.Response(description="Internal server error."),
        }
    )
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

    @swagger_auto_schema(
        operation_summary="Confirm Password Reset",
        operation_description="Verify reset token and set a new password.",
        manual_parameters=[
            openapi.Parameter(
                "uidb64", openapi.IN_PATH, description="Encoded user ID", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "token", openapi.IN_PATH, description="Password reset token", type=openapi.TYPE_STRING
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
            },
            required=["password"],
        ),
        responses={
            200: openapi.Response(description="Password reset successfully."),
            400: openapi.Response(description="Invalid token or bad request."),
            500: openapi.Response(description="Internal server error."),
        }
    )
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

    @swagger_auto_schema(
        operation_summary="Password Reset Complete",
        operation_description="Confirm that the password reset process has been completed.",
        responses={
            200: openapi.Response(description="Password reset process is complete."),
            500: openapi.Response(description="Internal server error."),
        }
    )
    def get(self, request):
        return Response({"message": "Password reset process is complete."}, status=status.HTTP_200_OK)


class SignupView(APIView):
    """
    API View to handle user signup.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Signup",
        operation_description="Register a new user and send a verification email.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(description="User created successfully."),
            400: openapi.Response(description="Validation error."),
            500: openapi.Response(description="Internal server error."),
        }
    )
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
    """
    API View to verify user email.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify Email",
        operation_description="Verify a user's email using a token.",
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="JWT verification token",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(description="Email verified successfully."),
            400: openapi.Response(description="Invalid or expired token."),
            404: openapi.Response(description="User not found."),
            500: openapi.Response(description="Database error."),
        }
    )
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
    """
    API View to resend email verification link to user.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Resend Verification Email",
        operation_description="Resend email verification link to user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's email"
                ),
            },
            required=["email"],
        ),
        responses={
            200: openapi.Response(description="Verification email sent."),
            400: openapi.Response(description="Email is required."),
            404: openapi.Response(description="User not found."),
            500: openapi.Response(description="Failed to send email."),
        }
    )
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
    """
    Allow users to obtain a pair of access and refresh tokens using their email and password.
    Tokens will be set in HTTP-only cookies instead of being returned in the response body.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Obtain JWT Token",
        operation_description="Authenticate user and return JWT access & refresh tokens, which will be set in HTTP-only cookies.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description="User's email address."),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description="User's password."),
                "role": openapi.Schema(type=openapi.TYPE_STRING, enum=["investor", "startup"], description="User's selected role for authentication ('startup' or 'investor')."),
            },
            required=["email", "password", "role"],
        ),
        responses={
            200: openapi.Response(
                description="JWT access and refresh tokens set in cookies.",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={"message": openapi.Schema(type=openapi.TYPE_STRING, description="Success message indicating login was successful.")}),
            ),
            400: openapi.Response(description="Invalid credentials or validation error."),
            401: openapi.Response(description="Unauthorized, email not verified."),
            403: openapi.Response(description="User is banned or inactive."),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        access_token = data["access"]
        refresh_token = data["refresh"]

        response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)

        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
            value=refresh_token,
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
        )
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom Token Refresh View to retrieve the refresh token from cookies or Authorization header.
    """
    def post(self, request, *args, **kwargs):
        # Try to get refresh token from cookie first
        refresh_token = request.COOKIES.get('refresh_token')

        # If not in cookie, try Authorization header
        if not refresh_token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                refresh_token = auth_header.split('Bearer ')[1].strip()
            else:
                return Response(
                    {"error": "Refresh token not found in cookies or Authorization header"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            data = {
                'access': str(refresh.access_token),
            }
            if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
                data['refresh'] = str(refresh)
                response = Response(data)
                response.set_cookie(
                    key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                    value=str(refresh),
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                    samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
                )
            else:
                response = Response(data)

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Log out the user by invalidating the refresh token.",
        operation_description="Log out the user by blacklisting the refresh token and deleting the cookies for access and refresh tokens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JWT refresh token"
                ),
            },
            required=["refresh"],
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged out.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Logout confirmation message"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid or missing refresh token.",
            ),
            500: openapi.Response(
                description="An unexpected error occurred.",
            ),
        }
    )
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"message": "User successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token') 

            request.session.flush()

            return response
        except TokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SelectRoleView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication] 
    serializer_class = CustomRoleSerializer

    @swagger_auto_schema(
        operation_summary="Select User Role",
        operation_description="Allows an authenticated user to select a role ('investor' or 'startup') and receive JWT tokens in cookies.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "role": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["investor", "startup"],
                    description="User's selected role."
                ),
            },
            required=["role"],
        ),
        responses={
            200: openapi.Response(description="Role selected and tokens set in cookies."),
            400: openapi.Response(description="Invalid role or user not eligible for the role."),
            401: openapi.Response(description="Unauthorized due to email not verified."),
            403: openapi.Response(description="User is banned or inactive."),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            access_token = data["access"]
            refresh_token = data["refresh"]

            response = Response({"message": "Role selected successfully"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                value=refresh_token,
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
            )

            return response

        except ValidationError as e:
            return Response(
                {"error": str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SetRoleView(GenericAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = SetRoleSerializer

    @swagger_auto_schema(
        operation_summary="Set User Roles After Signup",
        operation_description="Allows a newly registered user to set one or both roles ('investor', 'startup') after OAuth signup.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "roles": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING, enum=["investor", "startup"]),
                    description="User's initial roles (one or both)."
                ),
            },
            required=["roles"],
        ),
        responses={
            200: openapi.Response(description="Roles set and tokens issued."),
            400: openapi.Response(description="Invalid roles."),
            403: openapi.Response(description="User is banned or inactive."),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})

        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            access_token = data["access"]
            refresh_token = data["refresh"]

            response = Response({"message": "Roles set successfully"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                value=refresh_token,
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
            )

            return response

        except ValidationError as e:
            return Response({"error": str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
