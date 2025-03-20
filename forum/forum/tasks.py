import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task_no_ssl(self, subject: str, message: str, recipient_list: List[str], html_message=None):
    if not recipient_list:
        logger.warning("Attempt to send email with empty recipient list")
        return False

    server = None

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.starttls(context=context)

        logger.info('Logging into SMTP server...')
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        for recipient in recipient_list:
            try:
                msg = MIMEText(html_message if html_message else message,
                               "html" if html_message else "plain")
                msg["Subject"] = subject
                msg["From"] = settings.EMAIL_HOST_USER
                msg["To"] = recipient

                server.sendmail(settings.EMAIL_HOST_USER,
                                recipient, msg.as_string())
                logger.info(f'Email sent successfully to {recipient}')
            except Exception as e:
                logger.error(f'Failed to send email to {recipient}: {e}')
                raise
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(
                f'Max retries exceeded for sending email: {recipient_list}')
    finally:
        if server is not None:
            try:
                logger.info('Closing SMTP connection...')
                server.quit()
            except Exception as e:
                logger.error(f'Error while closing the connection {e}')

    return True


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
