from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from forum.tasks import send_email_task


class SendEmailAPIView(APIView):
    def post(self, request):
        subject = request.data.get("subject")
        message = request.data.get("message")  # Plain text version
        html_message = request.data.get("html_message")  # HTML version
        recipient = request.data.get("recipient")  # List of emails

        if not subject or not message or not recipient:
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        send_email_task.delay(subject, message, [recipient], html_message)

        return Response({"success": "HTML Email is being sent"}, status=status.HTTP_202_ACCEPTED)
