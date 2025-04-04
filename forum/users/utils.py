import logging
from datetime import datetime
from urllib.parse import urlencode

from celery.exceptions import CeleryError
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from forum.tasks import send_email_task_no_ssl, send_email_task

logger = logging.getLogger(__name__)

def validate_password_policy(password):
    """
    Validates the password against predefined complexity requirements.
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?`~" for char in password):
        return "Password must contain at least one special character."
    return ""


def send_reset_password_email(user, request):
    """
    Asynchronous task to generate a password reset link and queue an email for sending.
    Args:
        user_id (int): The ID of the user requesting a password reset.
    Raises:
        User.DoesNotExist: If no user is found with the given user_id.
    """
    logger = logging.getLogger(__name__)
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(
            f"/api/users/reset/{uid}/{token}/")

        subject = "Password Reset Request"
        message = f"Hi {user.first_name},\n\nYou requested a password reset. Click the link below to set a new password:\n{reset_link}\n\nIf you didn't request this, you can ignore this email.\n\nThanks,\nThe Forum-Beta Team"
        html_message = render_to_string(
            'emails/reset_password_email.html', {'user': user, 'reset_link': reset_link})
        try:
            send_email_task_no_ssl.delay(
                subject, message, [user.email], html_message)

            logger.info(f"Password reset email queued for {user.email}")
            return True

        except CeleryError as c:
            logger.error(f'Failed to queue password reset email: {c}')

    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False


def send_verification_email(user, request) -> bool:
    try:
        token = RefreshToken.for_user(user)

        verification_url = request.build_absolute_uri(
            f"{reverse('verify-email')}?{urlencode({'token': token})}"
        )

        subject = "Verify Your Email"
        message = f"Click the link to verify your email: {verification_url}"
        html_message = f"<p>Click <a href='{verification_url}'>here</a> to verify your email.</p>"

        send_email_task_no_ssl.delay(subject, message, [user.email], html_message)
        return True

    except CeleryError as ce:
        logger.error(f"Failed to send verification email: {ce}")
        return False
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False
    

def send_welcome_email(user, request: HttpRequest) -> bool:
    """
    Sends a welcome email to the user after successful registration or login using a template.
    
    Args:
        user: The User instance (custom User model).
        request: The HTTP request object to build absolute URLs.
    
    Returns:
        bool: True if the email task was successfully queued, False otherwise.
    """
    try:
        token = RefreshToken.for_user(user)

        welcome_url = request.build_absolute_uri(reverse('schema-swagger-ui'))
        verification_url = request.build_absolute_uri(
            f"{reverse('verify-email')}?{urlencode({'token': str(token)})}"
        ) if user.is_email_confirmed is False else None

        context = {
            'user_email': user.email,
            'welcome_url': welcome_url,
            'verification_url': verification_url,
            'current_year': datetime.now().year,
        }

        html_message = render_to_string('emails/welcome_email.html', context)

        message = (
            f"Hello {user.email},\n\n"
            "Thank you for joining our platform!\n"
            f"You can access your dashboard here: {welcome_url}\n"
        )
        if verification_url:
            message += f"\nPlease verify your email by clicking here: {verification_url}"

        subject = "Welcome to Our Platform!"

        send_email_task.delay(subject, message, [user.email], html_message)
        logger.info(f"Welcome email task queued for {user.email}")
        return True

    except NoReverseMatch as nre:
        logger.error(f"Failed to build URL for welcome email: {nre}")
        return False
    except CeleryError as ce:
        logger.error(f"Failed to queue welcome email task: {ce}")
        return False
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        return False
    

class TokenAuthSupportCookie(JWTAuthentication):
    """
    Extend the JWTAuthentication class to support cookie-based authentication.
    If no 'Authorization' header is provided, it falls back to the 'access_token' cookie.
    """
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            return super().authenticate(request)

        if 'access_token' in request.COOKIES:
            raw_token = request.COOKIES.get('access_token')
            if not raw_token:
                raise AuthenticationFailed('No token provided in cookie.')

            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)

        return None