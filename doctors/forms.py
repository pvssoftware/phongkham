from django import forms
from django.core.exceptions import ValidationError

from .models import MedicalRecord, MedicalHistory, PrescriptionDrug, Medicine

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
                  "sex"]


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
    last_menstrual_period = forms.DateField(input_formats=["%d/%m/%Y", ])
    # co_tu_cung_ps = forms.CharField(required=False)
    # tim_thai_ps = forms.CharField(required=False)
    # can_go_ps = forms.CharField(required=False)
    # co_tu_cung_pk = forms.CharField(required=False)
    # am_dao_pk = forms.CharField(required=False)
    # chuan_doan_khac_pk = forms.CharField(required=False)

    class Meta:
        model = MedicalHistory
        fields = ["disease_symptom", "diagnostis","service","PARA","contraceptive","note","last_menstrual_period","co_tu_cung_ps","tim_thai_ps","can_go_ps","co_tu_cung_pk","am_dao_pk","chuan_doan_khac_pk"]


class MedicineForm(forms.ModelForm):

    class Meta:
        model = Medicine
        fields = ["name", 'full_name', 'quantity',
                  'sale_price', 'import_price']

class MedicineEditForm(forms.Form):
    name  = forms.CharField()
    full_name  = forms.CharField()
    add_quantity = forms.CharField(required=False)
    sale_price = forms.CharField()
    import_price = forms.CharField()

    class Meta:
        fields = ["name", 'full_name', 'add_quantity',
                  'sale_price', 'import_price']

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
