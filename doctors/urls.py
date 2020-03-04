from django.conf.urls import url
from .views import search_navbar,DoctorProfileView, medical_record_create, medical_record_edit, medical_record_edit_back_history, medical_record_del,medical_record_view, medical_record_back_view, prescription_drug, take_drug, medical_history_del, remove_drug, remove_drug_out_stock, final_info, export_final_info_excel, export_final_info_excel_patient, MedicineList, medicine_create, medicine_edit,  medicine_edit_protect, medicine_del, upload_medicine_excel, search_drugs, cal_benefit, cal_benefit_protect, list_examination, settings_openingtime, settings_service, settings_service_protect, create_weekday, delete_weekday, download_medical_ultrasonography, download_endoscopy, merge_history_search, merge_history_confirm, merge_history, changelog_update_app, patient_login, patient_profile, patient_logout, check_license
from .views_api import download_xml_update



urlpatterns = [

    url(r"^check-license/(?P<pk_doctor>\d+)/$",check_license,name="check_license"),
    url(r"^patient-profile/(?P<pk_mrecord>\d+)/$",patient_profile,name="patient_profile"),
    url(r"^patient-logout/$",patient_logout,name="patient_logout"),
    url(r"^patient-login/$",patient_login,name="patient_login"),
    url(r"^changelog-update-app/$",changelog_update_app,name="changelog_update_app"),
    url(r"^download-xml-update/$",download_xml_update,name="download_xml_update"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record-merge/(?P<pk_mrecord>\d+)/medical-history-merge-confirm/(?P<pk_history>\d+)/$",merge_history_confirm,name="merge_history_confirm"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record-merge/(?P<pk_mrecord>\d+)/medical-history-merge/(?P<pk_history>\d+)/$",merge_history,name="merge_history"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-history-merge-search/(?P<pk_history>\d+)/$",merge_history_search,name="merge_history_search"),
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
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medicine-edit-protect/(?P<pk_medicine>\d+)/$",medicine_edit_protect,name="medicine_edit_protect"),
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
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history/(?P<pk_history>\d+)/drug-outstock-remove/(?P<pk_prescriptiondrugoutstock>\d+)/$",remove_drug_out_stock,name="remove_drug_out_stock"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-final/(?P<pk_history>\d+)/$",final_info,name="final_info"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-export-excel/(?P<pk_history>\d+)/$",export_final_info_excel,name="export_final_info_excel"),
    url(r"^doctor-profile/(?P<pk_doctor>\d+)/medical-record/(?P<pk_mrecord>\d+)/medical-history-export-excel-drug-patient/(?P<pk_history>\d+)/$",export_final_info_excel_patient,name="export_final_info_excel_patient"),

    
]