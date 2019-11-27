from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from .views_api import  create_record_ticket, get_doctor, CustomAuthToken, get_examination_patients, upload_medical_ultrasonography_file, delete_token_logout

urlpatterns = format_suffix_patterns([
    url(r"^create-ticket/$",create_record_ticket,name="create_ticket"),
    url(r"^get-doctor/$",get_doctor,name="get_doctor"),
    url(r'^get-doctor-token-auth/', CustomAuthToken.as_view()),
    url(r'^delete-doctor-token-auth/', delete_token_logout),
    url(r'^get-examination-patients/', get_examination_patients),
    url(r'^upload-medical-ultrasonography-file/', upload_medical_ultrasonography_file),
])