from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegistrationSerializers
from .models import Registration
from django.shortcuts import get_object_or_404
from .models import Profile,License,AdditionalDetails,Notification,TenderManager,PNDT_License,PersonalDetails
from .serializers import AdditionalDetailsSerializers,LicenseDetailsSerializers,AdditionalDetailsGetSerializer,NotificationsDetailsSerializers,PersonalDetailsSerializers
from .serializers import TenderDetailsSerializers
from .serializers import PNDTLicenseSerializers
from datetime import datetime, timedelta
from .models import PlayerId
from datetime import datetime

import random
import string

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

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
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful',
                'user':user.id,
                'role':user.role
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
                username=email
            )
            user.password_str = password
            user.save()

            # Check if any AdditionalDetails fields are provided
            if any([state, district, pincode, phone, bio]):
                # Create the AdditionalDetails record linked to the Profile
                AdditionalDetails.objects.create(
                    profile=user,
                    state=state,
                    district=district,
                    pincode=pincode,
                    phone=phone,
                    bio=bio
                )

            return Response({"msg": "User added successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"msg": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


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
    def patch(self, request):
        data = request.data
        profile_id = data.get("profile_id")
        additionaldetails = get_object_or_404(AdditionalDetails, profile__id=profile_id)
        serializer = AdditionalDetailsSerializers(additionaldetails, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Edited successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        
class ChangePasswordApi(APIView):
    def get(self,request):
        data=request.data
        profile_id=data.get("profile_id")
        if not profile_id:
            return Response({"msg":"an id is required"},status=status.HTTP_400_BAD_REQUEST)
        profile=get_object_or_404(Profile,id=profile_id)
        password=data.get("password")
        password2=profile.password_str
        print(password)
        if password==password2:
            new_password=data.get("new_password")
            profile.set_password(new_password)
            profile.password_str=new_password
            profile.save()
            return Response({"msg": "editted successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"msg":"the passwords do not match"},status=status.HTTP_400_BAD_REQUEST)
        

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
    

class SendNotificationView(APIView):
    def post(self,request):
        data=request.data
        serializer=NotificationsDetailsSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"added successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"failed to add","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class ViewNotificationView(APIView):
    def get(self,request):
        role=request.GET.get("role")
        notification_list=Notification.objects.all()
        if role:
            notification_list = notification_list.filter(profile__role=role)
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        tender_obj=get_object_or_404(TenderManager,id=tender_id)
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
class DownloadExcelReport(APIView):
    def get(self, request):
        file_name = "LICENSE_REPORT"
        title = "License Report"

        headers = [
            ("S.No", 10),
            ("Application Type", 25),
            ("License Number", 20),
            ("Date of Approval", 15),
            ("Expiry Date", 15),
            ("Product Name", 30),
            ("Model Number", 20),
            ("Class of Device", 20),
        ]

        licenses = License.objects.all()
        data = [
            [
                index,
                lic.application_type,
                lic.license_number,
                lic.date_of_approval.strftime('%Y-%m-%d'),
                lic.expiry_date.strftime('%Y-%m-%d'),
                lic.product_name,
                lic.model_number,
                lic.class_of_device_type,
            ]
            for index, lic in enumerate(licenses, start=1)
        ]

        return report_as_excel(title, headers, data, file_name)
    


class TenderViewerNotificationView(APIView):
    def get(self,request):
        role=request.GET.get("role")
        notification_list = Notification.objects.filter(profile__role__in=['tender_manager','admin'])
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PNDTLicenseViewerNotificationView(APIView):
    def get(self,request):
        role=request.GET.get("role")
        notification_list = Notification.objects.filter(profile__role__in=['pndt_license_manager','admin'])
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LicenseViewerNotificationView(APIView):
    def get(self,request):
        role=request.GET.get("role")
        notification_list = Notification.objects.filter(profile__role__in=['license_manager','admin'])
        serializer = NotificationsDetailsSerializers(notification_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TenderStatusView(APIView):
    def get(self, request):
        status_filter = request.GET.get("status")

        tenders = TenderManager.objects.all()
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
                    "bid_amount": tender.bid_amount,
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
                    "bid_amount": tender.bid_amount,
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
                    "bid_amount": tender.bid_amount,
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
