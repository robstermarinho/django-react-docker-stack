# authentication/urls.py

from django.urls import path
from .views import CustomVerifyEmailView
from dj_rest_auth.views import LoginView as DjRestAuthLoginView
from dj_rest_auth.registration.views import RegisterView as DjRestAuthRegisterView
from dj_rest_auth.registration.views import VerifyEmailView as DjRestAuthVerifyEmailView
urlpatterns = [
    # Authentication endpoints
    path("login/", DjRestAuthLoginView.as_view(), name="rest_login"),
    path("registration/", DjRestAuthRegisterView.as_view(), name="rest_register"),
    # Email verification endpoint
    path(
        "registration/verify-email/",
        CustomVerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
]
