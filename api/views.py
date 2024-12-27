from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegistrationSerializers
from .models import Registration
from django.shortcuts import get_object_or_404
from .models import Profile,License,AdditionalDetails,Notification
from .serializers import AdditionalDetailsSerializers,LicenseDetailsSerializers,AdditionalDetailsGetSerializer,NotificationsDetailsSerializers



import random
import string

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
    def post(self,request):
        data=request.data
        password=generate_random_password(9)
        email=data.get('email')
        first_name=data.get('firstname')
        last_name=data.get('lastname')
        role=data.get("role")
        try:
            user = Profile.objects.create_user(first_name=first_name,last_name=last_name,password=password,email=email,role=role,username=email)
            user.password_str=password
            user.save()
            return Response({"msg": "user added successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"msg": "something went wrong","error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class ListUsersView(APIView):
    def get(self,request):
        role=request.GET.get("role")
        users_list=AdditionalDetails.objects.all()

        if role is not None:
            users_list = users_list.filter(profile__role=role)

        if not users_list:
            return Response({"msg":"no users found"},status=status.HTTP_400_BAD_REQUEST)
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
        return Response({'msg':'deleted succesfully'},status=status.HTTP_200_OK)
        
        
class ChangeAddressApi(APIView):
    def patch(self,request):
        data=request.data
        profile_id=data.get("profile_id")
        additionaldetails=get_object_or_404(AdditionalDetails,profile__id=profile_id)
        serializer=AdditionalDetailsSerializers(additionaldetails,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "editted successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"msg": "something went wrong",}, status=status.HTTP_400_BAD_REQUEST)

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
    def get(self,request):
        application_type=request.GET.get("application_type",None)
        product_type=request.GET.get("product_type")
        product_name=request.GET.get("product_name")
        class_of_device_type=request.GET.get("class_of_device_type")
        license_list=License.objects.all()

        if application_type:
            license_list=license_list.filter(application_type=application_type)
        if product_type:
            license_list=license_list.filter(product_type=product_type)
        if product_name:
            license_list=license_list.filter(product_name=product_name)
        if class_of_device_type:
            license_list=license_list.filter(class_of_device_type=class_of_device_type)
        serializer=LicenseDetailsSerializers(license_list,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

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


        

