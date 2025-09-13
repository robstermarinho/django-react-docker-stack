# core/views.py

from django.http import JsonResponse


def home(request):
    return JsonResponse({"status": "Welcome to the API"}, status=200)
