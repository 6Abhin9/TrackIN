from background_task import background
from datetime import datetime
from onesignal_sdk.client import Client
from django.conf import settings
from .models import License, Profile  # Assuming Profile model has user details

# OneSignal Configuration
ONESIGNAL_APP_ID = ''
ONESIGNAL_API_KEY = ''
onesignal_client = Client(app_id=ONESIGNAL_APP_ID, rest_api_key=ONESIGNAL_API_KEY)

@background(schedule=10)  
def check_expiring_licenses():
    today = datetime.today().date()
    notifications = []

    licenses = License.objects.all()
    for licen in licenses:
        if licen.expiry_date:
            days_left = (licen.expiry_date - today).days
            if days_left in [10, 5, 1]:  # Send notifications on these days
                notifications.append({
                    "license_id": licen.id,
                    "license_name": licen.name,
                    "expiry_date": licen.expiry_date,
                    "days_left": days_left,
                    "message": f"Your license '{licen.name}' is expiring in {days_left} days!",
                })

                # Fetch users associated with this license
                users = Profile.objects.filter(license=licen)  # Assuming Profile has license relation
                user_ids = [user.onesignal_player_id for user in users if user.onesignal_player_id]  # Collect OneSignal IDs

                if user_ids:
                    send_push_notification(user_ids, licen.name, days_left)

    if notifications:
        print("Expiring Licenses:", notifications)
    else:
        print("No licenses are expiring soon.")

def send_push_notification(user_ids, license_name, days_left):
    """Send push notifications using OneSignal"""
    try:
        response = onesignal_client.send_notification(
            contents={"en": f"Your license '{license_name}' is expiring in {days_left} days!"},
            include_player_ids=user_ids,  # Send to specific users
            headings={"en": "License Expiry Alert"},
            priority=10
        )
        print(f"Notification sent: {response}")
    except Exception as e:
        print(f"Failed to send notification: {e}")
