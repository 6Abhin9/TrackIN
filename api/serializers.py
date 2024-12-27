from rest_framework import serializers
from .models import Registration
from .models import Profile,AdditionalDetails,License,Notification


class RegistrationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Registration
        fields='__all__'

class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'

class AdditionalDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model=AdditionalDetails
        fields='__all__'

class LicenseDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model=License
        fields='__all__'

class AdditionalDetailsGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=AdditionalDetails
        fields='__all__'
        depth=1

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'profile' in representation:  # Check if profile is included in the representation
            profile_data = representation['profile']
            profile_data.pop('password', None)  # Remove the password field
            profile_data.pop('last_login', None)  # Remove the password field
        return representation
    
class NotificationsDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Notification
        fields='__all__'