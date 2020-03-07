import os, re
from datetime import datetime

from django.views.generic import ListView
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from dateutil.parser import parse

from .forms import SearchDrugForm, PasswordProtectForm
from .models import Medicine, MedicalHistory
from .serializers import MedicalHistorySerializer
from .bulk_sms import send_sms
from user.models import DoctorProfile, SettingsService, User
from user.license import check_licenses, check_premium_licenses

# count and calculate ultrasonography, endoscopy, medical_test
def count_and_calculate_service(count,settings_service_cost):
    revenue = 0
    if settings_service_cost:
        revenue = count*int(settings_service_cost)
    return revenue

# update list examination patients function
def update_examination_patients_list(doctor,date_book,full_booked):
    histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=True).filter(date_booked__date__lte=date_book).order_by("date_booked")
                    
    html_patients = render_to_string("doctors/doctor_list_patients.html",{"pk_doctor":doctor.pk,"histories":histories,"full_booked":full_booked})

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "patients"+str(doctor.pk),
        {
            "type":"patient_update",
            "html_patients":html_patients,
        }
    )
# update list examination patients finished function
def update_examination_patients_finished_list(doctor,date_book):
    try:
        settings_service = doctor.doctor.settingsservice
    except DoctorProfile.settingsservice.RelatedObjectDoesNotExist:
        settings_service = SettingsService.objects.create(doctor=doctor.doctor)

    histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=False).filter(date_booked__date=date_book).order_by("date_booked")
                    
    html_patients = render_to_string("doctors/doctor_list_patients_finished.html",{"pk_doctor":doctor.pk,"histories":histories,"settings_service":settings_service})

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "patients_finished"+str(doctor.pk),
        {
            "type":"patient_update",
            "html_patients":html_patients,
        }
    )



# check date format dd/mm/Y
def check_date_format(date_string):
    if re.match(r"^([0-2]\d{1}|3[0-1])\/(0\d{1}|1[0-2])\/(19|20)\d{2}$",str(date_string)):
        return bool(parse(date_string))
    return False

# history serializer mix

def history_serializer_mix(data_history,info_day,doctor,date_book,phone):
    
    history_serializer = MedicalHistorySerializer(data=data_history,pk_doctor=doctor.pk)
    if history_serializer.is_valid():
        history=history_serializer.save()
        
        # histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=True).filter(date_booked__date__lte=date_book).order_by("date_booked")

        # update list examination patients
        update_examination_patients_list(doctor,date_book,False)
        
        # call send sms
        send_sms(doctor.doctor.full_name,doctor.pk,info_day.current_patients,history.date_booked,phone)

        
        # html_patients = render_to_string("doctors/doctor_list_patients.html",{"pk_doctor":doctor.pk,"histories":histories,"full_booked":False})

        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     "patients"+str(doctor.pk),
        #     {
        #         "type":"patient_update",
        #         "html_patients":html_patients,
        #     }
        # )

        return Response({
            "soTT":int(info_day.current_patients),
            "ngayKham":history_serializer.data["date_booked"],
            "tenBS":doctor.doctor.full_name
        }, status=status.HTTP_201_CREATED)

    return Response(history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# password protect mixin
def password_protect(request,pk_doctor,template_service,template_protect,context):
    if check_licenses(request):
        return render(request,"user/not_license.html",{})
    user = User.objects.get(pk=pk_doctor)
    settings_service = user.doctor.settingsservice
    error = ""
    if user == request.user:
        if request.method == "POST":
            form = PasswordProtectForm(request.POST)
            if form.is_valid():
                if settings_service.password_field == form.cleaned_data["password"]:
                    return render(request,template_service,context)
                error = "Mật khẩu không hợp lệ."
        context["error"] = error
        return render(request,template_protect,context)

# download medical_ultrasonography file
def download_medical_ultrasonography_file(history):

    file_path = history.medical_ultrasonography_file.path
    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as iv:
            response = HttpResponse(iv.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment;filename=' + \
                re.sub(r".*\/", "",history.medical_ultrasonography_file.name)
            return response
# download endoscopy file
def download_endoscopy_file(history):

    file_path = history.endoscopy_file.path
    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as iv:
            response = HttpResponse(iv.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment;filename=' + \
                re.sub(r".*\/", "",history.endoscopy_file.name)
            return response

weekday_dic ={
    0:"mon",
    1:"tue",
    2:"wed",
    3:"thu",
    4:"fri",
    5:"sat",
    6:"sun"
}

def get_days_detail(weekdays,date_book,examination_period):
    days = weekdays.filter(day=weekday_dic[date_book.weekday()]).order_by("opening_time")
    object_list = []
    if days:
        for day in days:
            time_duration = int((datetime.combine(date_book,day.closing_time) - datetime.combine(date_book,day.opening_time)).total_seconds()//60)
            total_patients = time_duration//int(examination_period)+1

            object_list.append({"time_duration":time_duration,"opening_time":day.opening_time,"closing_time":day.closing_time,"total_patients":total_patients})
    return object_list


def combine_datetime(my_time):
    my_date = datetime.strptime("08/10/1987","%d/%m/%Y")
    return datetime.combine(my_date,my_time)


def weekday_context(weekdays):
    days = {"mon":[],"tue":[],"wed":[],"thu":[],"fri":[],"sat":[],"sun":[]}   
    for day in weekdays:
        if day.day == "mon":
            days["mon"].append(day)
        elif day.day == "tue":
            days["tue"].append(day)
        elif day.day == "wed":
            days["wed"].append(day)
        elif day.day == "thu":
            days["thu"].append(day)
        elif day.day == "fri":
            days["fri"].append(day)
        elif day.day == "sat":
            days["sat"].append(day)
        elif day.day == "sun":
            days["sun"].append(day)
    return days



list_email_manage = ["haphuc87@gmail.com"]

class PageLinksMixin(ListView):
    page_kwarg = "page"

    def _page_urls(self, page_number):
        return "?{pkw}={n}".format(pkw=self.page_kwarg, n=page_number)

    def first_page(self, page):
        if page.number > 1:
            return self._page_urls(1)
        return None

    def last_page(self, page):
        last_page = page.paginator.num_pages
        if page.number < last_page:
            return self._page_urls(last_page)
        return None

    def previous_page(self, page):
        if page.has_previous() and page.number > 2:
            return self._page_urls(page.previous_page_number())
        return None

    def next_page(self, page):
        last_page = page.paginator.num_pages
        if page.has_next() and page.number < (last_page-1):
            return self._page_urls(page.next_page_number())
        return None

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context.get("page_obj")
        # print(dir(page))
        # print(page.paginator.page_range)
        if page is not None:
            context.update({"first_page_url": self.first_page(page), "previous_page_url": self.previous_page(
                page), "next_page_url": self.next_page(page), "last_page_url": self.last_page(page)})
        return context

class DoctorProfileMixin:
    def get(self,request,pk_doctor,*args,**kwargs):
        # check license
        if check_licenses(request):
            return render(request,"user/not_license.html",{})

        doctor = User.objects.get(pk=pk_doctor)
        try:
            doctor.doctor.settingsservice
        except DoctorProfile.settingsservice.RelatedObjectDoesNotExist:
            SettingsService.objects.create(doctor=doctor.doctor)
        
        if doctor == request.user:
            self.object_list = self.get_queryset().filter(doctor=doctor)
            
        # elif self.request.user.email in list_email_manage:
        #     self.object_list = self.get_queryset().filter(doctor=doctor)
        #     doctor = doctor

            page = request.GET.get('page')
            service = request.GET.get('service')
            # if sex=="male":
            #     self.object_list=self.object_list.filter(sex=False)
            #     print("male")
            # elif sex=="female":
            #     self.object_list=self.object_list.filter(sex=True)

            object_list = []
            if service == 'chua_kham':
                for ob in self.object_list:
                    if not ob.medicalhistory_set.all():
                        o = {"ob":ob,"ck":True}
                        object_list.append(o)
            
            elif service == 'san_khoa':
                for ob in self.object_list:
                    o = {"ob":ob,"ps":False,"pk":False}
                    if ob.medicalhistory_set.all():
                        for history in ob.medicalhistory_set.all():
                            if history.service == "khám phụ sản":
                                o['ps']  = True
                            else:
                                o['pk'] = True
                    if o['ps'] and o['pk']:                       
                        object_list.append(o)
            elif service == 'phu_san':
                for ob in self.object_list:
                    if ob.medicalhistory_set.all():
                        for history in ob.medicalhistory_set.all():
                            if history.service == "khám phụ sản":
                                o = {"ob":ob,"ps":True}
                                object_list.append(o)
                                break
                    
            elif service == 'phu_khoa':
                for ob in self.object_list:
                    if ob.medicalhistory_set.all():
                        for history in ob.medicalhistory_set.all():
                            if history.service == "khám phụ khoa":
                                o = {"ob":ob,"pk":True}
                                object_list.append(o)
                                break
                    
            else:

                for ob in self.object_list:
                    o = {"ob":ob}
                    if ob.medicalhistory_set.all():
                        for history in ob.medicalhistory_set.all():
                            if history.service == "khám phụ sản":
                                o['ps']  = True
                            else:
                                o['pk'] = True
                    else:
                        o['ck'] = True
                    object_list.append(o)           

            
            self.object_list = object_list
            

            context = self.get_context_data()
            context.update({"doctor":doctor,"page":page,"service":service})
            
            return self.render_to_response(context)
        
class MedicineMixin:
    # def medicine_list_protect(self,request,context):
    #         return password_protect(request,"doctors/doctor_medicine_list.html","doctors/doctor_medicine_list_protect.html",context)

    def get(self,request,pk_doctor,*args,**kwargs):
        # check premium license
        if check_premium_licenses(request):
            return render(request,"user/not_license.html",{})

        doctor = User.objects.get(pk=pk_doctor)

        if doctor == request.user:
            self.object_list = self.get_queryset().filter(doctor=doctor).order_by("date_expired")

            page = request.GET.get('page')
            order = request.GET.get('order')

            if order == 'desc':
                self.object_list = self.object_list.order_by('-full_name')
            elif order == 'asc':
                self.object_list = self.object_list.order_by('full_name')

            elif order == 'quantity_asc':
                self.object_list = sorted(self.object_list,key=lambda drug: int(drug.quantity))               
            elif order == 'quantity_desc':
                self.object_list = sorted(self.object_list,key=lambda drug: int(drug.quantity),reverse=True)
            
            elif order == 'sale_price_asc':
                self.object_list = sorted(self.object_list,key=lambda drug: int(drug.sale_price))
            elif order == 'sale_price_desc':
                self.object_list = sorted(self.object_list,key=lambda drug: int(drug.sale_price),reverse=True)
            
            elif order == 'import_price_asc':
                self.object_list = sorted(self.object_list,key=lambda drug: int(drug.import_price))
            elif order == 'import_price_desc':
                self.object_list = sorted(self.object_list,key=lambda drug: int(drug.import_price),reverse=True)
            elif order == 'date_expired_asc':
                self.object_list = self.object_list.order_by('date_expired')
            elif order == 'date_expired_desc':
                self.object_list = self.object_list.order_by('-date_expired')
            

            context = self.get_context_data()
            context.update({"doctor":doctor,"page":page,"order":order})

            # if doctor.doctor.settingsservice.password:
            #     return self.medicine_list_protect(request,context)
            return self.render_to_response(context)

        

    def post(self,request,pk_doctor):
        doctor = User.objects.get(pk=pk_doctor)
        if doctor == request.user:
            # check premium license
            if check_premium_licenses(request):
                return render(request,"user/not_license.html",{})

            form = SearchDrugForm(request.POST)
            if form.is_valid():
                search_drug_value = form.cleaned_data["search_drug"]

                drug_results = Medicine.objects.filter(Q(name__icontains=search_drug_value)| Q(full_name__icontains=search_drug_value))

                return render(request,'doctors/doctor_search_drugs.html',{"pk_doctor":pk_doctor,"drug_results":drug_results,"search_drug_value":search_drug_value})


            