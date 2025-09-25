from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.registration.views import VerifyEmailSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from allauth.account import app_settings as allauth_account_settings
from allauth.utils import get_username_max_length

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_account_settings.USERNAME_MIN_LENGTH,
        required=False,
    )
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, email):
        email = super().validate_email(email)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        })
        return data


class CustomVerifyEmailSerializer(VerifyEmailSerializer):
    code = serializers.CharField(required=False, help_text="6-digit verification code")
    email = serializers.EmailField(
        required=False, help_text="Email to verify (optional if user is logged in)"
    )
    key = serializers.CharField(required=False, help_text="Legacy verification key")

    def validate(self, attrs):
        # Must have either 'code' or 'key'
        if not attrs.get("code") and not attrs.get("key"):
            raise serializers.ValidationError("Either 'code' or 'key' is required.")
        return attrs
