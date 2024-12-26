from django.urls import path
from . import views
urlpatterns = [
    path('addusers/',views.AdminAddUsersApi.as_view()),
    path('account/',views.ChangeAddressApi.as_view()),
    path('license/',views.AddLicense.as_view()),
    path('list/',views.LicenseListView.as_view()),
    path('edit/',views.UpdateLicenseView.as_view()),
    path('editpassword/',views.ChangePasswordApi.as_view()),       

]