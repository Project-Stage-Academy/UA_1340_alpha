
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from forum.tasks import send_email_task_no_ssl
from celery.exceptions import CeleryError
import logging


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
