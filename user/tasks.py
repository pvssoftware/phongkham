from datetime import date, timedelta
from .models import DoctorProfile
from celery import task
from celery import shared_task


@shared_task(name="test")
def test_celery(p, *args, **kwargs):
    print("Hello {}".format(p))


@shared_task(name="check_time_use_trial")
def check_time_use_trial():
    today = date.today()
    doctors = DoctorProfile.objects.filter(is_trial=True,time_start_trial__lte=today)
    for doctor in doctors:
        doctor.is_trial = False
        doctor.save()
        doctor.user.is_active = False
        doctor.user.save()
    