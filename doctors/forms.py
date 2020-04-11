import re
from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist 
from django.conf import settings
from user.models import SettingsTime, SettingsService, WeekDay
from .models import MedicalRecord, MedicalHistory, PrescriptionDrug, PrescriptionDrugOutStock, Medicine
from .utils_forms import clean_upload_file
from user.utils import get_price_ultrasound_app_or_setting



class PatientLoginForm(forms.Form):
    phone = forms.CharField(label="Số điện thoại",max_length=14,help_text="Số điện thoại cá nhân.")

    password = forms.CharField(label=("Mật khẩu"),
        widget=forms.PasswordInput,
        help_text=("Mật khẩu được cấp bởi bác sĩ khi bệnh nhân khám bệnh."))
    doctor = forms.CharField(label="Mã phòng khám",max_length=13,help_text="Mã phòng khám mà bệnh nhân đã khám bệnh.")

    class Meta:
        fields = ("phone","password","doctor")

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        
        valid_phone = re.match(r"^(0|\+84)(9|3|7|8|5)([0-9]{8})$",phone)
        if not valid_phone:
            raise forms.ValidationError('Số điện thoại không hợp lệ.',
                code='invalid_phone',)
        return phone

class PatientBookForm(forms.Form):
    date = forms.DateField(input_formats=["%d/%m/%Y", ])
    class Meta:
        fields = ["date",]
class AddLinkMeetingForm(forms.Form):
    link_meeting = forms.CharField()
    class Meta:
        fields = ["link_meeting",]

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
    medical_ultrasonography_multi = forms.BooleanField(required=False)
    endoscopy = forms.BooleanField(required=False)
    medical_test = forms.BooleanField(required=False)
    password = forms.BooleanField(required=False)
    examination_online_cost = forms.CharField(required=False)
    
    class Meta:
        model = SettingsService
        fields = "__all__"
        # exclude = ['medical_ultrasonography_cost']
    
    

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
    password = forms.CharField(required=False)

    class Meta:
        model = MedicalRecord
        fields = ["full_name", "address", "birth_date",
                  "sex","phone","password"]
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
        fields = ["disease_symptom", "diagnostis","service","PARA","contraceptive","last_menstrual_period","co_tu_cung_ps","note_co_tu_cung_ps","tim_thai_ps","note_tim_thai_ps","can_go_ps","note_con_go_ps","co_tu_cung_pk","note_co_tu_cung_pk","am_dao_pk","note_am_dao_pk","is_waiting","medical_ultrasonography","medical_ultrasonography_file","medical_ultrasonography_2","medical_ultrasonography_file_2","medical_ultrasonography_3","medical_ultrasonography_file_3","endoscopy","endoscopy_file","blood_pressure","weight","glycemic","ph_meter","medical_test","medical_test_file"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(MedicalHistoryFormMix, self).__init__(*args, **kwargs)
        
    def clean_medical_ultrasonography_file(self):
        file = self.cleaned_data.get("medical_ultrasonography_file")
        
        return clean_upload_file(file)

    def clean_medical_ultrasonography_file_2(self):
        file = self.cleaned_data.get("medical_ultrasonography_file_2")
        
        return clean_upload_file(file)

    def clean_medical_ultrasonography_file_3(self):
        file = self.cleaned_data.get("medical_ultrasonography_file_3")
        
        return clean_upload_file(file)

    def clean_endoscopy_file(self):
        file = self.cleaned_data.get("endoscopy_file")
        return clean_upload_file(file)

    def clean_medical_test_file(self):
        file = self.cleaned_data.get("medical_test_file")
        return clean_upload_file(file)

    def save(self,commit=True):
        history = super().save(commit=commit)
        print("save")
        print(commit)
        print(history.medical_ultrasonography_cost)
    
        history.medical_ultrasonography_cost = history.medical_ultrasonography_cost_2 = history.medical_ultrasonography_cost_3 = get_price_ultrasound_app_or_setting(self.user,"0")
        
        if commit:
            history.save()
        return history


class MedicineForm(forms.ModelForm):
    date_expired = forms.DateField(input_formats=["%d/%m/%Y", ],required = False)
    unit = forms.CharField()
    class Meta:
        model = Medicine
        fields = ["name", 'full_name', 'quantity',
                  'sale_price', 'import_price',"date_expired","unit"]
    def clean_date_expired(self):
        date_expired = self.cleaned_data['date_expired']
        if date_expired:
            return date_expired
        return None

class MedicineEditForm(forms.Form):
    name  = forms.CharField()
    full_name  = forms.CharField()
    add_quantity = forms.CharField(required=False)
    sale_price = forms.CharField()
    import_price = forms.CharField()
    date_expired = forms.DateField(input_formats=["%d/%m/%Y", ],required = False)
    unit = forms.CharField()

    class Meta:
        fields = ["name", 'full_name', 'add_quantity',
                  'sale_price', 'import_price','date_expired',"unit"]
                  
    def clean_date_expired(self):
        date_expired = self.cleaned_data['date_expired']
        if date_expired:
            return date_expired
        return None

class UploadMedicineForm(forms.Form):
    file_excel = forms.FileField(help_text="chưa chọn file")

    class Meta:
        fields = ["file_excel"]

    def clean_file_excel(self):
        file_excel = self.cleaned_data.get("file_excel")
        if file_excel:
            if file_excel.name.endswith((".xls",".xlsx")):
                
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

    def __init__(self, *args, **kwargs):
        self.drug = kwargs.pop('drug',None)
        super(TakeDrugForm, self).__init__(*args, **kwargs)
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if int(quantity) > int(self.drug.quantity):
            raise forms.ValidationError("Số thuốc trong kho không đủ để thêm vào toa",code="invalid")
        return quantity


class TakeDrugOutStockForm(forms.ModelForm):
    cost = forms.CharField(required=False)
    class Meta:
        model = PrescriptionDrugOutStock
        fields = ["dose", "time_take_medicine", "quantity","cost","name","unit"]

    def clean_cost(self):
        cost = self.cleaned_data["cost"]
        if not cost:
            cost = "0"
        return cost
