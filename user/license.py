from datetime import timedelta

from user.models import License


license_dic = {
    "1year_premium":[365,"5000000"],
    "1month_premium":[30,"500000"],
    "3years_premium":[1095,"1200000"],
    "ultrasound_app":[0,"5000000"]
}

# add license to account payment successful
def add_license(payment,doctor,paydate):
    if payment.license == "ultrasound_app":
        doctor.license_ultrasound = True
    else:
        if doctor.license:
            if doctor.license.license_end > paydate:
                doctor.license.license_end = doctor.license.license_end + timedelta(days=license_dic[payment.license])
            else:
                doctor.license.license_end = paydate + timedelta(days=license_dic[payment.license])
            doctor.license.save()
        else:
            License.objects.create(doctor=doctor,license_end=paydate + timedelta(days=license_dic[payment.license]))
    doctor.is_trial = False
    doctor.save()
    doctor.user.is_active = True
    doctor.user.save()
# check all license
def check_licenses(request):
    try:
        if not request.user.doctor.has_license() and not request.user.doctor.license_ultrasound and not request.user.doctor.is_trial:
            return True
        else:
            return False
    except:
        return True
# check premium license
def check_premium_licenses(request):
    try:
        if not request.user.doctor.has_license() and not request.user.doctor.is_trial:
            return True
        else:
            return False
    except:
        return True
        