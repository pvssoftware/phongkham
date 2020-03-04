from datetime import date, timedelta
from .models import DoctorProfile, License
from celery import task
from celery import shared_task


today = date.today()


@shared_task(name="test")
def test_celery(p, *args, **kwargs):
    print("Hello {}".format(p))


@shared_task(name="check_time_use_trial")
def check_time_use_trial():
    
    doctors = DoctorProfile.objects.filter(is_trial=True,time_end_trial__lt=today)
    for doctor in doctors:
        doctor.is_trial = False
        doctor.save()
        doctor.user.is_active = False
        doctor.user.save()
        
@shared_task(name="check_time_license")
def check_time_license():
    licenses = License.objects.filter(license_end__lt=today)
    for li in licenses:
        if not li.doctor.license_ultrasound:
            li.doctor.is_active = False
            li.doctor.save()
    