import re
from datetime import date
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
# Create your models here.





class DoctorProfile(models.Model):
    
    KIND_DOCTOR = [
        ("obstetrician-gynecologist","bác sĩ sản phụ khoa"),
        ("Oral maxillofacial surgeon","bác sĩ ngoại răng hàm mặt"),
    ]

    phone = models.CharField(max_length=14)
    hotline = models.CharField(max_length=14,default="")
    full_name = models.CharField(max_length=30)
    clinic_address = models.CharField(max_length=70)
    clinic_name = models.CharField(max_length=100,default="")
    kind = models.CharField(max_length=30, choices=KIND_DOCTOR)
    is_trial = models.BooleanField(default=False)
    time_end_trial = models.DateField(blank=True,null=True)
    license_ultrasound = models.BooleanField(default=False)

    # def __str__(self):
    #     return "{}-{}".format(self.full_name,self.get_kind_display())
    def __str__(self):
        if self.clinic_name:
            return "Bs. {} - Pk. {} - {}".format(self.full_name,self.clinic_name,self.phone)
        else:
            return "Bs. {} - {}".format(self.full_name,self.phone)

    def has_license(self):
        try:
            license = self.license            
        except:
            return False
        
        return license.license_end > date.today()

    def has_trial(self):
        try:
            if self.is_trial:
                return self.time_end_trial > date.today()
            else:
                return False
        except:
            False

class License(models.Model):
    doctor = models.OneToOneField(DoctorProfile,on_delete=models.CASCADE,related_name="license")
    license_end = models.DateField()

class Payment(models.Model):
    email = models.EmailField()
    order_id = models.CharField(max_length=100,unique=True)
    amount = models.CharField(max_length=200)
    order_desc = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20,blank=True)
    success = models.BooleanField(default=False)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    license = models.CharField(max_length=50)
    vnpay_payment_url = models.TextField(default="")

    def save(self, *args, **kwargs):
        # check whether this payment is created or update
        if self.pk is None:
            # get datetime string 
            date_time_string = date.today().strftime("%d%m%y")
            # get all order id numbers of all payments in one day
            order_id_list = Payment.objects.filter(created__date=date.today()).values_list("order_id",flat=True)
            # calculate ordinal_number_string 
            if order_id_list:
                ordinal_number = 1 + max([int(i[14:]) for i in order_id_list])
                ordinal_number_string = (4 - len(str(ordinal_number)))*"0" + str(ordinal_number)
            else:
                ordinal_number_string = "0001"
            # create ticket_id
            self.order_id = "SFCVNPAY"+date_time_string+ordinal_number_string
            print(self.order_id)

        super(Payment, self).save(*args, **kwargs)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
            self, email, password, **kwargs):
        email = self.normalize_email(email)
        is_staff = kwargs.pop('is_staff', False)
        is_superuser = kwargs.pop(
            'is_superuser', False)
        user = self.model(
            email=email,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self, email, password=None,
            **extra_fields):
        return self._create_user(
            email, password, **extra_fields)

    def create_superuser(
            self, email, password,
            **extra_fields):
        return self._create_user(
            email, password,
            is_staff=True, is_superuser=True,
            **extra_fields)

    def update_pw_user(self,email,password):
        email = self.normalize_email(email)
        user = get_user_model().objects.get(email=email)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", max_length=100, unique=True)
    doctor = models.OneToOneField(
        DoctorProfile, on_delete=models.CASCADE,blank=True,null=True)
    is_staff = models.BooleanField("staff status", default=False, help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(
        "active", default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    is_admin = models.BooleanField(
        "admin PVS", default=False, help_text='Designates whether this user should be treated as admin. Admin can manage all doctors.')

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        if self.doctor:
            return "Bs. {} - email: {}".format(self.doctor.full_name,self.email)
        else:
            return self.email

class SettingsTime(models.Model):
    # mon_opening = models.TimeField(blank=True,null=True)
    # mon_closing = models.TimeField(blank=True,null=True)
    # tue_opening = models.TimeField(blank=True,null=True)
    # tue_closing = models.TimeField(blank=True,null=True)
    # wed_opening = models.TimeField(blank=True,null=True)
    # wed_closing = models.TimeField(blank=True,null=True)
    # thu_opening = models.TimeField(blank=True,null=True)
    # thu_closing = models.TimeField(blank=True,null=True)
    # fri_opening = models.TimeField(blank=True,null=True)
    # fri_closing = models.TimeField(blank=True,null=True)
    # sat_opening = models.TimeField(blank=True,null=True)
    # sat_closing = models.TimeField(blank=True,null=True)
    # sun_opening = models.TimeField(blank=True,null=True)
    # sun_closing = models.TimeField(blank=True,null=True)

    examination_period = models.CharField(max_length=10,help_text="(minutes)")
    enable_voice = models.BooleanField(default=False)
    doctor = models.OneToOneField(
        DoctorProfile, on_delete=models.CASCADE, blank=True, null=True, related_name="settings_time")

    def __str__(self):
        if self.doctor:
            return self.doctor.full_name
        else:
            return "-"

class WeekDay(models.Model):
    WEEKDAY={
        ("mon","Thứ Hai"),
        ("tue","Thứ Ba"),
        ("wed","Thứ Tư"),
        ("thu","Thứ Năm"),
        ("fri","Thứ Sáu"),
        ("sat","Thứ Bảy"),
        ("sun","Chủ Nhật"),
    }
    
    day = models.CharField(max_length=10,choices=WEEKDAY)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    settingstime = models.ForeignKey(SettingsTime,on_delete=models.CASCADE)

class SettingsService(models.Model):
    blood_pressure = models.BooleanField(default=False)
    weight = models.BooleanField(default=False)
    glycemic = models.BooleanField(default=False)
    ph_meter = models.BooleanField(default=False)
    take_care_pregnant_baby = models.BooleanField(default=False)
    point_based = models.BooleanField(default=False)

    medical_ultrasonography = models.BooleanField(default=False)
    medical_ultrasonography_cost = models.CharField(max_length=50,blank=True,null=True)
    medical_ultrasonography_multi = models.BooleanField(default=False)


    endoscopy = models.BooleanField(default=False)
    endoscopy_cost = models.CharField(max_length=50,blank=True,null=True)

    medical_test = models.BooleanField(default=False)
    medical_test_cost = models.CharField(max_length=50,blank=True,null=True)
    medical_test_multi = models.BooleanField(default=False)

    password = models.BooleanField(default=False)
    password_field = models.CharField(max_length=20,blank=True,null=True)

    examination_online_cost = models.CharField(max_length=200,blank=True,default="")
    medical_examination_cost = models.CharField(max_length=200,blank=True,null=True)

    doctor = models.OneToOneField(
        DoctorProfile, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.doctor:
            return self.doctor.full_name
        else:
            return "-"

