from django.conf.urls import url
from .views import search_navbar,DoctorProfileView, medical_record_create, medical_record_edit, medical_record_edit_back_history, medical_record_del,medical_record_view, medical_record_back_view, prescription_drug, take_drug, medical_history_del, remove_drug, final_info, export_final_info_excel, MedicineList, medicine_create, medicine_edit, medicine_del, upload_medicine_excel, search_drugs, cal_benefit, cal_benefit_protect, list_examination, settings_openingtime, settings_service, settings_service_protect, create_weekday, delete_weekday, download_medical_ultrasonography, download_endoscopy




urlpatterns = [

    url(r"^doctor-profile/(?P<pk_doctor>\d+)/search/$",search_navbar,name="search_navbar"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-history-download-endoscopy/(?P<pk_history>\d+)/$",download_endoscopy,name="download_endoscopy"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-history-download-medical-ultrasonography/(?P<pk_history>\d+)/$",download_medical_ultrasonography,name="download_medical_ultrasonography"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/create-weekday/$",create_weekday,name="create_weekday"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/delete-weekday/(?P<pk_weekday>\d+)/$",delete_weekday,name="delete_weekday"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/settings-openingtime/$",settings_openingtime,name="settings_openingtime"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/settings-service/$",settings_service,name="settings_service"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/settings-service-protect/$",settings_service_protect,name="settings_service_protect"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/cal-benefit/$",cal_benefit,name="cal_benefit"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/cal-benefit-protect/$",cal_benefit_protect,name="cal_benefit_protect"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/list-examination/$",list_examination,name="list_examination"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/$",DoctorProfileView.as_view(),name="doctor_profile"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medicine-list/$",MedicineList.as_view(),name="medicine_list"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/search-drugs/$",search_drugs,name="search_drugs"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medicine-create/$",medicine_create,name="medicine_create"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medicine-edit/(?P<pk_medicine>\d+)/$",medicine_edit,name="medicine_edit"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medicine-del/(?P<pk_medicine>\d+)/$",medicine_del,name="medicine_del"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medicine-upload-file-excel/$",upload_medicine_excel,name="upload_medicine_excel"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record-create/$",medical_record_create,name="medical_record_create"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/$",medical_record_view,name="medical_record_view"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record-edit/(?P<pk_mrecord>\d+)/$",medical_record_edit,name="medical_record_edit"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record-edit/(?P<pk_mrecord>\d+)/medical-history/(?P<pk_history>\d+)/$",medical_record_edit_back_history,name="medical_record_edit_back_history"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record-del/(?P<pk_mrecord>\d+)/$",medical_record_del,name="medical_record_del"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-edit/(?P<pk_history>\d+)/$",medical_record_back_view,
    name="medical_record_back_view"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-del/(?P<pk_history>\d+)/$",medical_history_del,name="medical_history_del"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history/(?P<pk_history>\d+)/$",prescription_drug,name="prescription_drug"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history/(?P<pk_history>\d+)/drug/(?P<pk_drug>\d+)/$",take_drug,name="take_drug"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history/(?P<pk_history>\d+)/drug-remove/(?P<pk_prescriptiondrug>\d+)/$",remove_drug,name="remove_drug"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-final/(?P<pk_history>\d+)/$",final_info,name="final_info"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-export/(?P<pk_history>\d+)/$",export_final_info_excel,name="export_final_info_excel"),

    
]