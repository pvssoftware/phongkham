import re, os
import pytz
from django.db import models
from user.models import User, DoctorProfile

# Create your models here.

class BookedDay(models.Model):
    doctor = models.ForeignKey(DoctorProfile,on_delete=models.CASCADE)
    date = models.DateField()
    max_patients = models.CharField(max_length=10)
    current_patients = models.CharField(max_length=5,default="0")

    def __str__(self):
        return self.doctor.full_name



class MedicalRecord(models.Model):
    full_name = models.CharField(max_length=30,blank=True,default="")
    birth_date = models.DateField(blank=True,null=True)
    address = models.CharField(max_length=50,blank=True,default="")
    sex = models.BooleanField(help_text="True is Female, False is Male",default=True)
    phone = models.CharField(max_length = 20,blank=True,null=True)
    password = models.CharField(max_length=10,default="")
    doctor = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return "{}-{}".format(self.full_name, self.phone)


def locate_medical_ultrasonography_upload(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_medical_ultrasonography)
    filename = ("%s_%s_%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone, instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    print(instance)
    return os.path.join("{}/{}/medical_ultrasonography/".format(instance.medical_record.pk,instance.pk),filename)

def locate_endoscopy_upload(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_endoscopy)
    filename = ("%s_%s_%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone,instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    return os.path.join("{}/{}/endoscopy/".format(instance.medical_record.pk,instance.pk),filename)

def locate_medical_test_upload(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_endoscopy)
    filename = ("%s_%s_%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone,instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    return os.path.join("{}/{}/medical_test/".format(instance.medical_record.pk,instance.pk),filename)


class MedicalHistory(models.Model):
    service = models.CharField(max_length=30,default="khám phụ sản")
    disease_symptom = models.TextField(blank=True)
    #  CHuẩn đoán
    diagnostis = models.TextField(blank=True)
    # A-B-C-D
    PARA = models.CharField(max_length=10,default="A-B-C-D",blank=True)
    # Chu kỳ kinh nguyệt cuối
    last_menstrual_period = models.DateField(blank=True,null=True)
    # Biện pháp tránh thai
    contraceptive = models.CharField(max_length=12,default="Khong",blank=True)
    # Huyết áp
    blood_pressure = models.CharField(max_length=50,blank=True,default="")
    # Cân nặng
    weight = models.CharField(max_length=30,blank=True,default="")
    # Chỉ số đường huyết
    glycemic = models.CharField(max_length=50,blank=True,default="")
    # Giấy quỳ pH
    ph_meter = models.CharField(max_length=30,blank=True,default="")

    date = models.DateTimeField(auto_now_add=True)
    date_booked = models.DateTimeField(blank=True,null=True)
    ordinal_number = models.CharField(max_length=10,null=True,blank=True)

    medical_ultrasonography = models.CharField(max_length=200,blank=True,default="")
    medical_ultrasonography_file = models.FileField(upload_to=locate_medical_ultrasonography_upload,blank=True,null=True)

    endoscopy = models.CharField(max_length=200,blank=True,default="")
    endoscopy_file = models.FileField(upload_to=locate_endoscopy_upload,blank=True,null=True)

    medical_test = models.CharField(max_length=200,blank=True,default="")
    medical_test_file = models.FileField(upload_to=locate_medical_test_upload,blank=True,null=True)
    
    co_tu_cung_ps = models.BooleanField(default=False,help_text='chỉ check khi khám phụ sản')
    note_co_tu_cung_ps = models.CharField(max_length=100,blank=True,default="",help_text='chỉ check khi khám cổ tử cung phụ sản')

    tim_thai_ps = models.BooleanField(default=False,help_text='chỉ check khi khám phụ sản')
    note_tim_thai_ps = models.CharField(max_length=100,blank=True,default="",help_text='chỉ check khi khám tim thai phụ sản')

    can_go_ps = models.BooleanField(default=False,help_text='chỉ check khi khám phụ sản')
    note_con_go_ps = models.CharField(max_length=100,blank=True,default="",help_text='chỉ check khi khám cơn gò phụ sản')

    co_tu_cung_pk = models.BooleanField(default=False,help_text='chỉ check khi khám phụ khoa')
    note_co_tu_cung_pk = models.CharField(max_length=100,blank=True,default="",help_text='chỉ check khi khám cổ tử cung phụ khoa')

    am_dao_pk = models.BooleanField(default=False,help_text='chỉ check khi khám phụ khoa')
    note_am_dao_pk = models.CharField(max_length=100,blank=True,default="",help_text='chỉ check khi khám âm đạo phụ khoa')
    
    is_waiting = models.BooleanField(default=False)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)

    def __str__(self):
        return self.medical_record.full_name
    class Meta:
        ordering = ['-date_booked']

class Medicine(models.Model):
    name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=50)
    quantity = models.CharField(max_length=10)
    sale_price = models.CharField(max_length=50)
    import_price = models.CharField(max_length=50)
    doctor = models.ForeignKey(User,on_delete=models.CASCADE)
    date_expired = models.DateField(blank=True,null=True)

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


class AppWindow(models.Model):
    installer = models.FileField(upload_to="installer_win/")
    version = models.CharField(max_length=20)
    release_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.version


