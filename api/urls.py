from django.urls import path
from . import views
urlpatterns = [
    path('addusers/',views.AdminAddUsersApi.as_view()),
    path('addpersonaldetails/',views.AddPersonalDetailsApi.as_view()), #for testing only no need to connect
    path('editpersonaldetails/<int:profile_id>/', views.EditPersonalDetailsApi.as_view(), name='editpersonaldetails-get'),
    path('editpersonaldetails/', views.EditPersonalDetailsApi.as_view(), name='editpersonaldetails-patch'),
    path('changeaccountaddress/<int:profile_id>/', views.ChangeAddressApi.as_view(), name='changeaccountaddress'),
    path('license/',views.AddLicense.as_view()),
    path('list/',views.LicenseListView.as_view()),
    path('edit/',views.UpdateLicenseView.as_view()),
    path('editpassword/',views.ChangePasswordApi.as_view()),
    path('listusers/',views.ListUsersView.as_view()),
    path('deleteusers/',views.DeleteUsersView.as_view()),
    path('sendnotification/',views.SendNotificationView.as_view()),
    path('viewnotification/',views.ViewNotificationView.as_view()),
    path('updatenotification/',views.UpdateNotificationView.as_view()),
    path('addtenderdetails/',views.AddTenderDetailsView.as_view()),
    path('changestatus/',views.ChangeForfietStatusView.as_view()),
    path('addpndtlicense/',views.AddPNDTLicenseView.as_view()),
    path('listpndtlicense/',views.ListPNDTLicenseView.as_view()),
    path('updatepndtlicense/',views.UpdatePNDTLicenseView.as_view()),
    path('expire_notification/',views.ExpireNotification.as_view()),
    
    path('login/',views.LoginAPIView.as_view())  ,
    path('download_license_excel/',views.DownloadExcelReport.as_view()) , 

    path('tendernotifications/', views.TenderViewerNotificationView.as_view()),
    path('pndtnotifications/', views.PNDTLicenseViewerNotificationView.as_view()),
    path('licensenotifications/', views.LicenseViewerNotificationView.as_view()),
    path('tenderstatus/', views.TenderStatusView.as_view()),

]