from datetime import date, timedelta
from django.db.models import Q
from .models import DoctorProfile, License
from celery import task
from celery import shared_task


today = date.today()


@shared_task(name="test")
def test_celery(p, *args, **kwargs):
    print("Hello {}".format(p))


@shared_task(name="check_time_use_trial")
def check_time_use_trial():
    
    doctors = DoctorProfile.objects.filter(is_trial=True,time_end_trial__lte=today)
    for doctor in doctors:
        doctor.is_trial = False
        doctor.save()
        doctor.user.is_active = False
        doctor.user.save()
        
@shared_task(name="check_time_license")
def check_time_license():
    doctors = DoctorProfile.objects.filter(Q(license__license_end__lte=today)|Q(license__isnull=True)).filter(license_ultrasound=False)
    for doctor in doctors:
        doctor.user.is_active = False
        doctor.user.save()
    