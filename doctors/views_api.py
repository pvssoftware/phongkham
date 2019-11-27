from datetime import date, datetime, timedelta


from  django.core.exceptions import ObjectDoesNotExist

from rest_framework import status, generics
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from user.models import User, DoctorProfile, SettingsTime
from .utils import get_days_detail, history_serializer_mix
from .custom_token import ExpiringTokenAuthentication
from .models import BookedDay, MedicalRecord, MedicalHistory
from .serializers import MedicalRecordSerializer, ExaminationPatientsSerializer, UploadMedicalUltrasonographySerializer


# create token for user login
class CustomAuthToken(ObtainAuthToken):
    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'maPK': user.pk,
            'dcPK': user.doctor.clinic_address,
            'soDT': user.doctor.phone,
            'tenBS':user.doctor.full_name,
            'loaiBS':user.doctor.get_kind_display()
        })
# delete token when user logout
@api_view(["POST"])
@authentication_classes([ExpiringTokenAuthentication])
def delete_token_logout(request):
    if request.method == "POST":
       user = request.user

       token = Token.objects.get(user=user)
       token.delete()
       return Response({"alert":"Bạn đã xoá token!"})
# get list examination patients
@api_view(["GET"])
@authentication_classes([ExpiringTokenAuthentication])
def get_examination_patients(request):
    if request.method == "GET":
        
        today = date.today()
            
        date_book = date(year=today.year,month=today.month,day=today.day)
        
        examination_list = MedicalHistory.objects.filter(medical_record__doctor__pk=request.user.pk,is_waiting=True).filter(date_booked__date__lte=date_book).order_by("date_booked")
        examination_serializer = ExaminationPatientsSerializer(examination_list, many=True)
        return Response(examination_serializer.data)
    

# upload medical ultrasonography file
@api_view(["PATCH"])
@authentication_classes([ExpiringTokenAuthentication])
def upload_medical_ultrasonography_file(request):
    if request.method == "PATCH":
        data = request.data
        try:
            history = MedicalHistory.objects.get(pk=int(data["id"]))
        except MedicalHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.user.pk == history.medical_record.doctor.pk:

            history_serializer = UploadMedicalUltrasonographySerializer(history,data=data)
            
            if history_serializer.is_valid():
                history_serializer.save()
                return Response(history_serializer.data)

            return Response(history_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

# check doctor
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

# book schedle examination
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
            return history_serializer_mix(data_history,info_bookedday,doctor,date_book,data["soDT"])
        except ObjectDoesNotExist:
            data_record = {
                "phone":data["soDT"],
                "doctor":int(data["maBS"]),
            
            }
            record_serializer = MedicalRecordSerializer(data=data_record)
            if record_serializer.is_valid():
                record_serializer.save()
                return history_serializer_mix(data_history,info_bookedday,doctor,date_book,data["soDT"])

            return Response(record_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            