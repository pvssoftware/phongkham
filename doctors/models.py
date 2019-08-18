from django.db import models
from user.models import User

# Create your models here.



class MedicalRecord(models.Model):
    full_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    address = models.CharField(max_length=50)
    sex = models.BooleanField(help_text="True is Female, False is Male")
    doctor = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

class MedicalHistory(models.Model):
    service = models.CharField(max_length=30,default="khám phụ sản")
    disease_symptom = models.TextField()
    #  CHuẩn đoán
    diagnostis = models.TextField()
    # A-B-C-D
    PARA = models.CharField(max_length=10,default="A-B-C-D")
    # Chu kỳ kinh nguyệt cuối
    last_menstrual_period = models.DateField(blank=True,null=True)
    # Biện pháp tránh thai
    contraceptive = models.CharField(max_length=12,default="Khong")
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=40,blank=True,null=True)
    co_tu_cung_ps = models.BooleanField(default=False,help_text='chỉ check khi khám phụ sản')
    tim_thai_ps = models.BooleanField(default=False,help_text='chỉ check khi khám phụ sản')
    can_go_ps = models.BooleanField(default=False,help_text='chỉ check khi khám phụ sản')
    co_tu_cung_pk = models.BooleanField(default=False,help_text='chỉ check khi khám phụ khoa')
    am_dao_pk = models.BooleanField(default=False,help_text='chỉ check khi khám phụ khoa')
    chuan_doan_khac_pk = models.BooleanField(default=False,help_text='chỉ check khi khám phụ khoa')

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)

    def __str__(self):
        return self.medical_record.full_name

class Medicine(models.Model):
    name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    quantity = models.CharField(max_length=10)
    sale_price = models.CharField(max_length=50)
    import_price = models.CharField(max_length=50)
    doctor = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['full_name']


class PrescriptionDrug(models.Model):
    dose = models.CharField(max_length=10)
    time_take_medicine = models.CharField(max_length=30)
    quantity = models.CharField(max_length=10)
    cost = models.CharField(max_length=50)
    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE)
    medical_history = models.ForeignKey(MedicalHistory,on_delete=models.CASCADE)

    def __str__(self):
        return self.medicine.name

