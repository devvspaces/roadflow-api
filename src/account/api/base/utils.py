
from account.models import User
from utils.base.email import render_email_message


def send_otp_email(user: User, request, template: str, subject: str):
    """
    Sends a otp email to user.
    """

    otp = user.set_otp()
    message = render_email_message(
        request, template, {"otp": otp}
    )
    return user.email_user(subject, message)


def send_verification_email(user: User, request):
    """
    Sends a verification email to user.
    """

    return send_otp_email(
        user, request,
        'account/email/verify_email.html', 'Verify your email')


def send_password_reset_email(user: User, request):
    """
    Sends a password reset email to user.
    """

    return send_otp_email(
        user, request,
        'account/email/password_reset.html', 'Reset your password')
