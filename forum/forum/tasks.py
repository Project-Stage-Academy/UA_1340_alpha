import logging
from typing import List

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_email_task(subject: str, message: str, recipient_list: List[str], html_message=None):
    if not recipient_list:
        logger.warning("Attempt to send email with empty recipient list")
        return

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Email sent successfully to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
