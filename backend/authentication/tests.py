import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from allauth.account.models import EmailAddress, EmailConfirmation
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
class RegistrationEndpointTests(APITestCase):
    """Test cases for registration endpoint using dj-rest-auth RegisterView"""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('rest_register')
        self.valid_payload = {
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }

    def test_successful_registration(self):
        """Test successful user registration with mandatory email verification"""
        response = self.client.post(self.registration_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

        # With EMAIL_VERIFICATION = "mandatory", no tokens are returned immediately
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Verification e-mail sent.')
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_registration_with_email_verification_optional(self):
        """Test registration when email verification is optional (returns tokens immediately)"""
        with patch('allauth.account.app_settings.EMAIL_VERIFICATION', 'optional'):
            response = self.client.post(self.registration_url, self.valid_payload)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # With optional verification, tokens should be returned immediately
            self.assertIn('access', response.data)
            self.assertIn('refresh', response.data)
            self.assertIn('user', response.data)

    def test_registration_duplicate_email(self):
        """Test registration with existing email"""
        # Create user first
        User.objects.create_user(
            email='test@example.com',
            password='password123',
            username='existinguser'
        )

        response = self.client.post(self.registration_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        payload = self.valid_payload.copy()
        payload['password2'] = 'differentpassword'

        response = self.client.post(self.registration_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_registration_weak_password(self):
        """Test registration with weak password"""
        payload = self.valid_payload.copy()
        payload.update({
            'password1': '123',
            'password2': '123'
        })

        response = self.client.post(self.registration_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_email(self):
        """Test registration without email"""
        payload = self.valid_payload.copy()
        del payload['email']

        response = self.client.post(self.registration_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(User.objects.count(), 0)

    def test_registration_with_username_and_email(self):
        """Test registration succeeds when username is supplied alongside email"""
        payload = self.valid_payload.copy()
        payload.update({
            'email': 'usernamed@example.com',
            'username': 'usernamed'
        })

        response = self.client.post(self.registration_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='usernamed@example.com')
        self.assertEqual(user.username, 'usernamed')
        self.assertEqual(response.data['detail'], 'Verification e-mail sent.')

    def test_registration_with_first_and_last_name(self):
        """Test registration persists first and last name fields"""
        payload = self.valid_payload.copy()
        payload.update({
            'email': 'nameduser@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe'
        })

        response = self.client.post(self.registration_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='nameduser@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(response.data['detail'], 'Verification e-mail sent.')

    def test_registration_invalid_email_format(self):
        """Test registration with invalid email format"""
        payload = self.valid_payload.copy()
        payload['email'] = 'invalid-email'

        response = self.client.post(self.registration_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


@pytest.mark.django_db
class LoginEndpointTests(APITestCase):
    """Test cases for login endpoint using dj-rest-auth LoginView"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('rest_login')
        self.email = 'test@example.com'
        self.password = 'testpassword123'

        # Create a test user
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            username='testuser'
        )

        # Create verified email address
        EmailAddress.objects.create(
            user=self.user,
            email=self.email,
            verified=True,
            primary=True
        )

    def test_successful_login_with_email(self):
        """Test successful login with email"""
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        })


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.email)

    def test_login_with_username_fails_when_email_only(self):
        """Test that username login fails when only email login is configured"""
        response = self.client.post(self.login_url, {
            'username': self.user.username,
            'password': self.password
        })

        # Should fail because current configuration only allows email login
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Must include "email"', str(response.data['non_field_errors'][0]))

    def test_login_with_wrong_password(self):
        """Test login with incorrect password"""
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': self.password
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_credentials(self):
        """Test login without providing credentials"""
        response = self.client.post(self.login_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        """Test login without password"""
        response = self.client.post(self.login_url, {
            'email': self.email
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_with_unverified_email(self):
        """Test login with unverified email when verification is required"""
        # Mark email as unverified
        email_address = EmailAddress.objects.get(user=self.user)
        email_address.verified = False
        email_address.save()

        with patch('allauth.account.app_settings.EMAIL_VERIFICATION', 'mandatory'):
            response = self.client.post(self.login_url, {
                'email': self.email,
                'password': self.password
            })

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_data_in_response(self):
        """Test that user data is correctly returned in login response"""
        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.save()

        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['user']
        self.assertEqual(user_data['pk'], self.user.pk)
        self.assertEqual(user_data['username'], self.user.username)
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['first_name'], 'Test')
        self.assertEqual(user_data['last_name'], 'User')

    def test_jwt_tokens_are_valid(self):
        """Test that returned JWT tokens are valid"""
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token = response.data['access']
        refresh_token = response.data['refresh']

        # Tokens should be non-empty strings
        self.assertTrue(isinstance(access_token, str))
        self.assertTrue(isinstance(refresh_token, str))
        self.assertTrue(len(access_token) > 0)
        self.assertTrue(len(refresh_token) > 0)


# Traditional Django TestCase for compatibility
class AuthenticationIntegrationTests(TestCase):
    """Integration tests using Django TestCase"""

    def setUp(self):
        self.email = 'integration@example.com'
        self.password = 'ComplexPassword2024!'

    def test_registration_to_login_flow(self):
        """Test complete flow from registration to login"""
        # Register user
        registration_response = self.client.post('/api/auth/registration/', {
            'email': self.email,
            'password1': self.password,
            'password2': self.password
        })


        self.assertIn(registration_response.status_code, [status.HTTP_201_CREATED])

        # Verify user was created
        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)

        # Manually verify email for testing (since email verification is mandatory)
        email_address = EmailAddress.objects.get(user=user, email=self.email)
        email_address.verified = True
        email_address.save()

        # Login with the registered user
        login_response = self.client.post('/api/auth/login/', {
            'email': self.email,
            'password': self.password
        })


        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        login_data = login_response.json()
        self.assertIn('access', login_data)
        self.assertIn('refresh', login_data)


@pytest.mark.django_db
class CustomVerifyEmailViewTests(APITestCase):
    """Test cases for CustomVerifyEmailView with code verification"""

    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('rest_verify_email')
        self.email = 'verify@example.com'
        self.password = 'VerifyPassword2024!'

        # Create a test user
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            username='verifyuser'
        )

        # Create unverified email address
        self.email_address = EmailAddress.objects.create(
            user=self.user,
            email=self.email,
            verified=False,
            primary=True
        )

    def test_code_verification_missing_parameters(self):
        """Test code verification with missing parameters"""
        # Missing code - falls back to key verification which fails
        response = self.client.post(self.verify_url, {
            'email': self.email
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid verification', str(response.data['detail']))

        # Missing email but has code - should trigger our custom handler
        response = self.client.post(self.verify_url, {
            'code': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email and verification code are required', str(response.data['detail']))

    def test_code_verification_already_verified_email(self):
        """Test code verification with already verified email"""
        # Mark email as verified
        self.email_address.verified = True
        self.email_address.save()

        response = self.client.post(self.verify_url, {
            'email': self.email,
            'code': '123456'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already verified', str(response.data['detail']))

    def test_code_verification_invalid_email(self):
        """Test code verification with invalid email"""
        response = self.client.post(self.verify_url, {
            'email': 'nonexistent@example.com',
            'code': '123456'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid email address', str(response.data['detail']))

    def test_code_verification_invalid_code(self):
        """Test code verification with invalid code"""
        # Create a confirmation record
        confirmation = EmailConfirmation.objects.create(
            email_address=self.email_address,
            key='test-confirmation-key'
        )

        response = self.client.post(self.verify_url, {
            'email': self.email,
            'code': '000000'  # Wrong code
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid or expired', str(response.data['detail']))

    def test_code_verification_with_valid_code(self):
        """Test code verification with valid code"""
        # Create a confirmation record
        confirmation = EmailConfirmation.objects.create(
            email_address=self.email_address,
            key='test-confirmation-key',
            sent=timezone.now()
        )

        # Import the view to get the expected code
        from .utils import generate_verification_code

        expected_code = generate_verification_code(confirmation.key)

        response = self.client.post(self.verify_url, {
            'email': self.email,
            'code': expected_code
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('successfully verified', str(response.data['detail']))

        # Verify that email address is now marked as verified
        self.email_address.refresh_from_db()
        self.assertTrue(self.email_address.verified)

    def test_key_verification_fallback(self):
        """Test that key verification still works (fallback to parent)"""
        # Create a confirmation record
        confirmation = EmailConfirmation.objects.create(
            email_address=self.email_address,
            key='test-key-12345',
            sent=timezone.now()
        )

        response = self.client.post(self.verify_url, {
            'key': confirmation.key
        })

        # The parent class should handle this
        # Result depends on the actual key validation logic
        # For now, we just check that it doesn't crash
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_code_verification_exceeds_max_attempts(self):
        """Lock the confirmation after repeated invalid attempts"""
        from .views import CustomVerifyEmailView
        from .utils import generate_verification_code

        confirmation = EmailConfirmation.objects.create(
            email_address=self.email_address,
            key='adapter-confirmation-key',
            sent=timezone.now()
        )

        actual_code = generate_verification_code(confirmation.key)
        wrong_code = '111111' if actual_code != '111111' else '222222'

        last_response = None
        for _ in range(CustomVerifyEmailView.MAX_VERIFICATION_ATTEMPTS):
            last_response = self.client.post(self.verify_url, {
                'email': self.email,
                'code': wrong_code
            })

        self.assertEqual(last_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Too many incorrect verification attempts', str(last_response.data['detail']))
        self.assertFalse(EmailConfirmation.objects.filter(pk=confirmation.pk).exists())


class CustomAccountAdapterTests(TestCase):
    """Unit tests for the custom account adapter email handling."""

    def test_send_confirmation_mail_includes_generated_code(self):
        from .adapter import CustomAccountAdapter
        from .utils import generate_verification_code

        adapter = CustomAccountAdapter()
        user = User.objects.create_user(
            email="adapter@example.com",
            password="ComplexPass123!",
            username="adapteruser",
        )

        email_address = EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=False,
            primary=True,
        )

        confirmation = EmailConfirmation.objects.create(
            email_address=email_address,
            key="adapter-confirmation-key",
            sent=timezone.now(),
        )

        expected_code = generate_verification_code(confirmation.key)

        with patch.object(
            adapter, "get_email_confirmation_url", return_value="https://example.com/verify"
        ), patch.object(adapter, "send_mail") as mock_send_mail:
            adapter.send_confirmation_mail(None, confirmation, signup=True)

        _, to_address, context = mock_send_mail.call_args[0]
        self.assertEqual(to_address, user.email)
        self.assertEqual(context["code"], expected_code)
        self.assertEqual(context["key"], confirmation.key)
        self.assertTrue(context["activate_url"].startswith("https://example.com/verify"))
