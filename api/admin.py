from django.contrib import admin
from .models import Feedback, Registration, RecentlyViewed
from .models import Profile, AdditionalDetails,License,Notification,TenderManager,PNDT_License,PersonalDetails,OTPVerification


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'get_is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('email',)
    actions = ['approve_selected_users']

    def get_is_approved(self, obj):
        return obj.is_approved
    get_is_approved.boolean = True  
    get_is_approved.short_description = "Approved"

    # Admin can approve multiple external users
    def approve_selected_users(self, request, queryset):
        count = queryset.filter(role='external_license_viewer', is_approved=False).update(is_approved=True)
        self.message_user(request, f"{count} external user(s) approved successfully.")
    approve_selected_users.short_description = "Approve selected external users"

    # Allow editing `is_approved` only for external users
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.role != 'external_license_viewer':
            return ('is_approved',)  
        return ()
    
#Register models with admin site
admin.site.register(Registration)
admin.site.register(Profile, ProfileAdmin)  #Use the custom admin class
admin.site.register(AdditionalDetails)
admin.site.register(License)
admin.site.register(Notification)
admin.site.register(TenderManager)
admin.site.register(PNDT_License)
admin.site.register(PersonalDetails)
admin.site.register(OTPVerification)
