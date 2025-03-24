import logging
import unittest
from unittest.mock import MagicMock, patch

from forum.tasks import send_email_task, send_email_task_no_ssl

logger = logging.getLogger("forum.tasks")
logger.setLevel(logging.ERROR)

class TestEmailTasks(unittest.TestCase):
    
    @patch("forum.tasks.smtplib.SMTP")
    @patch("forum.tasks.settings")
    def test_send_email_task_no_ssl_success(self, mock_settings, mock_smtp):
        mock_settings.EMAIL_HOST = "smtp.example.com"
        mock_settings.EMAIL_PORT = 587
        mock_settings.EMAIL_HOST_USER = "user@example.com"
        mock_settings.EMAIL_HOST_PASSWORD = "password"
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        recipient_list = ["recipient@example.com"]
        subject = "Test Subject"
        message = "Test Message"
        
        result = send_email_task_no_ssl(subject, message, recipient_list)
        
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()

    @patch("forum.tasks.smtplib.SMTP")
    @patch("forum.tasks.settings")
    def test_send_email_task_no_ssl_failure(self, mock_settings, mock_smtp):
        mock_settings.EMAIL_HOST = "smtp.example.com"
        mock_settings.EMAIL_PORT = 587
        mock_settings.EMAIL_HOST_USER = "user@example.com"
        mock_settings.EMAIL_HOST_PASSWORD = "password"
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = Exception("SMTP error")
        
        recipient_list = ["recipient@example.com"]
        subject = "Test Subject"
        message = "Test Message"
        
        with self.assertRaises(Exception):
            send_email_task_no_ssl(subject, message, recipient_list)

    @patch("forum.tasks.send_mail")
    @patch("forum.tasks.settings")
    def test_send_email_task_success(self, mock_settings, mock_send_mail):
        mock_settings.EMAIL_HOST_USER = "user@example.com"
        mock_send_mail.return_value = 1  # Django send_mail повертає кількість відправлених листів

        recipient_list = ["recipient@example.com"]
        subject = "Test Subject"
        message = "Test Message"
        
        send_email_task(subject, message, recipient_list)
        
        mock_send_mail.assert_called_once_with(
            subject,
            message,
            mock_settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
            html_message=None
        )

    @patch("forum.tasks.send_mail")
    @patch("forum.tasks.settings")
    def test_send_email_task_failure(self, mock_settings, mock_send_mail):
        mock_settings.EMAIL_HOST_USER = "user@example.com"
        mock_send_mail.side_effect = Exception("SMTP error")
        
        recipient_list = ["recipient@example.com"]
        subject = "Test Subject"
        message = "Test Message"
        
        with self.assertLogs(logger, level="ERROR") as log:
            send_email_task(subject, message, recipient_list)
        
        self.assertIn("Failed to send email", log.output[0])

if __name__ == "__main__":
    unittest.main()