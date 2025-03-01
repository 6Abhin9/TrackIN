from background_task import background
from datetime import datetime
from django.conf import settings
from .models import License, PlayerId  # Assuming Profile model has user details
import os
import requests

# OneSignal Configuration
ONESIGNAL_APP_ID = os.getenv('APP_ID', '')
ONESIGNAL_API_KEY = os.getenv('API_KEY', '')

@background(schedule=1)  
def check_expiring_licenses():
    print('hii')
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

                users = PlayerId.objects.all() 
                user_ids = users.values_list('player_id', flat=True)

                if user_ids:
                    send_push_notification(user_ids, licen.name, days_left)

    if notifications:
        send_push_notification('', 'jjjj', 'hhh')

        print("Expiring Licenses:", notifications)
    else:
        print("No licenses are expiring soon." ,datetime.now())

def send_push_notification(user_ids, license_name, days_left):
    """Send push notifications using OneSignal"""
    try:
        # Prepare the notification payload
        payload = {
            "app_id": '18d9ac09-3b59-4855-8873-64ccfb81b69a',
            "contents": {"en": f"License '{license_name}' is expiring in {days_left} days!"},
            "included_segments": ["All"],
            "data": {"extra_data": f"License '{license_name}' is expiring soon!"},
        }

        # If specific user IDs are provided, send to those users
        if user_ids:
            payload["include_player_ids"] = user_ids

        # Send the request to OneSignal API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic os_v2_app_ddm2ycj3lfeflcdtmtgpxanwtlv2l6fh3asuckfi3nddev3zrevpvljxke6n56geebhmz4cvtqwxc3tkfffl5a7xamfpr4xo6jxvdui",
        }
        response = requests.post(
            "https://onesignal.com/api/v1/notifications",
            json=payload,
            headers=headers
        )

        # Check if the request was successful
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Failed to send notification: {e}")