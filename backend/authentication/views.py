from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.adapter import get_adapter
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from .serializers import CustomVerifyEmailSerializer
import logging
import hashlib
import hmac
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomVerifyEmailView(VerifyEmailView):
    """
    Enhanced email verification view with code and key support
    Implements security features similar to dj-rest-auth VerifyEmailView
    """
    permission_classes = (AllowAny,)
    serializer_class = CustomVerifyEmailSerializer

    # Security settings
    CODE_EXPIRY_MINUTES = 15
    MAX_VERIFICATION_ATTEMPTS = 5
    RATE_LIMIT_WINDOW = 60  # seconds

    def get_serializer(self, *args, **kwargs):
        return CustomVerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.info(f"Email verification request from IP: {request.META.get('REMOTE_ADDR')}")

        # Check if 'code' exists in request (custom behavior)
        if "code" in request.data:
            return self.verify_by_code_secure(request)

        # Use original secure behavior for 'key' verification
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Key verification failed: {e}")
            return Response(
                {"detail": _("Invalid verification key.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @transaction.atomic
    def verify_by_code_secure(self, request):
        """
        Secure code verification with proper validation and security checks
        """
        code = request.data.get("code")
        email = request.data.get("email")

        # Input validation
        if not code or not email:
            return Response(
                {"detail": _("Both email and verification code are required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get user and email address
            user = User.objects.select_for_update().get(email=email)
            email_address = EmailAddress.objects.select_for_update().get(
                email=email, user=user
            )

            # Check if already verified
            if email_address.verified:
                return Response(
                    {"detail": _("Email is already verified.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Find valid confirmation record
            confirmation = self.get_valid_confirmation(email_address, code)
            if not confirmation:
                # Log failed attempt for security monitoring
                logger.warning(
                    f"Invalid verification code attempt for {email} from IP: {request.META.get('REMOTE_ADDR')}"
                )
                return Response(
                    {"detail": _("Invalid or expired verification code.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Perform secure confirmation
            self.perform_confirmation(request, confirmation, email_address)

            logger.info(f"Email {email} successfully verified with code")

            return Response(
                {"detail": _("Email successfully verified.")},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            logger.warning(f"Verification attempt for non-existent user: {email}")
            return Response(
                {"detail": _("Invalid email address.")},
                status=status.HTTP_400_BAD_REQUEST,  # Don't reveal user existence
            )
        except EmailAddress.DoesNotExist:
            logger.warning(f"Verification attempt for non-existent email address: {email}")
            return Response(
                {"detail": _("Invalid email address.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            logger.error(f"Validation error in email verification: {e}")
            return Response(
                {"detail": _("Verification failed. Please try again.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error in verify_by_code_secure: {e}")
            return Response(
                {"detail": _("Verification failed. Please contact support.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_valid_confirmation(self, email_address, code):
        """
        Get valid confirmation record with proper validation
        """
        try:
            # Find confirmation records for this email address
            confirmations = EmailConfirmation.objects.filter(
                email_address=email_address
            ).select_for_update()

            for confirmation in confirmations:
                # Check if code matches (implement proper validation)
                if self.validate_verification_code(confirmation, code):
                    # Check expiration
                    if self.is_confirmation_expired(confirmation):
                        logger.info(f"Expired confirmation found for {email_address.email}")
                        continue

                    return confirmation

            return None

        except Exception as e:
            logger.error(f"Error finding valid confirmation: {e}")
            return None

    def validate_verification_code(self, confirmation, provided_code):
        """
        Validate verification code with proper security
        In a real implementation, you'd store and validate against proper codes
        """
        # For now, we'll use a simple approach based on confirmation key
        # In production, implement proper code generation and validation
        expected_code = self.generate_code_from_key(confirmation.key)
        return provided_code == expected_code

    def generate_code_from_key(self, key):
        """
        Generate 6-digit code from confirmation key
        This is a simplified implementation - use proper cryptographic methods in production
        """
        # Use HMAC to generate consistent code from key
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret')
        digest = hmac.new(
            secret_key.encode('utf-8'),
            key.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Extract 6 digits from digest
        code = ''.join(filter(str.isdigit, digest))[:6]
        return code.zfill(6)  # Pad with zeros if needed

    def is_confirmation_expired(self, confirmation):
        """
        Check if confirmation has expired
        """
        if not confirmation.sent:
            return True

        expiry_time = confirmation.sent + timedelta(minutes=self.CODE_EXPIRY_MINUTES)
        return timezone.now() > expiry_time

    def perform_confirmation(self, request, confirmation, email_address):
        """
        Perform the actual confirmation with proper security measures
        """
        try:
            # Use the adapter for proper confirmation flow
            adapter = get_adapter(request)

            # Confirm the email using allauth's proper method
            confirmation.confirm(request)

            # Additional security: ensure email address is marked as verified
            email_address.refresh_from_db()
            if not email_address.verified:
                email_address.set_verified()

            logger.info(f"Email confirmation completed for {email_address.email}")

        except Exception as e:
            logger.error(f"Error performing confirmation: {e}")
            raise ValidationError("Confirmation failed")
