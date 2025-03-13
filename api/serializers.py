from rest_framework import serializers
from .models import Feedback, PersonalDetails, Registration
from .models import Profile,AdditionalDetails,License,Notification,TenderManager,PNDT_License, TenderManager


class RegistrationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Registration
        fields='__all__'

class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'

class PersonalDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = '__all__'

    def validate_gender(self, value):
        # Optional: Add validation for gender
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError("Gender cannot be empty.")
        return value

    def validate_blood_group(self, value):
        # Optional: Add validation for blood group
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError("Blood group cannot be empty.")
        return value

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


class TenderDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model=TenderManager
        fields='__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class PNDTLicenseSerializers(serializers.ModelSerializer):
    class Meta:
        model=PNDT_License
        fields='__all__'


class TenderManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderManager
        fields = '__all__'