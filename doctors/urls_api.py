from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
# from rest_framework_simplejwt.views import TokenRefreshView
from .views_api import  create_record_ticket, get_doctor, CustomAuthToken, get_examination_patients, get_info_patient, upload_medical_ultrasonography_file, upload_medical_test_file, delete_token_logout, check_version_app
# from .jwt_custom import MyTokenObtainPairView

urlpatterns = format_suffix_patterns([
    url(r"^create-ticket/$",create_record_ticket,name="create_ticket"),
    url(r"^get-doctor/$",get_doctor,name="get_doctor"),
    url(r'^get-doctor-token-auth/', CustomAuthToken.as_view()),
    # url(r'^get-token-pair/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # url(r'^refresh-access-token/', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^delete-doctor-token-auth/', delete_token_logout),
    url(r'^get-examination-patients/', get_examination_patients),
    url(r'^get-info-patient/', get_info_patient),
    url(r'^upload-medical-ultrasonography-file/', upload_medical_ultrasonography_file),
    url(r'^upload-medical-test-file/', upload_medical_test_file),
    url(r'^check-update-app-win/', check_version_app),
    # url(r'^update-status-merchant/', update_status_merchant,name="update_status_merchant"),
])