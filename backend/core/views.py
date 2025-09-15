# core/views.py

from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime


def home(request):

    if request.GET.get("mail_test") == "1" and settings.DEBUG:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        send_mail(
            "Test Email",
            f"This is a test email sent at {now}",
            "test@example.com",
            ["test@example.com"],
        )
        return JsonResponse({"status": "Test email sent"}, status=200)

    return JsonResponse({"status": "Welcome to the API"}, status=200)
