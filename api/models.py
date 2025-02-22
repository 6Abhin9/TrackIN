from django.db import models
from django.contrib.auth.models import AbstractUser


class Registration(models.Model):
    name=models.CharField(max_length=100,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    address=models.CharField(max_length=100,null=True)
    number=models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

class Profile(AbstractUser):
    REQUIRED_FIELDS=['username']
    USERNAME_FIELD='email'
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('license_manager', 'License Manager'),
        ('tender_manager', 'Tender Manager'),
        ('pndt_license_manager', 'PNDT License Manager'),
        ('internal_license_viewer','Internal License Viewer'),
        ('external_license_viewer','External License Viewer'),
        ('tender_viewer','Tender Viewer'),
        ('pndt_license_viewer','PNDT License Viewer'),
    ]


    username=models.CharField(max_length=100,null=True,blank=True)
    email=models.EmailField(unique=True)
    password_str=models.CharField(max_length=255,null=True,blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    
    
    
    def __str__(self):
        return self.email

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
    LICENSE_TYPE = [
        ('manufacturing_license', 'Manufacturing License'),
        ('test_license', 'Test License'),
        ('import_license', 'Import License'),
        ('export_license', 'Export License'),
    ]

    application_type=models.CharField(max_length=50,choices=LICENSE_TYPE)
    application_number=models.CharField(max_length=50, unique=True)
    license_number=models.CharField(max_length=50, unique=True)
    date_of_submission=models.DateField()
    date_of_approval=models.DateField()
    expiry_date=models.DateField()

    PRODUCT_TYPE = [
        ('choice1', 'choice1'),
        ('choice2', 'choice2'),
        ('choice3', 'choice3'),
        ('choice4', 'choice4'),
        
    ]
    product_type=models.CharField(max_length=50,choices=PRODUCT_TYPE)
    product_name=models.CharField(max_length=100)
    model_number=models.CharField(max_length=50)
    intended_use=models.TextField(null=True,blank=True)
    CLASS_OF_DEVICE_TYPE = [
        ('choice1', 'choice1'),
        ('choice2', 'choice2'),
        ('choice3', 'choice3'),
        ('choice4', 'choice4'),
    ]
    class_of_device_type=models.CharField(max_length=50,choices=CLASS_OF_DEVICE_TYPE)
    software=models.BooleanField(default=False)
    legal_manufacturer=models.TextField(null=True,blank=True)
    agent_address=models.TextField(null=True,blank=True)
    accesories=models.TextField(null=True,blank=True)
    shell_life=models.TextField(null=True,blank=True)
    pack_size=models.IntegerField(default=0)
    attachments=models.FileField(null=True,blank=True)

    def __str__(self):
        return self.product_name
    

class Notification(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    title=models.CharField(max_length=150,null=True,blank=True)
    content=models.TextField()
    time=models.DateTimeField(null=True,blank=True)
    

    def __str__(self):
        return self.title



class TenderManager(models.Model):
    tender_id=models.CharField(max_length=25, primary_key=True)
    tender_title=models.CharField(max_length=150)
    issuing_authority=models.TextField()
    tender_description=models.TextField(null=True, blank=True)
    tender_attachments=models.FileField(null=True, blank=True)
    EMD_amount=models.CharField(max_length=50)
    EMD_payment_status=models.BooleanField()
    payment_mode=[
        ('online','online'),
        ('offline','offline')
    ]
    EMD_payment_mode=models.CharField(max_length=100,choices=payment_mode,null=True,blank=True)
    EMD_payment_date=models.DateField(null=True,blank=True)
    transaction_number=models.CharField(max_length=100,null=True,blank=True)
    payment_attachments=models.FileField(null=True,blank=True)
    forfeiture_status=models.BooleanField(default=False)
    forfeiture_reason=models.TextField(null=True,blank=True)
    EMD_refund_status=models.BooleanField()
    EMD_refund_date=models.DateField(null=True,blank=True)
    bid_amount=models.CharField(max_length=100)
    bid_outcome=models.BooleanField()

    def __str__(self):
        return self.tender_title
# class TenderManager(models.Model):


class PNDT_License(models.Model):
    license_number=models.CharField(max_length=50)
    application_number=models.CharField(max_length=50)
    submission_date=models.DateField()
    expiry_date=models.DateField()
    approval_date=models.DateField()
    PRODUCT_TYPE = [
        ('choice1', 'choice1'),
        ('choice2', 'choice2'),
        ('choice3', 'choice3'),
        ('choice4', 'choice4'),
    ]
    product_type=models.CharField(max_length=150,choices=PRODUCT_TYPE)
    product_name=models.TextField()
    model_number=models.CharField(max_length=50)
    intended_use=models.TextField()
    CLASS_OF_DEVICE=[
        ('class1','class1'),
        ('class2','class2'),
        ('class3','class3'),
        ('ultrasonic','ultrasonic')
    ]
    class_of_device=models.CharField(max_length=50, choices=CLASS_OF_DEVICE)
    software_used=models.TextField()
    legal_manufacturer=models.TextField()
    authorize_agent_address=models.TextField()
    
    def __str__(self):
        return self.product_name


class PlayerId(models.Model):
    player_id=models.CharField(max_length=255)

    def __str__(self):
        return self.player_id