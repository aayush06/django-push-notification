from django.conf.urls import url, include
from rest_framework.authtoken import views


from .views import (RegisterView, LoginView, DownloadFile, EmployeeData, OrganisationData, check)


urlpatterns = [
    url('register/', RegisterView.as_view(), name='register'),
    url('login/', LoginView.as_view(), name='login'),
    url('download/', DownloadFile.as_view(), name='download-file'),
    url('employee_data/', EmployeeData.as_view(), name='employee-data'),
    url('organisation_data/', OrganisationData.as_view(), name='org-data'),
    url(r'check/',check, name='check'),
]