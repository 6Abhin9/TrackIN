from background_task import background
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import os
import requests

from .models import License, Profile, PlayerId

# OneSignal Configuration
ONESIGNAL_APP_ID = os.getenv('ONESIGNAL_APP_ID', '')
ONESIGNAL_API_KEY = os.getenv('ONESIGNAL_API_KEY', '')


@background(schedule=1)  # Runs in the background
def check_expiring_licenses():
    """Checks for expiring licenses and notifies License Managers and users."""
    print('Checking for expiring licenses...')
    today = datetime.today().date()
    notifications = []

    licenses = License.objects.all()

    for licen in licenses:
        if licen.expiry_date:
            days_left = (licen.expiry_date - today).days
            if days_left in [10, 5, 1]:  
                notifications.append({
                    "license_id": licen.id,
                    "license_number": licen.license_number,
                    "expiry_date": licen.expiry_date,
                    "days_left": days_left,
                    "message": f"Your license '{licen.license_number}' is expiring in {days_left} days!",
                })

                # Get all License Managers
                license_managers = Profile.objects.filter(role='license_manager')
                manager_emails = license_managers.values_list('email', flat=True)

                # Send email to License Managers
                if manager_emails:
                    send_mail(
                        "License Expiry Notification",
                        f"License '{licen.license_number}' is expiring in {days_left} days.",
                        "meddocxinc@gmail.com",  # Sender email
                        list(manager_emails),
                        fail_silently=False,
                    )
                    print(f"Email sent to License Managers: {list(manager_emails)}")

                # Send push notification to users
                users = PlayerId.objects.all()  
                user_ids = users.values_list('player_id', flat=True)
                print(user_ids)

                send_push_notification(user_ids, licen.license_number, days_left)
                if user_ids:
                    print('hiii');
                    

    if notifications:
        print("Expiring Licenses:", notifications)
    else:
        print("No licenses are expiring soon.", datetime.now())


def send_push_notification(user_ids, license_name, days_left):
    """Send push notifications using OneSignal."""
    try:
        payload = {
            "app_id": '18d9ac09-3b59-4855-8873-64ccfb81b69a',
            "contents": {"en": f"License '{license_name}' is expiring in {days_left} days!"},
            "included_segments": ["All"],
            "data": {"extra_data": f"License '{license_name}' is expiring soon!"},
        }

        if user_ids:
            payload["include_player_ids"] = list(user_ids)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic os_v2_app_ddm2ycj3lfeflcdtmtgpxanwtlv2l6fh3asuckfi3nddev3zrevpvljxke6n56geebhmz4cvtqwxc3tkfffl5a7xamfpr4xo6jxvdui",
        }
        response = requests.post(
            "https://onesignal.com/api/v1/notifications",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Failed to send notification: {e}")
