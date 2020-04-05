from django.contrib import admin
from .models import MedicalRecord, MedicalHistory, Medicine, PrescriptionDrug, PrescriptionDrugOutStock, BookedDay, AppWindow

# Register your models here.

class AppWindowAdmin(admin.ModelAdmin):
    list_display = ["version","release_date"]
    model = AppWindow

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["full_name","phone","birth_date","doctor","id","created_at"]
    model = MedicalRecord
    search_fields = ('phone','full_name','doctor__email')

class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ["medical_record","date","get_email","id"]
    model = MedicalHistory
    search_fields = ('medical_record__doctor__email','medical_record__full_name')
    def get_email(self, obj):
        return obj.medical_record.doctor.email
    get_email.short_description = 'doctor'
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


