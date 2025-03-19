from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Profile(AbstractUser):
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('license_manager', 'License Manager'),
        ('tender_manager', 'Tender Manager'),
        ('pndt_license_manager', 'PNDT License Manager'),
        ('internal_license_viewer', 'Internal License Viewer'),
        ('external_license_viewer', 'External License Viewer'),
        ('tender_viewer', 'Tender Viewer'),
        ('pndt_license_viewer', 'PNDT License Viewer'),
    ]

    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password_str = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    authority = models.CharField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)  # Approval required only for external users
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)  # New field for profile image

    def __str__(self):
        return self.email

    # Ensure only external users require approval
    @property
    def is_active(self):
        if self.role == "external_license_viewer":
            return self.is_approved
        return True
    
class PersonalDetails(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='personal_details')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)  # Free-text input
    blood_group = models.CharField(max_length=50, null=True, blank=True)  # Free-text input
    nationality = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"Personal Details for {self.profile.email}"

class AdditionalDetails(models.Model):
    profile=models.OneToOneField(Profile,on_delete=models.CASCADE)
    state=models.CharField(max_length=50,null=True,blank=True)
    district=models.CharField(max_length=50,null=True,blank=True)
    pincode=models.CharField(max_length=10,null=True,blank=True)
    phone=models.CharField(max_length=10,null=True,blank=True)
    bio=models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.profile.first_name
    


class License(models.Model):
    # Updated LICENSE_TYPE choices
    LICENSE_TYPE = [
        ('manufacturing_license', 'Manufacturing License'),
        ('test_license', 'Test License'),
        ('import_license', 'Import License'),
        ('warehouse_license', 'Warehouse License'),  # Changed from 'export_license'
    ]

    application_type = models.CharField(max_length=50, choices=LICENSE_TYPE)
    application_number = models.CharField(max_length=50, unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    date_of_submission = models.DateField()
    date_of_approval = models.DateField()
    expiry_date = models.DateField()

    # Removed PRODUCT_TYPE choices and changed to TextField
    product_type = models.TextField()  # Changed from CharField with choices
    product_name = models.CharField(max_length=100)
    model_number = models.CharField(max_length=50)
    intended_use = models.TextField(null=True, blank=True)

    # Updated CLASS_OF_DEVICE_TYPE choices to uppercase
    CLASS_OF_DEVICE_TYPE = [
        ('A', 'A'),  
        ('B', 'B'),  
        ('C', 'C'),  
        ('D', 'D'),  
    ]
    class_of_device_type = models.CharField(max_length=50, choices=CLASS_OF_DEVICE_TYPE)
    software = models.BooleanField(default=False)
    legal_manufacturer = models.TextField(null=True, blank=True)
    agent_address = models.TextField(null=True, blank=True)
    accesories = models.TextField(null=True, blank=True)
    shelf_life = models.TextField(null=True, blank=True)
    pack_size = models.IntegerField(default=0)
    attachments = models.FileField(null=True, blank=True)
    viewed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.product_name
    

class Notification(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_notifications')
    sender_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    content = models.TextField()
    time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback from {self.name} ({self.email})"


class TenderManager(models.Model):
    tender_id = models.CharField(max_length=25, primary_key=True)
    tender_title = models.CharField(max_length=150)
    issuing_authority = models.TextField()
    tender_description = models.TextField(null=True, blank=True)
    tender_attachments = models.FileField(null=True, blank=True)
    EMD_amount = models.CharField(max_length=50)
    payment_mode = [
        ('online', 'online'),
        ('offline', 'offline')
    ]
    EMD_payment_mode = models.CharField(max_length=100, choices=payment_mode, null=True, blank=True)
    EMD_payment_date = models.DateField(null=True, blank=True)
    transaction_number = models.CharField(max_length=100, null=True, blank=True)
    payment_attachments = models.FileField(null=True, blank=True)
    TENDER_STATUS = [
        ('applied', 'applied'),
        ('completed', 'completed')
    ]
    tender_status = models.CharField(max_length=100, choices=TENDER_STATUS, default='applied')
    forfeiture_status = models.BooleanField(default=False)
    forfeiture_reason = models.TextField(null=True, blank=True)
    EMD_refund_status = models.BooleanField()
    EMD_refund_date = models.DateField(null=True, blank=True)
    BID_OUTCOME = [
        ('won', 'won'),
        ('lost', 'lost'),
        ('not_declared', 'not_declared')
    ]
    bid_outcome = models.CharField(max_length=100, choices=BID_OUTCOME, default='not_declared')
    tender_handler = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'tender_viewer'})

    def __str__(self):
        return self.tender_id


class PNDT_License(models.Model):
    license_number = models.CharField(max_length=50)
    application_number = models.CharField(max_length=50)
    submission_date = models.DateField()
    expiry_date = models.DateField()
    approval_date = models.DateField()
    
    product_type = models.TextField()
    product_name = models.TextField()
    model_number = models.CharField(max_length=50)
    
    STATES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry')
    ]
    state = models.CharField(max_length=50, choices=STATES, default='Andhra Pradesh')
    
    intended_use = models.TextField()
    
    CLASS_OF_DEVICE = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]
    class_of_device = models.CharField(max_length=1, choices=CLASS_OF_DEVICE)
    
    software = models.BooleanField(default=False)
    legal_manufacturer = models.TextField()
    authorize_agent_address = models.TextField()
    attachments = models.FileField(null=True, blank=True)
    
    def __str__(self):
        return self.product_name


class PlayerId(models.Model):
    player_id=models.CharField(max_length=255)

    def __str__(self):
        return self.player_id
    
class RecentlyViewed(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE,null=True,blank=True)
    licen=models.ForeignKey(License,on_delete=models.CASCADE,null=True,blank=True)
    viewed_date=models.DateTimeField(null=True,blank=True)



from django.db import models
from django.utils.timezone import now  # Import the `now` function
from .models import Profile  # Import the Profile model

class OTPVerification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)  # Use the imported `now` function

    def is_valid(self):
        # Check if the OTP is valid (created within the last 300 seconds)
        return (now() - self.created_at).seconds < 300

    def __str__(self):
        return f"OTP for {self.user.email}"