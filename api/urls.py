from django.urls import path
from . import views
urlpatterns = [
    path('addusers/',views.AdminAddUsersApi.as_view()),
    path('changeaccountaddress/',views.ChangeAddressApi.as_view()),
    path('license/',views.AddLicense.as_view()),
    path('list/',views.LicenseListView.as_view()),
    path('edit/',views.UpdateLicenseView.as_view()),
    path('editpassword/',views.ChangePasswordApi.as_view()),
    path('listusers/',views.ListUsersView.as_view()),
    path('deleteusers/',views.DeleteUsersView.as_view()),
    path('sendnotification/',views.SendNotificationView.as_view()),
    path('viewnotification/',views.ViewNotificationView.as_view()),
    path('updatenotification/',views.UpdateNotificationView.as_view())

           
]