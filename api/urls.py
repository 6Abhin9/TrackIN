from django.urls import path
from . import views
from .views import AppliedTenderList, FeedbackView, RequestOTPView, UpdateProfileImageView, VerifyOTPView, PNDT_LicenseStatisticsView
from .views import TenderCountAPIView, CompletedTendersWithoutEMDRefundList, AwardedTenderList, TendersnotawardedList, Top5pendingemd, ChangeUsernameApi 
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
    path('download_license_excel/',views.DownloadTenderExcelReport.as_view()) , 

    path('tendernotifications/', views.TenderViewerNotificationView.as_view()),
    path('pndtnotifications/', views.PNDTLicenseViewerNotificationView.as_view()),
    path('licensenotifications/', views.LicenseViewerNotificationView.as_view()),
    path('tenderstatus/', views.TenderStatusView.as_view()),
    path('tenderlist/', views.ListTenderView.as_view()),
    path('updatetender/',views.UpdateTenderView.as_view()),

    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('totalemdamount/', views.TotalEMDAmountView.as_view(), name='totalemdamount'),
    path('countusers/',views.CountUsersView.as_view()),
    path('recentlyadded/', views.RecentlyAddedView.as_view()),
    path('recentlyviewed/', views.RecentlyViewedView.as_view()),
    path('licenseoverview/', views.LicenseStatisticsView.as_view()),

    path('register-external-user/', views.ExternalUserRegistrationView.as_view(), name='register-external-user'),
    path('approve-external-user/<int:profile_id>/', views.ApproveExternalUserView.as_view(), name='approve-external-user'),
    path('pndtoverview/', views.PNDT_LicenseStatisticsView.as_view()),
    path('tenderoverview/', views.TenderCountAPIView.as_view()),
    path('emd_refund_pending/', views.CompletedTendersWithoutEMDRefundList.as_view()),
    path('awardedtenders/', AwardedTenderList.as_view()),
    path('tendernotawardedlist/', TendersnotawardedList.as_view()),
    path('appliedtenders/', AppliedTenderList.as_view()),
    path('change-username/', ChangeUsernameApi.as_view()),
    path('top5_pendingemd/', Top5pendingemd.as_view()), 
    path('tenderlist/', views.ListTenderView.as_view()),
    path('totalusers/', views.DashboardStatsView.as_view()),
    path('update-profile-image/', UpdateProfileImageView.as_view(), name='update-profile-image')


]