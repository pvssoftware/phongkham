from datetime import date, datetime, timedelta


from  django.core.exceptions import ObjectDoesNotExist

from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from user.models import User, DoctorProfile, SettingsTime
from .utils import get_days_detail, history_serializer_mix
from .models import BookedDay, MedicalRecord
from .serializers import MedicalRecordSerializer




@api_view(["POST"])
def get_doctor(request):
    if request.method == "POST":
        data = request.data
        try:
            doctor=User.objects.get(pk=int(data["maBS"]))
            if doctor.doctor.settings_time.enable_voice:
                return Response({
                    "maBS":int(data["maBS"]),
                    "tenBS":doctor.doctor.full_name
                },
                status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def create_record_ticket(request):
    if request.method == "POST":
        data = request.data

        date_book = data["ngay"]
        date_book = datetime.strptime(date_book,"%d/%m/%Y")

        today = date.today()

        if date(day=date_book.day,month=date_book.month,year=date_book.year) < today:
            return Response({"alert":"Nhập ngày không hợp lệ!!!"},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        doctor = User.objects.get(pk=int(data["maBS"]))
        try:
            settings_time = doctor.doctor.settings_time
        except:
            settings_time = SettingsTime.objects.create(examination_period="0",doctor=doctor.doctor)

        

        days_detail = get_days_detail(settings_time.weekday_set.all(),date_book,settings_time.examination_period)

        if not days_detail:
           return Response({"alert":"Bác sỹ không làm việc ngày này!!!"},status=status.HTTP_412_PRECONDITION_FAILED)
        
        
        total_patients = 0
        for day_detail in days_detail:
            total_patients += day_detail["total_patients"]

        try:
            info_bookedday = BookedDay.objects.get(doctor=doctor.doctor,date=date_book)
            info_bookedday.max_patients = total_patients
            info_bookedday.save()

            if int(info_bookedday.current_patients) < int(info_bookedday.max_patients):
                total_patients_prevday = 0
                for day_detail in days_detail:
                    if int(info_bookedday.current_patients) < (day_detail["total_patients"]+total_patients_prevday):
                        info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                        info_bookedday.save()

                        datetime_book = datetime.combine(date_book,day_detail["opening_time"]) + timedelta(minutes=(int(info_bookedday.current_patients)-total_patients_prevday-1)*int(doctor.doctor.settings_time.examination_period))
                        break
                    else:
                        total_patients_prevday += day_detail["total_patients"]
                ordinal_number = info_bookedday.current_patients
            else:
                return Response({"alert":"Da full lich kham!!!"},status=status.HTTP_417_EXPECTATION_FAILED)

        except ObjectDoesNotExist:
            info_bookedday = BookedDay.objects.create(doctor=doctor.doctor,date=date_book,max_patients=str(total_patients),current_patients="1")
            datetime_book = datetime.combine(date_book,days_detail[0]["opening_time"])

            ordinal_number = '1'

        data_history = {
            "date_booked":datetime_book.strftime("%d/%m/%Y %H:%M"),
            "medical_record":data["soDT"],
            "ordinal_number":ordinal_number,
            "is_waiting":True
        }

        try:
            MedicalRecord.objects.get(doctor=doctor,phone=data["soDT"])
            return history_serializer_mix(data_history,info_bookedday,doctor,date_book)
        except ObjectDoesNotExist:
            data_record = {
                "phone":data["soDT"],
                "doctor":int(data["maBS"]),
            
            }
            record_serializer = MedicalRecordSerializer(data=data_record)
            if record_serializer.is_valid():
                record_serializer.save()
                return history_serializer_mix(data_history,info_bookedday,doctor,date_book)

            return Response(record_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            