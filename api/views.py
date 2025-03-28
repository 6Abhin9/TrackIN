from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import FeedbackSerializer
from django.shortcuts import get_object_or_404
from .models import Profile,License,AdditionalDetails,Notification,Tenders,PNDT_License,PersonalDetails
from .serializers import AdditionalDetailsSerializers,LicenseDetailsSerializers,AdditionalDetailsGetSerializer,NotificationsDetailsSerializers,PersonalDetailsSerializers
from .serializers import TenderDetailsSerializers
from .serializers import PNDTLicenseSerializers,ProfileSerializers
from datetime import datetime, timedelta
from .models import PlayerId
from datetime import datetime
from django.utils.timezone import now
from django.http import JsonResponse
from django.views import View
from django.db.models import Sum, Q, Count
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .models import Profile, OTPVerification

import random
import string

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken 
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from .signals import user_created  # Import the custom signal


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        player_id = request.data.get('player_id')

        # Authenticate user
        user = authenticate(username=email, password=password)

        if user is not None:
            if player_id:
                player, created = PlayerId.objects.get_or_create(player_id=player_id)
                if created:
                    player.save()

            # Fetch additional details
            personal_details = PersonalDetails.objects.filter(profile=user).first()
            additional_details = AdditionalDetails.objects.filter(profile=user).first()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,  # Include username in the response
                    'role': user.role,
                    'image': user.image.url if user.image else None,  # Include the profile image URL
                },
                'personal_details': {
                    'date_of_birth': personal_details.date_of_birth if personal_details else None,
                    'gender': personal_details.gender if personal_details else None,
                    'blood_group': personal_details.blood_group if personal_details else None,
                    'nationality': personal_details.nationality if personal_details else None,
                },
                'additional_details': {
                    'state': additional_details.state if additional_details else None,
                    'district': additional_details.district if additional_details else None,
                    'pincode': additional_details.pincode if additional_details else None,
                    'phone': additional_details.phone if additional_details else None,
                    'bio': additional_details.bio if additional_details else None,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
def generate_random_password(length=12):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits

    all_characters = lowercase_letters + uppercase_letters + digits 
    password = [
        random.choice(lowercase_letters),
        random.choice(uppercase_letters),
        random.choice(digits),
    ]

    password += random.choices(all_characters, k=length - 4)
    random.shuffle(password)
    print(''.join(password))
    return ''.join(password)


class AdminAddUsersApi(APIView):
    def post(self, request):
        data = request.data
        password = generate_random_password(9)
        email = data.get('email')
        first_name = data.get('firstname')
        last_name = data.get('lastname')
        role = data.get("role")
        image = request.FILES.get('image')

        # AdditionalDetails fields (optional)
        state = data.get('state', None)
        district = data.get('district', None)
        pincode = data.get('pincode', None)
        phone = data.get('phone', None)
        bio = data.get('bio', None)

        try:
            # Create the Profile (User)
            user = Profile.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                password=password,
                email=email,
                role=role,
                username=email,
                image=image
            )
            user.password_str = password
            user.save()

            # Send the custom signal after password_str is set
            user_created.send(sender=self.__class__, instance=user)

            # Create AdditionalDetails if needed
            if True:
                AdditionalDetails.objects.create(
                    profile=user,
                    state=state,
                    district=district,
                    pincode=pincode,
                    phone=phone,
                    bio=bio
                )
                PersonalDetails.objects.create(profile=user)

            return Response({"msg": "User added successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
import logging
        
logger = logging.getLogger(__name__)

class UpdateProfileImageView(APIView):
    def patch(self, request, profile_id):  # Changed from user_id to profile_id
        try:
            image = request.FILES.get('image')
            
            if not image:
                return Response(
                    {"error": "No image provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if image.size > 2 * 1024 * 1024:
                return Response(
                    {"error": "Image size should be less than 2MB"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = Profile.objects.get(id=profile_id)  # Changed to use profile_id
            
            if user.image:
                user.image.delete(save=False)
            
            user.image = image
            user.save()
            
            return Response(
                {
                    "message": "Profile image updated successfully",
                    "image_url": user.image.url if user.image else None
                },
                status=status.HTTP_200_OK
            )
            
        except ObjectDoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating profile image: {str(e)}")
            return Response(
                {"error": "An error occurred while updating the profile image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ListUsersView(APIView):
    def get(self,request):
        role=request.GET.get("role")
        users_list=AdditionalDetails.objects.all()

        if role is not None:
            users_list = users_list.filter(profile__role=role)

        if not users_list:
            return Response({"msg":"users not found"},status=status.HTTP_400_BAD_REQUEST)
        serializer=AdditionalDetailsGetSerializer(users_list,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class DeleteUsersView(APIView):
    def delete(self,request):
        data=request.data
        profile_id=data.get("profile_id")
        if not profile_id:
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        users_list=get_object_or_404(Profile,id=profile_id)
        users_list.delete()
        return Response({'msg':'deletion succesfull'},status=status.HTTP_200_OK)
    
class AddPersonalDetailsApi(APIView):
    def post(self, request):
        # Create a mutable copy of request.data
        data = request.data.copy()

        profile_id = data.get("profile_id")

        # Validate that profile_id is provided
        if not profile_id:
            return Response({"msg": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the profile
            profile = Profile.objects.get(id=profile_id)

            # Check if PersonalDetails already exists for the profile
            if PersonalDetails.objects.filter(profile=profile).exists():
                return Response({"msg": "Personal details already exist for this profile"}, status=status.HTTP_400_BAD_REQUEST)

            # Add profile_id to the data for validation
            data['profile'] = profile.id

            # Validate and save the PersonalDetails
            serializer = PersonalDetailsSerializers(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Personal details added successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"msg": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"msg": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EditPersonalDetailsApi(APIView):
    def get(self, request, profile_id):
        try:
            # Fetch the profile
            profile = Profile.objects.get(id=profile_id)

            # Fetch the PersonalDetails record for the profile
            personal_details = PersonalDetails.objects.get(profile=profile)

            # Serialize the data
            serializer = PersonalDetailsSerializers(personal_details)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({"msg": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except PersonalDetails.DoesNotExist:
            return Response({"msg": "Personal details not found for this profile"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        # Create a mutable copy of request.data
        data = request.data.copy()

        profile_id = data.get("profile_id")

        # Validate that profile_id is provided
        if not profile_id:
            return Response({"msg": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the profile
            profile = Profile.objects.get(id=profile_id)

            # Fetch the PersonalDetails record for the profile
            personal_details = PersonalDetails.objects.get(profile=profile)

            # Validate and update the PersonalDetails
            serializer = PersonalDetailsSerializers(personal_details, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Personal details updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"msg": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except PersonalDetails.DoesNotExist:
            return Response({"msg": "Personal details not found for this profile"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
'''class AddAdditionalDetailsApi(APIView):
    def post(self, request):
        # Create a mutable copy of request.data
        data = request.data.copy()  # This makes the QueryDict mutable

        profile_id = data.get("profile_id")

        # Validate that profile_id is provided
        if not profile_id:
            return Response({"msg": "profile_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the profile
            profile = Profile.objects.get(id=profile_id)

            # Check if AdditionalDetails already exists for the profile
            if AdditionalDetails.objects.filter(profile=profile).exists():
                return Response({"msg": "Additional details already exist for this profile"}, status=status.HTTP_400_BAD_REQUEST)

            # Add profile_id to the data for validation
            data['profile'] = profile.id

            # Validate and save the AdditionalDetails
            serializer = AdditionalDetailsSerializers(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Additional details added successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"msg": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"msg": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)'''
        
class ChangeAddressApi(APIView):
    def get(self, request, profile_id):
        try:
            # Fetch the AdditionalDetails record for the profile
            additional_details = AdditionalDetails.objects.get(profile__id=profile_id)

            # Serialize the data
            serializer = AdditionalDetailsSerializers(additional_details)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AdditionalDetails.DoesNotExist:
            return Response({"msg": "Additional details not found for this profile"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, profile_id):
        try:
            # Fetch the AdditionalDetails record for the profile
            additional_details = AdditionalDetails.objects.get(profile__id=profile_id)

            # Validate and update the AdditionalDetails
            serializer = AdditionalDetailsSerializers(additional_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Additional details updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except AdditionalDetails.DoesNotExist:
            return Response({"msg": "Additional details not found for this profile"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangeUsernameApi(APIView):
    def post(self, request):
        data = request.data
        profile_id = data.get("profile_id")
        if not profile_id:
            return Response({"msg": "A profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the profile
        profile = get_object_or_404(Profile, id=profile_id)

        # Get the new username
        new_username = data.get("new_username")
        if not new_username:
            return Response({"msg": "A new username is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the new username already exists
        if Profile.objects.filter(username=new_username).exists():
            return Response({"msg": "This username is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the username
        profile.username = new_username
        profile.save()

        return Response({"msg": "Username updated successfully"}, status=status.HTTP_200_OK)

class ChangePasswordApi(APIView):
    def get(self, request):
        # Use request.GET to access query parameters
        profile_id = request.GET.get("profile_id")
        password = request.GET.get("password")
        new_password = request.GET.get("new_password")

        if not profile_id:
            return Response({"msg": "an id is required"}, status=status.HTTP_400_BAD_REQUEST)

        profile = get_object_or_404(Profile, id=profile_id)

        # Verify the current password
        if password == profile.password_str:
            profile.set_password(new_password)
            profile.password_str = new_password
            profile.save()
            return Response({"msg": "Password changed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "The passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
  

class ExternalUserRegistrationView(APIView):
    def post(self, request):
        data = request.data.copy()  #Create a mutable copy of request data
        email = data.get('email')

        # Check if email already exists
        if Profile.objects.filter(email=email).exists():
            return Response({"msg": "Email is already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Assign external user role manually
        data['role'] = 'external_license_viewer'
        data['is_approved'] = False  # External users must be approved
        data['password_str'] = make_password(data.get('password'))  # Hash password

        serializer = ProfileSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Registration successful. Awaiting admin approval."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"msg": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ApproveExternalUserView(APIView):
    permission_classes = [IsAdminUser]  #Ensures only admins can access

    def patch(self, request, user_id):
        user = get_object_or_404(Profile, id=user_id, role='external_license_viewer')

        if user.is_approved:
            return Response({"msg": "User is already approved."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_approved = True
        user.save()

        return Response({"msg": f"User {user.email} approved successfully."}, status=status.HTTP_200_OK)



class AddLicense(APIView):
    def post(self,request):
        fromdata=request.data
        serializer=LicenseDetailsSerializers(data=fromdata)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"added successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"failed to add","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

class LicenseListView(APIView):
    def get(self, request):
        application_type = request.GET.get("application_type", None)
        product_type = request.GET.get("product_type", None)
        class_of_device_type = request.GET.get("class_of_device_type", None)
        expiry_start_date = request.GET.get("expiry_start_date", None)
        expiry_end_date = request.GET.get("expiry_end_date", None)

        license_list = License.objects.all()

        if application_type:
            license_list = license_list.filter(application_type=application_type)
        if product_type:
            license_list = license_list.filter(product_type=product_type)
        if class_of_device_type:
            license_list = license_list.filter(class_of_device_type=class_of_device_type)
        if expiry_start_date and expiry_end_date:
            # Convert string dates to datetime objects
            start_date = datetime.strptime(expiry_start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(expiry_end_date, "%Y-%m-%d").date()
            # Filter licenses within the date range
            license_list = license_list.filter(expiry_date__range=[start_date, end_date])

        serializer = LicenseDetailsSerializers(license_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
from django.utils import timezone
class UpdateLicenseView(APIView):
    def patch(self,request):
        license_id= request.data.get('id')
        if not license_id: 
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        
        license_obj=get_object_or_404(License,id=license_id)
        serializer=LicenseDetailsSerializers(license_obj,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"edited successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"failed to edit","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        license_id=request.GET.get('id')
        if not license_id:
            return Response({"msg":"id is required"},status=status.HTTP_400_BAD_REQUEST)
        license_obj=get_object_or_404(License,id=license_id)
        serializer=LicenseDetailsSerializers(license_obj)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def delete(self,request):
        license_id=request.GET.get('id')
        if not license_id:
            return Response({"msg":"id is required"},status=status.HTTP_400_BAD_REQUEST)
        license_obj=get_object_or_404(License,id=license_id)
        license_obj.delete()
        return Response({'msg':'deleted succesfully'},status=status.HTTP_200_OK)
    

import logging
logger = logging.getLogger(__name__)


class SendNotificationView(APIView):
    def post(self, request):
        data = request.data
        sender_profile_id = data.get('profile')  # Sender's profile ID
        title = data.get('title')
        content = data.get('content')

        logger.info(f"Received request: {data}")

        if not sender_profile_id:
            return Response({"msg": "Profile ID is required"}, status=400)

        try:
            sender_profile = Profile.objects.get(id=sender_profile_id)
        except Profile.DoesNotExist:
            return Response({"msg": "Profile does not exist"}, status=404)

        if not title or not content:
            return Response({"msg": "Title and content are required"}, status=400)

        logger.info(f"Sender's role: {sender_profile.role}")

        # Determine recipients based on sender role
        if sender_profile.role == 'admin':
            recipients = Profile.objects.all()
        elif sender_profile.role == 'license_manager':
            recipients = Profile.objects.filter(role__in=['internal_license_viewer'])
        elif sender_profile.role == 'tender_manager':
            recipients = Profile.objects.filter(role='tender_viewer')
        elif sender_profile.role == 'pndt_license_manager':
            recipients = Profile.objects.filter(role='pndt_license_viewer')
        else:
            return Response({"msg": "Unauthorized to send notifications"}, status=403)

        logger.info(f"Recipients: {recipients}")

        notifications = []
        for recipient in recipients:
            try:
                notification = Notification.objects.create(
                    profile=recipient,
                    sender_profile=sender_profile,  # Ensure sender is saved
                    title=title,
                    content=content,
                    time=now()
                )
                logger.info(f"Notification created: {notification}")
                notifications.append({
                    "profile": recipient.id,
                    "sender_profile": sender_profile.id,  # Add sender profile in response
                    "title": notification.title,
                    "content": notification.content,
                    "time": notification.time
                })
            except Exception as e:
                logger.error(f"Failed to create notification for recipient {recipient.id}: {e}")

        return Response({
            "msg": "Notifications sent successfully",
            "notifications": notifications
        }, status=200)



class ViewNotificationView(APIView):
    def get(self, request):
        # Get profile_id and role from query parameters
        profile_id = request.query_params.get('profile_id')
        role = request.query_params.get('role')

        if not profile_id or not role:
            return Response({"msg": "profile_id and role are required"}, status=400)

        # Fetch notifications based on role and profile_id
        if role == "admin":
            # Admin can see all notifications
            notification_list = Notification.objects.all()
        elif role == "license_manager":
            # License manager can see notifications sent to them or sent by them to others
            notification_list = Notification.objects.filter(
                Q(profile_id=profile_id) | Q(sender_profile_id=profile_id)
            )
        elif role == "pndt_license_manager":
            # PNDT license manager can see notifications sent to them or sent by them to others
            notification_list = Notification.objects.filter(
                Q(profile_id=profile_id) | Q(sender_profile_id=profile_id)
            )
        elif role == "tender_manager":
            # Tender manager can see notifications sent to them or sent by them to others
            notification_list = Notification.objects.filter(
                Q(profile_id=profile_id) | Q(sender_profile_id=profile_id)
            )
        else:
            # For other roles, fetch notifications sent to the profile_id
            notification_list = Notification.objects.filter(profile_id=profile_id)

        # Serialize the notifications
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        print(serializer.data)
        return Response(serializer.data, status=200)


class UpdateNotificationView(APIView):
    def patch(self,request):
        data=request.data
        profile_id=data.get('id')
        if not profile_id: 
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        notification=get_object_or_404(Notification,id=profile_id)
        serializer=NotificationsDetailsSerializers(notification,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "editted successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"msg": "something went wrong",}, status=status.HTTP_400_BAD_REQUEST)
        

    def get(self,request):
        data=request.data
        profile_id=data.get('id')
        if not profile_id: 
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        notification=get_object_or_404(Notification,id=profile_id)
        serializer=NotificationsDetailsSerializers(notification)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request):
        data=request.data
        profile_id=data.get('id')
        if not profile_id: 
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        notification=get_object_or_404(Notification,id=profile_id)
        notification.delete()
        return Response({'msg':'deleted succesfully'},status=status.HTTP_200_OK)


class TenderViewerNotificationView(APIView):
    def get(self, request):
        role = request.GET.get("role")
        
        notification_list = Notification.objects.filter(profile__role=role)
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=200)


class PNDTLicenseViewerNotificationView(APIView):
    def get(self, request):
        role = request.GET.get("role")
        
        notification_list = Notification.objects.filter(profile__role=role)
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=200)


class LicenseViewerNotificationView(APIView):
    def get(self, request):
        role = request.GET.get("role")
        
        notification_list = Notification.objects.filter(profile__role=role)
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=200)


class ExternalLicenseViewerNotificationView(APIView):
    def get(self, request):
        role = request.GET.get("role")
        
        notification_list = Notification.objects.filter(profile__role=role, sender_profile__role="admin")
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=200)



class FeedbackView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddTenderDetailsView(APIView):
    def post(self,request):
        data=request.data
        serializer=TenderDetailsSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"added successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"failed to add","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
class ChangeForfietStatusView(APIView):
    def post(self,request):
        tender_id=request.data.get("tender_id")
        if not tender_id:
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        tender_obj=get_object_or_404(Tenders,id=tender_id)
        forfeiture_reason=request.data.get("forfeiture_reason")
        if not forfeiture_reason:
            return Response({"msg":"A reason is required"},status=status.HTTP_400_BAD_REQUEST)
            
        tender_obj.forfeiture_reason=forfeiture_reason
        tender_obj.save()

        return Response({"msg":"forefiet status is true","forfeiture_reason":tender_obj.forfeiture_reason},status=status.HTTP_200_OK)
        

class AddPNDTLicenseView(APIView):
    def post(self,request):
        data=request.data
        serializer=PNDTLicenseSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"added successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"failed to add","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
class ListPNDTLicenseView(APIView):
    def get(self,request):
        product_type=request.GET.get("product_type")
        intended_use=request.GET.get("intended_use")
        class_of_device=request.GET.get("class_of_device")
        PNDTlicense_list=PNDT_License.objects.all()

        if product_type:
            PNDTlicense_list=PNDTlicense_list.filter(product_type=product_type)
        if intended_use:
            PNDTlicense_list=PNDTlicense_list.filter(intended_use=intended_use)
        if class_of_device:
            PNDTlicense_list=PNDTlicense_list.filter(class_of_device=class_of_device)
        serializer=PNDTLicenseSerializers(PNDTlicense_list,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    


class UpdatePNDTLicenseView(APIView):
    def patch(self,request):
        license_number= request.data.get('license_number')
        if not license_number: 
            return Response({"msg":"An id is required"},status=status.HTTP_400_BAD_REQUEST)
        
        license_obj=get_object_or_404(PNDT_License,license_number=license_number)
        serializer=PNDTLicenseSerializers(license_obj,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"edited successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"failed to edit","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        license_number=request.GET.get('license_number')
        if not license_number:
            return Response({"msg":"id is required"},status=status.HTTP_400_BAD_REQUEST)
        license_obj=get_object_or_404(PNDT_License,license_number=license_number)
        serializer=PNDTLicenseSerializers(license_obj)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def delete(self,request):
        license_number=request.GET.get('license_number')
        if not license_number:
            return Response({"msg":"id is required"},status=status.HTTP_400_BAD_REQUEST)
        license_obj=get_object_or_404(PNDT_License,license_number=license_number)
        license_obj.delete()
        return Response({'msg':'deleted succesfully'},status=status.HTTP_200_OK)
    



class ExpireNotification(APIView):
    def get(self, request):
        today = datetime.today().date()
        notifications = []

        licenses = License.objects.all()
        for licen in licenses:
            if licen.expiry_date:
                days_left = (licen.expiry_date - today).days
                if days_left in [10, 5, 1]:  
                    notifications.append({
                        "license_id": licen.id,
                        "license_name": licen.name,
                        "expiry_date": licen.expiry_date,
                        "days_left": days_left,
                        "message": f"Your license '{licen.name}' is expiring in {days_left} days!",
                    })

        if notifications:
            return Response({"notifications": notifications}, status=status.HTTP_200_OK)
        return Response({"msg": "No licenses are expiring soon."}, status=status.HTTP_200_OK)


from .reports import report_as_excel

class DownloadTenderExcelReport(APIView):
    def get(self, request):
        file_name = "TENDER_REPORT"
        title = "Tender Report"

        headers = [
            ("S.No", 10),
            ("Tender ID", 20),
            ("Tender Title", 30),
            ("Issuing Authority", 30),
            ("Tender Description", 40),
            ("EMD Amount", 15),
            ("Payment Mode", 15),
            ("EMD Payment Date", 15),
            ("Tender Status", 15),
            ("Bid Outcome", 15),
            ("Forfeiture Status", 15),
            ("Forfeiture Reason", 30),
        ]

        tenders = Tenders.objects.all()
        data = [
            [
                index,
                tender.tender_id,
                tender.tender_title,
                tender.issuing_authority,
                tender.tender_description,
                tender.EMD_amount,
                tender.EMD_payment_mode if tender.EMD_payment_mode else "N/A",
                tender.EMD_payment_date.strftime('%Y-%m-%d') if tender.EMD_payment_date else "N/A",
                tender.tender_status,
                tender.bid_outcome,
                "Yes" if tender.forfeiture_status else "No",
                tender.forfeiture_reason if tender.forfeiture_reason else "N/A",
            ]
            for index, tender in enumerate(tenders, start=1)
        ]

        return report_as_excel(title, headers, data, file_name)

    

class TenderStatusView(APIView):
    def get(self, request):
        status_filter = request.GET.get("status")

        tenders = Tenders.objects.all()
        completed_tenders = []
        rejected_tenders = []
        pending_tenders = []

        for tender in tenders:
            if tender.EMD_refund_status:
                tender_status = "Completed"
                completed_tenders.append({
                    "tender_id": tender.tender_id,
                    "tender_title": tender.tender_title,
                    "issuing_authority": tender.issuing_authority,
                    "EMD_amount": tender.EMD_amount,
                    "EMD_refund_date": tender.EMD_refund_date,
                    "tender_status": tender_status
                })
            elif not tender.EMD_refund_status and not tender.forfeiture_status:
                tender_status = "Rejected"
                rejected_tenders.append({
                    "tender_id": tender.tender_id,
                    "tender_title": tender.tender_title,
                    "issuing_authority": tender.issuing_authority,
                    "EMD_amount": tender.EMD_amount,
                    "EMD_refund_date": tender.EMD_refund_date,
                    "tender_status": tender_status
                })
            else:
                tender_status = "Pending"
                pending_tenders.append({
                    "tender_id": tender.tender_id,
                    "tender_title": tender.tender_title,
                    "issuing_authority": tender.issuing_authority,
                    "EMD_amount": tender.EMD_amount,
                    "EMD_refund_date": tender.EMD_refund_date,
                    "tender_status": tender_status
                })

        if status_filter == "completed":
            return Response({"tenders": completed_tenders}, status=status.HTTP_200_OK)
        elif status_filter == "rejected":
            return Response({"tenders": rejected_tenders}, status=status.HTTP_200_OK)
        elif status_filter == "pending":
            return Response({"tenders": pending_tenders}, status=status.HTTP_200_OK)
        else:
            return Response({
                "completed_count": len(completed_tenders),
                "rejected_count": len(rejected_tenders),
                "pending_count": len(pending_tenders)
            }, status=status.HTTP_200_OK) 


from .tasks import check_expiring_licenses


check_expiring_licenses(schedule=1)

# API to request OTP for password reset
class RequestOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            # Fetch the user by email
            user = Profile.objects.get(email=email)
            # Generate a 6-digit OTP
            otp = str(random.randint(100000, 999999))
            # Create an OTP entry for the user
            OTPVerification.objects.create(user=user, otp=otp)

            # Send the OTP via email
            send_mail(
                "Password Reset OTP",
                f"Your OTP is: {otp}",
                "meddocx@gmail.com",  # Replace with your email
                [email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({"error": "User with this email not found"}, status=status.HTTP_404_NOT_FOUND)

# API to verify OTP and reset password
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        try:
            # Fetch the user by email
            user = Profile.objects.get(email=email)
            # Fetch the OTP entry for the user
            otp_entry = OTPVerification.objects.filter(user=user, otp=otp).first()

            # Check if the OTP entry exists and is valid
            if otp_entry and otp_entry.is_valid():
                # Set the new password for the user
                user.set_password(new_password)
                # Update the password_str field with the new password (plain text or hashed)
                user.password_str = new_password  # Or use make_password(new_password) for hashing
                user.save()
                # Delete the OTP entry after successful verification
                otp_entry.delete()
                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            else:
                # If OTP is invalid or expired, return an error
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            # If the user does not exist, return an error
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class ListTenderView(APIView):
    def get(self,request):
        EMD_payment_status=request.GET.get("EMD_payment_status")
        forfeiture_status=request.GET.get("forfeiture_status")
        EMD_refund_status=request.GET.get("EMD_refund_status")
        ListTenderView=Tenders.objects.all()

        if EMD_payment_status:
            ListTenderView=ListTenderView.filter(EMD_payment_status=EMD_payment_status)
        if EMD_payment_status:
            ListTenderView=ListTenderView.filter(forfeiture_status=forfeiture_status)
        if EMD_refund_status:
            ListTenderView=ListTenderView.filter(EMD_refund_status=EMD_refund_status)
        serializer=TenderDetailsSerializers(ListTenderView,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class UpdateTenderView(APIView):
    def patch(self, request):
        tender_id = request.data.get('tender_id') 
        if not tender_id:
            return Response({"msg": "A tender_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        tender_obj = get_object_or_404(Tenders, tender_id=tender_id)
        
        serializer = TenderDetailsSerializers(tender_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Tender updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "Failed to update", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        tender_id = request.GET.get('tender_id')
        if not tender_id:
            return Response({"msg": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        tender_obj = Tenders.objects.filter(tender_id=tender_id).first()
        if not tender_obj:
            return Response({"msg": "Tender not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TenderDetailsSerializers(tender_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        tender_id = request.GET.get('tender_id')
        if not tender_id:
            return Response({"msg": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        tender_obj = Tenders.objects.filter(tender_id=tender_id).first()
        if not tender_obj:
            return Response({"msg": "Tender not found"}, status=status.HTTP_404_NOT_FOUND)
        
        tender_obj.delete()
        return Response({"msg": "Deleted successfully"}, status=status.HTTP_200_OK)



class TotalEMDAmountView(View):
    def get(self, request, *args, **kwargs):
        # Calculate the total EMD amount
        total_emd = Tenders.objects.aggregate(total_emd_amount=Sum('EMD_amount'))['total_emd_amount'] or 0

        # Calculate the total pending EMD amount
        total_pending_emd = Tenders.objects.filter(EMD_refund_status=False).aggregate(total_pending_emd_amount=Sum('EMD_amount'))['total_pending_emd_amount'] or 0

        # Calculate the total number of tenders
        total_tenders = Tenders.objects.count()

        # Prepare the response data
        response_data = {
            'total_emd_amount': total_emd,
            'total_pending_emd_amount': total_pending_emd,
            'total_tenders': total_tenders,
        }

        # Return the response as JSON
        return JsonResponse(response_data)
    
class CountUsersView(APIView):
    def get(self, request):
        user_count = Profile.objects.exclude(role='admin').count()
        total_licenses = License.objects.count()
        total_pndt_licenses = PNDT_License.objects.count()
        total_tenders = Tenders.objects.count()
        
        return Response({
            "total_users": user_count,
            "total_licenses": total_licenses,
            "total_pndt_licenses": total_pndt_licenses,
            "total_tenders": total_tenders
        }, status=status.HTTP_200_OK)


class RecentlyAddedView(APIView):
    def get(self, request):
        filter_type = request.query_params.get('filter', 'all')
        
        now = timezone.now()
        
        if filter_type == 'this_week':
            start_date = now - timedelta(days=now.weekday())
            recent_licenses = License.objects.filter(date_of_submission__gte=start_date).order_by('-date_of_submission')[:5]
            recent_pndt_licenses = PNDT_License.objects.filter(submission_date__gte=start_date).order_by('-submission_date')[:5]
        elif filter_type == 'this_month':
            start_date = now.replace(day=1)
            recent_licenses = License.objects.filter(date_of_submission__gte=start_date).order_by('-date_of_submission')[:5]
            recent_pndt_licenses = PNDT_License.objects.filter(submission_date__gte=start_date).order_by('-submission_date')[:5]
        elif filter_type == 'this_year':
            start_date = now.replace(month=1, day=1)
            recent_licenses = License.objects.filter(date_of_submission__gte=start_date).order_by('-date_of_submission')[:5]
            recent_pndt_licenses = PNDT_License.objects.filter(submission_date__gte=start_date).order_by('-submission_date')[:5]
        elif filter_type == 'last_year':
            start_date = now.replace(year=now.year - 1, month=1, day=1)
            end_date = now.replace(year=now.year - 1, month=12, day=31)
            recent_licenses = License.objects.filter(date_of_submission__gte=start_date, date_of_submission__lte=end_date).order_by('-date_of_submission')[:5]
            recent_pndt_licenses = PNDT_License.objects.filter(submission_date__gte=start_date, submission_date__lte=end_date).order_by('-submission_date')[:5]
        else:
            recent_licenses = License.objects.order_by('-date_of_submission')[:5]
            recent_pndt_licenses = PNDT_License.objects.order_by('-submission_date')[:5]
        
        # Include product_name in the response
        return Response({
            "recent_licenses": [
                {"application_number": license.application_number, "product_name": license.product_name}
                for license in recent_licenses
            ],
            "recent_pndt_licenses": [
                {"application_number": pndt_license.application_number, "product_name": pndt_license.product_name}
                for pndt_license in recent_pndt_licenses
            ]
        }, status=status.HTTP_200_OK)

class RecentlyViewedView(APIView):
    def get(self, request):
        recently_viewed_licenses = License.objects.order_by('-viewed_date')[:5]
        recently_viewed_pndt_licenses = PNDT_License.objects.order_by('-submission_date')[:5]
        
        # Include product_name in the response
        return Response({
            "recently_viewed_licenses": [
                {"application_number": license.application_number, "product_name": license.product_name}
                for license in recently_viewed_licenses
            ],
            "recently_viewed_pndt_licenses": [
                {"application_number": pndt_license.application_number, "product_name": pndt_license.product_name}
                for pndt_license in recently_viewed_pndt_licenses
            ]
        }, status=status.HTTP_200_OK)


from django.utils.timezone import now
from datetime import timedelta
from .models import License

class LicenseStatisticsView(APIView):
    def get(self, request):
        today = now().date()
        
        total_licenses = License.objects.count()
        expiring_soon = License.objects.filter(expiry_date__range=[today + timedelta(days=1), today + timedelta(days=30)]).count()
        expired_licenses = License.objects.filter(expiry_date__lte=today).count()
        active_licenses = License.objects.filter(expiry_date__gt=today).count()
        
        return Response({
            "total_licenses": total_licenses,
            "expiring_soon": expiring_soon,
            "expired_licenses": expired_licenses,
            "active_licenses": active_licenses
        }, status=status.HTTP_200_OK)
    

class PNDT_LicenseStatisticsView(APIView):
    def get(self, request):
        today = now().date()
        total_licenses = PNDT_License.objects.count()
        expiring_soon = PNDT_License.objects.filter(expiry_date__range=[today + timedelta(days=1), today + timedelta(days=30)]).count()
        expired_licenses = PNDT_License.objects.filter(expiry_date__lte=today).count()
        active_licenses = PNDT_License.objects.filter(expiry_date__gt=today).count()
        return Response({
            "total_licenses": total_licenses,
            "expiring_soon": expiring_soon,
            "expired_licenses": expired_licenses,
            "active_licenses": active_licenses
        }, status=status.HTTP_200_OK)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tenders

class TenderCountAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Count tenders with status 'applied'
        applied_count = Tenders.objects.filter(tender_status='applied').count()

        # Count tenders with status 'completed' and bid outcome 'won'
        completed_won_count = Tenders.objects.filter(tender_status='completed', bid_outcome='won').count()

        # Count tenders with status 'completed' and bid outcome 'lost'
        rejected_count = Tenders.objects.filter(tender_status='completed', bid_outcome='lost').count()

        # Count tenders with status 'completed' and EMD refund status False
        emd_pending_count = Tenders.objects.filter(tender_status='completed', EMD_refund_status=False).count()

        # Return the counts in a response
        return Response({
            'applied': applied_count,
            'completed_won': completed_won_count,
            'rejected': rejected_count,
            'emd_pending': emd_pending_count,
        }, status=status.HTTP_200_OK)
    



from rest_framework import generics
from .models import Tenders
from .serializers import TenderManagerSerializer

class AppliedTenderList(generics.ListAPIView):
    serializer_class = TenderManagerSerializer

    def get_queryset(self):
        return Tenders.objects.filter(tender_status='applied')  

class AwardedTenderList(generics.ListAPIView):
    serializer_class = TenderManagerSerializer

    def get_queryset(self):
        return Tenders.objects.filter(tender_status='completed', bid_outcome='won')
    
class TendersnotawardedList(generics.ListAPIView):
    serializer_class = TenderManagerSerializer

    def get_queryset(self):
        return Tenders.objects.filter(tender_status='completed', bid_outcome='lost')
    
class CompletedTendersWithoutEMDRefundList(generics.ListAPIView):
    serializer_class = TenderManagerSerializer

    def get_queryset(self):
        # Filter tenders where tender_status is 'completed' and EMD_refund_status is False
        return Tenders.objects.filter(tender_status='completed', EMD_refund_status=False)
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tenders
from .serializers import TenderManagerSerializer

class Top5pendingemd(APIView):
    def get(self, request):
        # Filter tenders with status 'completed' and EMD refund status 'False'
        tenders_refund_pending = Tenders.objects.filter(tender_status='completed', EMD_refund_status=False)
        
        # Filter all tenders with status 'completed' (regardless of refund status)
        tenders_completed = Tenders.objects.filter(tender_status='completed')
        
        # Calculate the total EMD amount to be refunded (for refund pending tenders)
        total_emd_refund_pending = 0
        for tender in tenders_refund_pending:
            try:
                # Convert EMD_amount to float and add to total
                total_emd_refund_pending += float(tender.EMD_amount)
            except (ValueError, TypeError):
                # Skip if EMD_amount is not a valid number
                continue
        
        # Calculate the total EMD amount for all completed tenders (regardless of refund status)
        total_emd_completed = 0
        for tender in tenders_completed:
            try:
                # Convert EMD_amount to float and add to total
                total_emd_completed += float(tender.EMD_amount)
            except (ValueError, TypeError):
                # Skip if EMD_amount is not a valid number
                continue
        
        # Get the top 5 tenders with the highest EMD refund pending
        # Sort by EMD_amount in descending order and take the first 5
        top_5_tenders = sorted(
            tenders_refund_pending,
            key=lambda x: float(x.EMD_amount) if x.EMD_amount and x.EMD_amount.replace('.', '', 1).isdigit() else 0,
            reverse=True
        )[:5]
        
        # Serialize the top 5 tenders
        serializer = TenderManagerSerializer(top_5_tenders, many=True)
        
        # Prepare the response data
        response_data = {
            'total_emd_refund_pending': total_emd_refund_pending,  # Total EMD to be refunded
            'total_emd_completed': total_emd_completed,  # Total EMD for all completed tenders
            'top_5_tenders': serializer.data  # Top 5 tenders with highest refund pending
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    

    from django.views import View
from django.http import JsonResponse
from django.db.models import Sum
from .models import Tenders

class TotalEMDAmountView(View):
    def get(self, request, *args, **kwargs):
        # Calculate the total EMD amount for tenders with status 'completed'
        total_emd = Tenders.objects.filter(tender_status='completed').aggregate(total_emd_amount=Sum('EMD_amount'))['total_emd_amount'] or 0

        # Calculate the total pending EMD amount for tenders with status 'completed' and EMD_refund_status False
        total_pending_emd = Tenders.objects.filter(tender_status='completed', EMD_refund_status=False).aggregate(total_pending_emd_amount=Sum('EMD_amount'))['total_pending_emd_amount'] or 0

        # Calculate the total number of tenders with status 'completed' and EMD_refund_status False
        total_pending_emd_count = Tenders.objects.filter(tender_status='completed', EMD_refund_status=False).count()

        # Prepare the response data
        response_data = {
            'total_emd_amount': total_emd,
            'total_pending_emd_amount': total_pending_emd,
            'total_pending_emd_count': total_pending_emd_count,
        }

        # Return the response as JSON
        return JsonResponse(response_data)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tenders
from .serializers import TenderDetailsSerializers

class ListTenderView(APIView):
    def get(self, request):
        # Get query parameters
        EMD_payment_status = request.GET.get("EMD_payment_status")
        forfeiture_status = request.GET.get("forfeiture_status")
        EMD_refund_status = request.GET.get("EMD_refund_status")

        # Start with all tenders
        ListTenderView = Tenders.objects.all()

        # Apply filters based on query parameters
        if EMD_payment_status:
            ListTenderView = ListTenderView.filter(EMD_payment_status=EMD_payment_status)
        if forfeiture_status:
            ListTenderView = ListTenderView.filter(forfeiture_status=forfeiture_status)
        if EMD_refund_status:
            ListTenderView = ListTenderView.filter(EMD_refund_status=EMD_refund_status)

        # Calculate the total count of filtered tenders
        total_tender_count = ListTenderView.count()

        # Serialize the filtered queryset
        serializer = TenderDetailsSerializers(ListTenderView, many=True)

        # Prepare the response data
        response_data = {
            'total_tender_count': total_tender_count,  # Add total count to the response
            'tenders': serializer.data,  # Include serialized tender data
        }

        # Return the response
        return Response(response_data, status=status.HTTP_200_OK)
    

class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]  # Restrict access to admins only

    def get(self, request):
        current_date = now().date()

        # **Total Counts**
        total_users = Profile.objects.exclude(role='admin').count()  # Exclude admin users
        total_licenses = License.objects.count()
        total_tenders = Tenders.objects.count()
        total_pndt_licenses = PNDT_License.objects.count()

        # **Active Counts**
        active_licenses = License.objects.filter(expiry_date__gte=current_date).count()
        active_tenders = Tenders.objects.exclude(tender_status='completed').count()
        active_pndt_licenses = PNDT_License.objects.filter(expiry_date__gte=current_date).count()

        return Response({
            "total_users": total_users,
            "total_licenses": total_licenses,
            "total_tenders": total_tenders,
            "total_pndt_licenses": total_pndt_licenses,
            "active_licenses": active_licenses,
            "active_tenders": active_tenders,
            "active_pndt_licenses": active_pndt_licenses
        }, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import License

def format_license_data(licenses):
    """
    Formats license data into a list of dictionaries with only the required fields.
    """
    return [
        {
            "product_name": licen.product_name,
            "license_number": licen.license_number,
            "expiry_date": licen.expiry_date,
            "date_of_approval": licen.date_of_approval,
        }
        for licen in licenses
    ]

class LicenseExpiryAndActiveByDate(APIView):
    def post(self, request):
        try:
            # Fetch all licenses from the database
            all_licenses = License.objects.all()

            # Format the data with only the required fields
            formatted_licenses = format_license_data(all_licenses)

            return Response(
                {
                    "licenses": formatted_licenses if formatted_licenses else "No licenses found.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while fetching data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

#PNDT license calender API
def format_pndt_license_data(pndt_licenses):
    """
    Formats PNDT license data into a list of dictionaries with only the required fields.
    """
    return [
        {
            "license_number": pndt.license_number,
            "expiry_date": pndt.expiry_date,
            "approval_date": pndt.approval_date,
            "product_name": pndt.product_name,
        }
        for pndt in pndt_licenses
    ]

class PNDTLicenseCalenderList(APIView):
    def post(self, request):
        try:
            # Fetch all PNDT licenses from the database
            all_pndt_licenses = PNDT_License.objects.all()

            # Format the data with only the required fields
            formatted_pndt_licenses = format_pndt_license_data(all_pndt_licenses)

            return Response(
                {
                    "pndt_licenses": formatted_pndt_licenses if formatted_pndt_licenses else "No PNDT licenses found.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while fetching data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def format_tender_data(tenders):
    """
    Formats tender data into a list of dictionaries with only the required fields.
    """
    return [
        {
            "tender_id": tender.tender_id,
            "emd_payment_date": tender.EMD_payment_date,  # EMD payment date
            "emd_refund_date": tender.EMD_refund_date,      # EMD refund date
            "tender_name": tender.tender_title,             # Tender name (title)
        }
        for tender in tenders
    ]

class TenderCalender(APIView):
    def post(self, request):
        try:
            # Fetch all tenders from the database
            all_tenders = Tenders.objects.all()

            # Format the data with only the required fields
            formatted_tenders = format_tender_data(all_tenders)

            return Response(
                {
                    "tenders": formatted_tenders if formatted_tenders else "No tenders found.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while fetching data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )