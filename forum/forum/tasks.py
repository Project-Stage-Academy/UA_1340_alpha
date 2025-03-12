import logging
from typing import List

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

logger = logging.getLogger(__name__)


@shared_task
def send_email_task_no_ssl(subject: str, message: str, recipient_list: List[str], html_message=None):
    if not recipient_list:
        logger.warning("Attempt to send email with empty recipient list")
        return
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.starttls(context=context)

        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        for recipient in recipient_list:
            msg = MIMEText(html_message if html_message else message,
                           "html" if html_message else "plain")
            msg["Subject"] = subject
            msg["From"] = settings.EMAIL_HOST_USER
            msg["To"] = recipient

            server.sendmail(settings.EMAIL_HOST_USER,
                            recipient, msg.as_string())

        server.quit()
        logger.info(f"Email sent successfully to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")


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
