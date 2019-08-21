from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
# Create your models here.

class DoctorProfile(models.Model):
    
    KIND_DOCTOR = [
        ("gynecologist","bác sĩ phụ khoa"),
        ("Oral maxillofacial surgeon","bác sĩ ngoại răng hàm mặt"),
    ]

    phone = models.CharField(max_length=14)
    full_name = models.CharField(max_length=30, unique=True)
    clinic_address = models.CharField(max_length=70)
    kind = models.CharField(max_length=30, choices=KIND_DOCTOR)

    def __str__(self):
        return "{}-{}".format(self.full_name,self.get_kind_display())

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
