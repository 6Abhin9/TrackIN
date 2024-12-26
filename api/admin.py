from django.contrib import admin
from .models import Registration
from .models import Profile, AdditionalDetails,License

admin.site.register(Registration)
admin.site.register(Profile)
admin.site.register(AdditionalDetails)
admin.site.register(License)