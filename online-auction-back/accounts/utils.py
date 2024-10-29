from django.core.mail import send_mail

def send_otp_email(user):
    user.generate_otp()  # Generate and save OTP with expiry
    subject = "Your OTP for Account Verification"
    message = f"Hello {user.first_name},\n\nYour OTP is {user.otp}. It will expire in 3 minutes."
    email_from = "your-email@example.com"
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)
