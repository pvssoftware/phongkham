from django.contrib import admin
from .models import MedicalRecord, MedicalHistory, Medicine, PrescriptionDrug, BookedDay

# Register your models here.


class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["full_name","birth_date","doctor"]
    model = MedicalRecord

class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ["medical_record","date"]
    model = MedicalHistory

class MedicineAdmin(admin.ModelAdmin):
    list_display = ["name","doctor","sale_price","import_price"]
    model = Medicine

class PrescriptionDrugAdmin(admin.ModelAdmin):
    list_display = ["id","medical_history",]
    model = PrescriptionDrug

class BookedDayAdmin(admin.ModelAdmin):
    list_display = ["doctor","date","max_patients","current_patients"]
    model = BookedDay


admin.site.register(MedicalRecord,MedicalRecordAdmin)
admin.site.register(MedicalHistory,MedicalHistoryAdmin)
admin.site.register(Medicine,MedicineAdmin)
admin.site.register(PrescriptionDrug,PrescriptionDrugAdmin)
admin.site.register(BookedDay,BookedDayAdmin)


