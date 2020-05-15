from django.contrib import admin
from .models import MedicalRecord, MedicalHistory, Medicine, PrescriptionDrug, PrescriptionDrugOutStock, BookedDay, AppWindow

# Register your models here.

class AppWindowAdmin(admin.ModelAdmin):
    list_display = ["version","release_date","app_ultrasound"]
    model = AppWindow

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["full_name","phone","birth_date","doctor","id","created_at"]
    model = MedicalRecord
    search_fields = ('phone','full_name','doctor__email','doctor__doctor__full_name')

class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ["medical_record","date_booked","get_doctor","id"]
    model = MedicalHistory
    search_fields = ('medical_record__doctor__doctor__full_name','medical_record__doctor__doctor__clinic_name','medical_record__doctor__doctor__phone','medical_record__full_name')
    def get_doctor(self, obj):
        return obj.medical_record.doctor.doctor
    get_doctor.short_description = 'doctor'
    # def get_id(self, obj):
    #     return obj.medical_record.id
    # get_id.short_description = 'id_patient'

class MedicineAdmin(admin.ModelAdmin):
    list_display = ["name","doctor","sale_price","import_price"]
    model = Medicine

class PrescriptionDrugAdmin(admin.ModelAdmin):
    list_display = ["id","medical_history",]
    model = PrescriptionDrug
class PrescriptionDrugOutStockAdmin(admin.ModelAdmin):
    list_display = ["id","medical_history",]
    model = PrescriptionDrugOutStock

class BookedDayAdmin(admin.ModelAdmin):
    list_display = ["doctor","date","max_patients","current_patients"]
    model = BookedDay


admin.site.register(MedicalRecord,MedicalRecordAdmin)
admin.site.register(MedicalHistory,MedicalHistoryAdmin)
admin.site.register(Medicine,MedicineAdmin)
admin.site.register(PrescriptionDrug,PrescriptionDrugAdmin)
admin.site.register(PrescriptionDrugOutStock,PrescriptionDrugOutStockAdmin)
admin.site.register(BookedDay,BookedDayAdmin)
admin.site.register(AppWindow,AppWindowAdmin)


