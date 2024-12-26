from rest_framework import serializers
from .models import Registration
from .models import Profile,AdditionalDetails,License


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