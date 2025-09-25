from allauth.account.adapter import DefaultAccountAdapter

from .utils import generate_verification_code


class CustomAccountAdapter(DefaultAccountAdapter):
    """Send short verification codes for email confirmation."""

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        ctx = {
            "user": emailconfirmation.email_address.user,
        }

        # Generate verification code for email confirmation
        code = generate_verification_code(emailconfirmation.key)

        ctx.update(
            {
                "code": code,
                "key": emailconfirmation.key,
                "activate_url": self.get_email_confirmation_url(
                    request, emailconfirmation
                ),
            }
        )

        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"

        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
