from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views_api import  create_record_ticket, get_doctor

urlpatterns = format_suffix_patterns([
    url(r"^create-ticket/$",create_record_ticket,name="create_ticket"),
    url(r"^get-doctor/$",get_doctor,name="get_doctor"),
])