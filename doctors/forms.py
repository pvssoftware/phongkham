from django import forms

from .models import MedicalRecord, MedicalHistory, PrescriptionDrug, Medicine


class SearchNavBarForm(forms.Form):
    search_navbar = forms.CharField()

    class Meta:
        fields = ["search_navbar"]


class MedicalRecordForm(forms.ModelForm):
    sex = forms.CharField()
    birth_date = forms.DateField(input_formats=["%d/%m/%Y", ])

    class Meta:
        model = MedicalRecord
        fields = ["full_name", "address", "birth_date",
                  "sex", "height", "identity_card"]


class MedicalHistoryForm(forms.ModelForm):

    class Meta:
        model = MedicalHistory
        fields = ["disease_symptom", "diagnostis"]


class MedicineForm(forms.ModelForm):

    class Meta:
        model = Medicine
        fields = ["name", 'full_name', 'quantity',
                  'sale_price', 'import_price']


class SearchDrugForm(forms.Form):

    search_drug = forms.CharField()

    class Meta:
        fields = ["search_drug"]


class TakeDrugForm(forms.ModelForm):
    class Meta:
        model = PrescriptionDrug
        fields = ["dose", "time_take_medicine", "quantity"]
