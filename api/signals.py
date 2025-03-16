# api/signals.py
from django.dispatch import Signal
from django.core.mail import send_mail
from django.conf import settings
from django.dispatch import receiver

# Step 1: Define the custom signal
user_created = Signal()

# Step 2: Define the signal handler
@receiver(user_created)
def send_password_email(sender, instance, **kwargs):
    """
    Signal to send an email with the auto-generated password when a new Profile is created.
    """
    subject = 'Your Account Has Been Created'
    message = f'Your account has been created. Use this password to access your account: {instance.password_str}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [instance.email]  # Send the email to the user's email address

    # Send the email
    send_mail(subject, message, email_from, recipient_list)