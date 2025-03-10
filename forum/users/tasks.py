from forum.tasks import send_email_task
from celery import shared_task
from users.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


@shared_task
def send_reset_password_email(user_id):
    """
    Asynchronous task to generate a password reset link and queue an email for sending.
    Args:
        user_id (int): The ID of the user requesting a password reset.
    Raises:
        User.DoesNotExist: If no user is found with the given user_id.
    """
    logger.info("Sending reset password email...")

    try:
        user = User.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset_password/{uid}/{token}/"

        subject = "Password Reset Request"
        message = f"Hi {user.first_name},\n\nYou requested a password reset. Click the link below to set a new password:\n{reset_link}\n\nIf you didn't request this, you can ignore this email.\n\nThanks,\nThe Forum-Beta Team"
        html_message = render_to_string(
            'emails/reset_password_email.html', {'user': user, 'reset_link': reset_link})

        send_email_task.delay(subject, message, [user.email], html_message)

        logger.info(f"Password reset email queued for {user.email}")

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
