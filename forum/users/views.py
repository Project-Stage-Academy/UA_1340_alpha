import logging
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.db import IntegrityError, DatabaseError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from forum.tasks import send_email_task_no_ssl, send_email_task
from rest_framework.permissions import AllowAny
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.template.loader import render_to_string
from datetime import timedelta
import logging
from .utils import validate_password_policy, send_reset_password_email


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

logger = logging.getLogger(__name__)

class SignupView(APIView):

    def post(self, request):
        logger.info("SignupView POST request received with data: %s", request.data)
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    logger.info("User created successfully with id: %s", user.id)
                    # send email here
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
            return Response({
                "error": "Failed to create user. An unexpected error occurred",
                "details": str(e)
            },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendEmailAPIView(APIView):
    def post(self, request):
        logger.info("SendEmailAPIView POST request received with data: %s", request.data)
        subject = request.data.get("subject")
        message = request.data.get("message")  # Plain text version
        html_message = request.data.get("html_message")  # HTML version
        recipient = request.data.get("recipient")  # List of emails

        if not subject or not message or not recipient:
            logger.error("Missing fields in request data")
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_list = []
        if isinstance(recipient, str):
            recipient_list.append(recipient)
        else:
            logger.error("Recipient must be a string")
            return Response(
                {"error": "recipient must be a string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for email in recipient_list:
            try:
                validate_email(email)
            except ValidationError:
                logger.error("Invalid email: %s", email)
                return Response(
                    {"error": f"Invalid email: {email}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        send_email_task.delay(subject, message, recipient_list, html_message)
        logger.info("Email task sent to queue with subject: %s", subject)

        return Response({"success": "HTML Email is being sent"}, status=status.HTTP_202_ACCEPTED)
