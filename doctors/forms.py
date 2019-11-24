from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist 
from django.conf import settings
from user.models import SettingsTime, SettingsService, WeekDay
from .models import MedicalRecord, MedicalHistory, PrescriptionDrug, Medicine
from .utils_forms import clean_upload_file


class PasswordProtectForm(forms.Form):
    password = forms.CharField()
    class Meta:
        fields = ("password",)

class WeekDayForm(forms.ModelForm):

    class Meta:
        model = WeekDay
        fields = ["day","opening_time","closing_time"]

class SettingsTimeForm(forms.ModelForm):

    enable_voice = forms.BooleanField(required=False)
    examination_period = forms.CharField(required=False)
    class Meta:
        model = SettingsTime
        fields = ["enable_voice","examination_period"]


class SettingsServiceForm(forms.ModelForm):
    blood_pressure = forms.BooleanField(required=False)
    weight = forms.BooleanField(required=False)
    glycemic = forms.BooleanField(required=False)
    ph_meter = forms.BooleanField(required=False)
    medical_ultrasonography = forms.BooleanField(required=False)
    endoscopy = forms.BooleanField(required=False)
    medical_test = forms.BooleanField(required=False)
    password = forms.BooleanField(required=False)
    
    class Meta:
        model = SettingsService
        fields = "__all__"
    

class CalculateBenefitForm(forms.Form):
    from_date = forms.DateField(input_formats=["%d/%m/%Y", ])
    to_date = forms.DateField(input_formats=["%d/%m/%Y", ])
    class Meta:
        fields = ["from_date","to_date"]

        
class SearchNavBarForm(forms.Form):
    search_navbar = forms.CharField()

    class Meta:
        fields = ["search_navbar"]


class MedicalRecordForm(forms.ModelForm):
    sex = forms.CharField()
    birth_date = forms.DateField(input_formats=["%Y"])

    class Meta:
        model = MedicalRecord
        fields = ["full_name", "address", "birth_date",
                  "sex","phone"]
    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor',None)
        self.pk_mrecord = kwargs.pop('pk_mrecord',None)
        super(MedicalRecordForm, self).__init__(*args, **kwargs)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        print(phone)
        if phone == None:
            return None
        else:
            try:
                record = MedicalRecord.objects.get(doctor=self.doctor,phone=phone)
                print(record.pk)
                print(self.pk_mrecord)
                if self.pk_mrecord:
                    print(type(self.pk_mrecord))
                    if record.pk == int(self.pk_mrecord):
                        print("valid")
                        return phone
                raise forms.ValidationError("Số điện thoại trùng với bệnh nhân khác")
            except ObjectDoesNotExist:
                return phone


# class MedicalHistoryForm(forms.ModelForm):

#     class Meta:
#         model = MedicalHistory
#         fields = ["disease_symptom", "diagnostis","service","PARA","last_menstrual_period","contraceptive","note"]

class MedicalHistoryFormMix(forms.ModelForm):
    # disease_symptom = forms.CharField()
    # diagnostis = forms.CharField()
    # service = forms.CharField()
    # PARA = forms.CharField()
    # contraceptive = forms.CharField()
    # note = forms.CharField(required=False)
    last_menstrual_period = forms.DateField(input_formats=["%d/%m/%Y",], required=False)
    # is_waiting = forms.CharField()
    # co_tu_cung_ps = forms.CharField(required=False)
    # tim_thai_ps = forms.CharField(required=False)
    # can_go_ps = forms.CharField(required=False)
    # co_tu_cung_pk = forms.CharField(required=False)
    # am_dao_pk = forms.CharField(required=False)
    # chuan_doan_khac_pk = forms.CharField(required=False)

    class Meta:
        model = MedicalHistory
        fields = ["disease_symptom", "diagnostis","service","PARA","contraceptive","last_menstrual_period","co_tu_cung_ps","note_co_tu_cung_ps","tim_thai_ps","note_tim_thai_ps","can_go_ps","note_con_go_ps","co_tu_cung_pk","note_co_tu_cung_pk","am_dao_pk","note_am_dao_pk","is_waiting","medical_ultrasonography","medical_ultrasonography_file","endoscopy","endoscopy_file","blood_pressure","weight","glycemic","ph_meter","medical_test","medical_test_file"]
        
    def clean_medical_ultrasonography_file(self):
        file = self.cleaned_data.get("medical_ultrasonography_file")
        
        return clean_upload_file(file)

    def clean_endoscopy_file(self):
        file = self.cleaned_data.get("endoscopy_file")
        return clean_upload_file(file)

    def clean_medical_test_file(self):
        file = self.cleaned_data.get("medical_test_file")
        return clean_upload_file(file)


class MedicineForm(forms.ModelForm):
    date_expired = forms.DateField(input_formats=["%d/%m/%Y", ])
    class Meta:
        model = Medicine
        fields = ["name", 'full_name', 'quantity',
                  'sale_price', 'import_price',"date_expired"]

class MedicineEditForm(forms.Form):
    name  = forms.CharField()
    full_name  = forms.CharField()
    add_quantity = forms.CharField(required=False)
    sale_price = forms.CharField()
    import_price = forms.CharField()
    date_expired = forms.DateField(input_formats=["%d/%m/%Y", ])

    class Meta:
        fields = ["name", 'full_name', 'add_quantity',
                  'sale_price', 'import_price','date_expired']

class UploadMedicineForm(forms.Form):
    file_excel = forms.FileField(help_text="chưa chọn file")

    class Meta:
        fields = ["file_excel"]

    def clean_file_excel(self):
        file_excel = self.cleaned_data.get("file_excel")
        if file_excel:
            if file_excel.name.endswith((".xls",".xlsx")):
                print("excel")
                return file_excel
            else:
                raise ValidationError("The File is not a excel file. Please upload only excel file.")


class SearchDrugForm(forms.Form):

    search_drug = forms.CharField()

    class Meta:
        fields = ["search_drug"]


class TakeDrugForm(forms.ModelForm):
    class Meta:
        model = PrescriptionDrug
        fields = ["dose", "time_take_medicine", "quantity"]
