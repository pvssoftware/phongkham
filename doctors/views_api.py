from datetime import date, datetime, timedelta
import os, json
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from  django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.shortcuts import render

from rest_framework import status, generics
from rest_framework.decorators import api_view, authentication_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import User, DoctorProfile, SettingsTime
from user.license import check_licenses, check_premium_licenses
from .utils import get_days_detail, history_serializer_mix, update_examination_patients_list, update_examination_patients_finished_list
from .custom_token import ExpiringTokenAuthentication,is_token_expired
from .models import BookedDay, MedicalRecord, MedicalHistory, AppWindow
from .serializers import MedicalRecordSerializer, ExaminationPatientsUltrasoundSerializer, MedicalRecordExaminationSerializer,UploadMedicalUltrasonographySerializer, UploadMedicalUltrasonographySerializer2, UploadMedicalUltrasonographySerializer3, ResponseUploadMedicalUltrasonographySerializer, CreateUploadMedicalUltrasonographySerializer, UploadMedicalTestSerializer, UploadMedicalTestSerializer2, UploadMedicalTestSerializer3, ResponseUploadMedicalTestSerializer, CreateUploadMedicalTestSerializer, ExaminationPatientsMedicalTestSerializer


# update status merchant
# @api_view(["POST"])
# @renderer_classes([TemplateHTMLRenderer])
# def update_status_merchant(request):
#     if request.method == "POST":
#         data = request.data
#         return Response({"user":data['test']},template_name="user/update_status_merchant.html")


# link download file xml
def download_xml_update(request):
    installer = AppWindow.objects.get(pk=1)
    file_path = installer.installer.path
    # file_xml = ET.parse(file_path)
    # print(file_path)
    # xml_content = ET.tostring(file_xml.getroot(),encoding='unicode')
    return HttpResponse(open(file_path).read(),content_type='text/xml')
    

# update app desktop window
@api_view(["GET"])
def check_version_app(request):
    if request.method == "GET":
        data = request.data
        installer = AppWindow.objects.get(pk=1)

        data_version = data['version'].split(".")
        installer_version = installer.version.split(".")
        if (data_version[0] != installer_version[0]) or (data_version[3] != installer_version[3]):
            return Response({
                "new_version": installer.version
            },status=status.HTTP_200_OK)

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
# create token for user login
class CustomAuthToken(ObtainAuthToken):
    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        if is_token_expired(token):
            token.delete()
            token = Token.objects.create(user = token.user)
            
        return Response({
            'token': token.key,
            'maPK': user.pk,
            'dcPK': user.doctor.clinic_address,
            'tenPK': user.doctor.clinic_name,
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
        service = request.GET.get("service")
        if service == "ultrasound":
            examination_serializer = ExaminationPatientsUltrasoundSerializer(examination_list, many=True,context={"request": request})
        elif service == "medicaltest":
            examination_serializer = ExaminationPatientsMedicalTestSerializer(examination_list, many=True,context={"request": request})
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(examination_serializer.data)

# get infomation patient
@api_view(["GET"])
@authentication_classes([ExpiringTokenAuthentication])   
def get_info_patient(request):
   if request.method == "GET":

        # data = request.data
        phone = request.GET.get('phone')
        try:
           mrecord = MedicalRecord.objects.get(phone=phone,doctor=request.user)
        except MedicalRecord.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        mrecord_serializer = MedicalRecordExaminationSerializer(mrecord,context={"request": request})
        
        return Response(mrecord_serializer.data)  
      
# upload medical ultrasonography file
@api_view(["PATCH","POST"])
@authentication_classes([ExpiringTokenAuthentication])
def upload_medical_ultrasonography_file(request):
    if request.method == "PATCH":
        data = request.data
        json_file = json.loads(data['json_file'])
        # update info patient
        if data['id_patient']:
            try:
                mrecord = MedicalRecord.objects.get(pk=int(data["id_patient"]),doctor=request.user)
                mrecord.full_name = data['full_name']
                mrecord.birth_date = date(year=int(data["birth_date"]),month=1,day=1)
                mrecord.address = data['address']
                mrecord.sex = json_file['sex']
                mrecord.save()
            except MedicalRecord.DoesNotExist:
                return Response({"alert":"Mã bệnh nhân không hợp lệ!!!"},status=status.HTTP_404_NOT_FOUND)

        # upload file
        try:
            history = MedicalHistory.objects.get(pk=int(data["id"]))
        except MedicalHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.user.pk == history.medical_record.doctor.pk:
            if data["seq"] == "1":
                history_serializer = UploadMedicalUltrasonographySerializer(history,data=data,context={"request": request,"is_waiting":json_file["is_waiting"]})
            elif data["seq"] == "2":
                history_serializer = UploadMedicalUltrasonographySerializer2(history,data=data,context={"request": request,"is_waiting":json_file["is_waiting"]})
            elif data["seq"] == "3":
                history_serializer = UploadMedicalUltrasonographySerializer3(history,data=data,context={"request": request,"is_waiting":json_file["is_waiting"]})
            
            if history_serializer.is_valid():
                history_serializer.save()

                # update list examination patients
                update_examination_patients_list(request.user,date.today(),False)

                # update list examination patients finished
                update_examination_patients_finished_list(request.user,date.today())

                history = MedicalHistory.objects.get(pk=history_serializer.data["id"])
                # response_data = CreateUploadMedicalUltrasonographySerializer(history,context={"request": request})
                response_data = ResponseUploadMedicalUltrasonographySerializer(history,context={"request": request})
                
                return Response(response_data.data)

            return Response(history_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST':
        data = request.data
        json_file = json.loads(data['json_file'])
        # update info patient
        if data['id_patient']:
            try:
                mrecord = MedicalRecord.objects.get(pk=int(data["id_patient"]),doctor=request.user)
                mrecord.full_name = data['full_name']
                mrecord.birth_date = date(year=int(data["birth_date"]),month=1,day=1)
                mrecord.address = data['address']
                mrecord.sex = json_file['sex']
                mrecord.save()
            except MedicalRecord.DoesNotExist:
                return Response({"alert":"Mã bệnh nhân không hợp lệ!!!"},status=status.HTTP_404_NOT_FOUND)

        else:
            mrecord = MedicalRecord.objects.create(doctor=request.user,full_name=data['full_name'],birth_date=date(year=int(data["birth_date"]),month=1,day=1),sex=json_file['sex'],phone=data['phone'],address=data['address'])
        
        try:
            settings_time = request.user.doctor.settings_time
        except:
            settings_time = SettingsTime.objects.create(examination_period="0",doctor=request.user.doctor)
        
        today = date.today()                       
        date_book = date(year=today.year,month=today.month,day=today.day)

        if json_file['is_waiting']:
            
            if settings_time.enable_voice:
                days_detail = get_days_detail(settings_time.weekday_set.all(),date_book,settings_time.examination_period)
                if not days_detail:
                    response_data = MedicalRecordExaminationSerializer(mrecord,context={"request": request})
                    return Response(response_data.data,status=status.HTTP_400_BAD_REQUEST)
                
                total_patients = 0
                for day_detail in days_detail:
                    total_patients += day_detail["total_patients"]
                    closing_time = day_detail["closing_time"]

                try:
                    info_bookedday = BookedDay.objects.get(doctor=request.user.doctor,date=date_book)
                    info_bookedday.max_patients = total_patients
                    info_bookedday.save()
                    if int(info_bookedday.current_patients) < int(info_bookedday.max_patients):
                        full_booked = False
                        total_patients_prevday = 0
                        for day_detail in days_detail:
                            if int(info_bookedday.current_patients) < (day_detail["total_patients"]+total_patients_prevday):
                                info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                                info_bookedday.save()

                                datetime_book = datetime.combine(date_book,day_detail["opening_time"]) + timedelta(minutes=(int(info_bookedday.current_patients)-total_patients_prevday-1)*int(request.user.doctor.settings_time.examination_period))
                                break
                            else:
                                total_patients_prevday += day_detail["total_patients"]
                            
                    else:
                        full_booked = True

                        info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                        info_bookedday.save()

                        datetime_book = datetime.combine(date_book,closing_time) + timedelta(minutes=(int(info_bookedday.current_patients)- int(info_bookedday.max_patients))*int(request.user.doctor.settings_time.examination_period))
                        print("max")
                    
                    ordinal_number = info_bookedday.current_patients
                    date_booked = datetime_book

                except ObjectDoesNotExist:
                    full_booked = False

                    BookedDay.objects.create(doctor=request.user.doctor,date=date_book,max_patients=str(total_patients),current_patients="1")
                    datetime_book = datetime.combine(date_book,days_detail[0]["opening_time"])

                    ordinal_number = '1'
                    date_booked = datetime_book
            else:
                full_booked = False
                try:
                    info_bookedday = BookedDay.objects.get(doctor=request.user.doctor,date=date_book)
                    info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                    info_bookedday.save()
                    
                except ObjectDoesNotExist:
                    info_bookedday = BookedDay.objects.create(doctor=request.user.doctor,date=date_book,max_patients="limitless",current_patients="1")

                date_booked = datetime.now()
                ordinal_number = info_bookedday.current_patients
                

        else:
            date_booked = datetime.now()
            ordinal_number = "-1"
            
        if not data['medical_ultrasonography_file']:
            medical_ultrasonography_file = None
        else:
            medical_ultrasonography_file = data['medical_ultrasonography_file']
        try:

            medical_ultrasonography_cost = data['medical_ultrasonography_cost']
        except:
            medical_ultrasonography_cost = "0"
            
        data_history = {
            # "medical_record":mrecord,
            "date_booked":date_booked,
            "medical_ultrasonography_file":medical_ultrasonography_file,
            "medical_ultrasonography_cost":medical_ultrasonography_cost,
            "medical_ultrasonography":data["medical_ultrasonography"],
            "is_waiting":json_file["is_waiting"],
            "ordinal_number":ordinal_number

        }
        print(data_history)
        history_serializer = CreateUploadMedicalUltrasonographySerializer(data=data_history,context={"request": request,"medical_record":mrecord})
        if history_serializer.is_valid():
            history_serializer.save()
            
            if json_file["is_waiting"]:
                print(date_book)
                update_examination_patients_list(request.user,date_book,full_booked)
            # update list examination patients finished
            update_examination_patients_finished_list(request.user,date_book)           
             
            return Response(history_serializer.data)
        return Response(history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# upload medical test file
@api_view(["PATCH","POST"])
@authentication_classes([ExpiringTokenAuthentication])       
def upload_medical_test_file(request):
    if request.method == "PATCH":
        data = request.data
        json_file = json.loads(data['json_file'])
        # update info patient
        if data['id_patient']:
            try:
                mrecord = MedicalRecord.objects.get(pk=int(data["id_patient"]),doctor=request.user)
                mrecord.full_name = data['full_name']
                mrecord.birth_date = date(year=int(data["birth_date"]),month=1,day=1)
                mrecord.address = data['address']
                mrecord.sex = json_file['sex']
                mrecord.save()
            except MedicalRecord.DoesNotExist:
                return Response({"alert":"Mã bệnh nhân không hợp lệ!!!"},status=status.HTTP_404_NOT_FOUND)

        # upload file
        try:
            history = MedicalHistory.objects.get(pk=int(data["id"]))
        except MedicalHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.user.pk == history.medical_record.doctor.pk:
            if data["seq"] == "1":
                history_serializer = UploadMedicalTestSerializer(history,data=data,context={"request": request,"is_waiting":json_file["is_waiting"]})
            elif data["seq"] == "2":
                history_serializer = UploadMedicalTestSerializer2(history,data=data,context={"request": request,"is_waiting":json_file["is_waiting"]})
            elif data["seq"] == "3":
                history_serializer = UploadMedicalTestSerializer3(history,data=data,context={"request": request,"is_waiting":json_file["is_waiting"]})
            
            if history_serializer.is_valid():
                history_serializer.save()

                # update list examination patients
                update_examination_patients_list(request.user,date.today(),False)

                # update list examination patients finished
                update_examination_patients_finished_list(request.user,date.today())

                history = MedicalHistory.objects.get(pk=history_serializer.data["id"])
                
                response_data = ResponseUploadMedicalTestSerializer(history,context={"request": request})
                
                return Response(response_data.data)

            return Response(history_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST':
        data = request.data
        json_file = json.loads(data['json_file'])
        # update info patient
        if data['id_patient']:
            try:
                mrecord = MedicalRecord.objects.get(pk=int(data["id_patient"]),doctor=request.user)
                mrecord.full_name = data['full_name']
                mrecord.birth_date = date(year=int(data["birth_date"]),month=1,day=1)
                mrecord.address = data['address']
                mrecord.sex = json_file['sex']
                mrecord.save()
            except MedicalRecord.DoesNotExist:
                return Response({"alert":"Mã bệnh nhân không hợp lệ!!!"},status=status.HTTP_404_NOT_FOUND)

        else:
            mrecord = MedicalRecord.objects.create(doctor=request.user,full_name=data['full_name'],birth_date=date(year=int(data["birth_date"]),month=1,day=1),sex=json_file['sex'],phone=data['phone'],address=data['address'])
        
        try:
            settings_time = request.user.doctor.settings_time
        except:
            settings_time = SettingsTime.objects.create(examination_period="0",doctor=request.user.doctor)
        
        today = date.today()                       
        date_book = date(year=today.year,month=today.month,day=today.day)

        if json_file['is_waiting']:
            
            if settings_time.enable_voice:
                days_detail = get_days_detail(settings_time.weekday_set.all(),date_book,settings_time.examination_period)
                if not days_detail:
                    response_data = MedicalRecordExaminationSerializer(mrecord,context={"request": request})
                    return Response(response_data.data,status=status.HTTP_400_BAD_REQUEST)
                
                total_patients = 0
                for day_detail in days_detail:
                    total_patients += day_detail["total_patients"]
                    closing_time = day_detail["closing_time"]

                try:
                    info_bookedday = BookedDay.objects.get(doctor=request.user.doctor,date=date_book)
                    info_bookedday.max_patients = total_patients
                    info_bookedday.save()
                    if int(info_bookedday.current_patients) < int(info_bookedday.max_patients):
                        full_booked = False
                        total_patients_prevday = 0
                        for day_detail in days_detail:
                            if int(info_bookedday.current_patients) < (day_detail["total_patients"]+total_patients_prevday):
                                info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                                info_bookedday.save()

                                datetime_book = datetime.combine(date_book,day_detail["opening_time"]) + timedelta(minutes=(int(info_bookedday.current_patients)-total_patients_prevday-1)*int(request.user.doctor.settings_time.examination_period))
                                break
                            else:
                                total_patients_prevday += day_detail["total_patients"]
                            
                    else:
                        full_booked = True

                        info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                        info_bookedday.save()

                        datetime_book = datetime.combine(date_book,closing_time) + timedelta(minutes=(int(info_bookedday.current_patients)- int(info_bookedday.max_patients))*int(request.user.doctor.settings_time.examination_period))
                        print("max")
                    
                    ordinal_number = info_bookedday.current_patients
                    date_booked = datetime_book

                except ObjectDoesNotExist:
                    full_booked = False

                    BookedDay.objects.create(doctor=request.user.doctor,date=date_book,max_patients=str(total_patients),current_patients="1")
                    datetime_book = datetime.combine(date_book,days_detail[0]["opening_time"])

                    ordinal_number = '1'
                    date_booked = datetime_book
            else:
                full_booked = False
                try:
                    info_bookedday = BookedDay.objects.get(doctor=request.user.doctor,date=date_book)
                    info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                    info_bookedday.save()
                    
                except ObjectDoesNotExist:
                    info_bookedday = BookedDay.objects.create(doctor=request.user.doctor,date=date_book,max_patients="limitless",current_patients="1")

                date_booked = datetime.now()
                ordinal_number = info_bookedday.current_patients
                

        else:
            date_booked = datetime.now()
            ordinal_number = "-1"
            
        if not data['medical_test_file']:
            medical_test_file = None
        else:
            medical_test_file = data['medical_test_file']
        try:

            medical_test_cost = data['medical_test_cost']
        except:
            medical_test_cost = "0"
            
        data_history = {
            # "medical_record":mrecord,
            "date_booked":date_booked,
            "medical_test_file":medical_test_file,
            "medical_test_cost":medical_test_cost,
            "medical_test":data["medical_test"],
            "is_waiting":json_file["is_waiting"],
            "ordinal_number":ordinal_number

        }
        print(data_history)
        history_serializer = CreateUploadMedicalTestSerializer(data=data_history,context={"request": request,"medical_record":mrecord})
        if history_serializer.is_valid():
            history_serializer.save()
            
            if json_file["is_waiting"]:
                print(date_book)
                update_examination_patients_list(request.user,date_book,full_booked)
            # update list examination patients finished
            update_examination_patients_finished_list(request.user,date_book)           
             
            return Response(history_serializer.data)
        return Response(history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# check doctor
@api_view(["POST"])
def get_doctor(request):
    if request.method == "POST":
        data = request.data
        try:
            doctor=User.objects.get(pk=int(data["maBS"]))
            # check license
            if not doctor.is_active:
                return Response(status=status.HTTP_400_BAD_REQUEST)

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

        doctor = User.objects.get(pk=int(data["maBS"]))
        # check license
        if not doctor.is_active:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        date_book = data["ngay"]
        date_book = datetime.strptime(date_book,"%d/%m/%Y")

        today = date.today()

        if date(day=date_book.day,month=date_book.month,year=date_book.year) < today:
            return Response({"alert":"Nhập ngày không hợp lệ!!!"},status=status.HTTP_406_NOT_ACCEPTABLE)
        
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
            