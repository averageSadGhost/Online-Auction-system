import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_otp_email(user):
    """
    Generate and send OTP email to user for account verification.

    Args:
        user: The user instance to send OTP to.
    """
    user.generate_otp()
    subject = "Your OTP for Account Verification"
    message = f"Hello {user.first_name},\n\nYour OTP is {user.otp}. It will expire in 3 minutes."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    try:
        send_mail(subject, message, email_from, recipient_list)
        logger.info(f"OTP email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {e}")
