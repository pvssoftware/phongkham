import xlsxwriter, xlrd, io, os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta, date
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from user.models import User, DoctorProfile, WeekDay, SettingsTime, SettingsService
from .models import MedicalRecord, MedicalHistory, Medicine, PrescriptionDrug, BookedDay
from .utils import PageLinksMixin, DoctorProfileMixin, MedicineMixin, weekday_context, combine_datetime, get_days_detail, download_medical_ultrasonography_file, download_endoscopy_file, password_protect, check_date_format
from .forms import MedicalHistoryFormMix, SearchDrugForm, TakeDrugForm, UploadMedicineForm,MedicalRecordForm, SearchNavBarForm, MedicineForm, MedicineEditForm, CalculateBenefitForm, SettingsServiceForm, SettingsTimeForm, WeekDayForm, PasswordProtectForm


# merge history search
def merge_history_search(request,pk_doctor,pk_history):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        if request.method == "POST":
            form = SearchNavBarForm(request.POST)
            
            if form.is_valid():
                key_words = form.cleaned_data["search_navbar"]
                results = MedicalRecord.objects.filter(doctor=user,phone__icontains=key_words)

                return render(request,"doctors/doctor_merge_history_search.html",{"results":results,"form":form,"pk_doctor":pk_doctor,"pk_history":pk_history})
        results = {}  
        form = SearchNavBarForm()
        return render(request,"doctors/doctor_merge_history_search.html",{"results":results,"form":form,"pk_doctor":pk_doctor,"pk_history":pk_history})

# merge history confirm
def merge_history_confirm(request,pk_doctor,pk_mrecord,pk_history):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
        pk_mrecord_new = MedicalHistory.objects.get(pk=pk_history).medical_record.pk
        return render(request,"doctors/doctor_merge_history_confirm.html",{"pk_mrecord":pk_mrecord,"pk_mrecord_new":pk_mrecord_new,"pk_doctor":pk_doctor,"pk_history":pk_history,"mrecord":mrecord})
# merge history
def merge_history(request,pk_doctor,pk_mrecord,pk_history):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        history_merge = MedicalHistory.objects.get(pk=pk_history)
        mrecord_new = history_merge.medical_record

        mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
        history_merge.medical_record = mrecord
        history_merge.save()

        mrecord_new.delete()
        return redirect(reverse("final_info",kwargs={"pk_doctor":pk_doctor,"pk_history":pk_history,"pk_mrecord":pk_mrecord}))

# settings services protect

def settings_service_protect(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    return password_protect(request,pk_doctor,"doctors/doctor_settings_service.html","doctors/doctor_settings_service_protect.html",{"doctor":user.doctor})

# settings services

def settings_service(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    
    if user.doctor:
        if request.method == "POST":
            form = SettingsServiceForm(request.POST)
            
            if form.is_valid():
                try:
                    # user.doctor.settingsservice.delete()
                    # form = form.save()
                    # form.doctor = user.doctor
                    # print("try")
                    # form.save()

                    settings_service = user.doctor.settingsservice
                    settings_service.blood_pressure = form.cleaned_data["blood_pressure"]
                    settings_service.weight = form.cleaned_data["weight"]
                    settings_service.glycemic = form.cleaned_data["glycemic"]
                    settings_service.ph_meter = form.cleaned_data["ph_meter"]
                    settings_service.medical_ultrasonography = form.cleaned_data["medical_ultrasonography"]
                    settings_service.medical_ultrasonography_cost = form.cleaned_data["medical_ultrasonography_cost"]
                    settings_service.endoscopy = form.cleaned_data["endoscopy"]
                    settings_service.endoscopy_cost = form.cleaned_data["endoscopy_cost"]
                    settings_service.password = form.cleaned_data["password"]
                    settings_service.password_field = form.cleaned_data["password_field"]

                    settings_service.save()
                except DoctorProfile.settingsservice.RelatedObjectDoesNotExist:
                    form = form.save()
                    form.doctor = user.doctor
                    print("except")
                    form.save()
                return render(request,"doctors/doctor_settings_service.html",{"doctor":user.doctor})
        if user.doctor.settingsservice.password:
            return redirect(reverse("settings_service_protect",kwargs={"pk_doctor":pk_doctor}))
        return render(request,"doctors/doctor_settings_service.html",{"doctor":user.doctor})

# settings opening time
def settings_openingtime(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        if request.method == "POST":
            form = SettingsTimeForm(request.POST)
            
            if form.is_valid():                
                try:                    
                    settings_time = user.doctor.settings_time
                    # form = form.save()
                    settings_time.examination_period = form.cleaned_data["examination_period"]
                    settings_time.enable_voice = form.cleaned_data["enable_voice"]
                    # form.doctor = user.doctor
                    print("try")
                    # form.save()
                    settings_time.save()
                except DoctorProfile.settings_time.RelatedObjectDoesNotExist:
                    form = form.save()
                    form.doctor = user.doctor
                    print("except")
                    form.save()

                
                weekdays = user.doctor.settings_time.weekday_set.all()
                days = weekday_context(weekdays)

                return render(request,"doctors/doctor_settings_openingtime.html",{"doctor":user.doctor,"days":days})
        try:
            weekdays = user.doctor.settings_time.weekday_set.all().order_by("opening_time")
            days = weekday_context(weekdays)
        except DoctorProfile.settings_time.RelatedObjectDoesNotExist:
            days = {}
        return render(request,"doctors/doctor_settings_openingtime.html",{"doctor":user.doctor,"days":days})

# create weekday
def create_weekday(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        if request.method == "POST":
            form = WeekDayForm(request.POST)
            
            if form.is_valid():
                
                settings_time = user.doctor.settings_time
                
                valid = True
                if settings_time.weekday_set.all():
                    for day in settings_time.weekday_set.all():
                        if day.day == form.cleaned_data['day']:
                            if not ((combine_datetime(form.cleaned_data["opening_time"]) < combine_datetime(day.opening_time) and combine_datetime(form.cleaned_data["closing_time"]) < combine_datetime(day.opening_time)) or (combine_datetime(form.cleaned_data["opening_time"]) > combine_datetime(day.closing_time) and combine_datetime(form.cleaned_data["closing_time"]) > combine_datetime(day.closing_time))):
                                valid = False
                if valid:
                    form = form.save(commit=False)
                    form.settingstime = settings_time
                    form.save()
                    return redirect(reverse('settings_openingtime',kwargs={'pk_doctor':pk_doctor}))
                else:
                    return render(request,"doctors/doctor_create_weekday.html",{"doctor":user.doctor,"form":form})

        return render(request,"doctors/doctor_create_weekday.html",{"doctor":user.doctor,"form":[]})

# delete weekday
def delete_weekday(request,pk_doctor,pk_weekday):
    user = User.objects.get(pk=pk_doctor)
    day = WeekDay.objects.get(pk=pk_weekday)
    if user == request.user:
        day.delete()
        return redirect(reverse('settings_openingtime',kwargs={'pk_doctor':pk_doctor}))


# calculate benefit protect

def cal_benefit_protect(request,pk_doctor):
    form = CalculateBenefitForm()

    return password_protect(request,pk_doctor,'doctors/doctor_cal_benefit.html','doctors/doctor_cal_benefit_protect.html',{"pk_doctor":pk_doctor,"form":form})

# calculate benefit

def cal_benefit(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        form = CalculateBenefitForm(request.GET)
        if form.is_valid():
            
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            histories = MedicalHistory.objects.filter(medical_record__doctor = user).filter(date__gte=from_date).filter(date__lte=to_date+timedelta(days=1))
            histories_object = []
            gross_revenue = 0
            accrued_expenses = 0
            for history in histories:
                his = {"history":history,"revenue":0,"expense":0,"benefit":0}
                if history.prescriptiondrug_set.all():
                    for pres_drug in history.prescriptiondrug_set.all():
                        gross_revenue += int(pres_drug.cost)
                        accrued_expenses += int(pres_drug.quantity)*int(pres_drug.medicine.import_price)
                        his['revenue'] += int(pres_drug.cost)
                        his['expense'] += int(pres_drug.quantity)*int(pres_drug.medicine.import_price)
                    his['benefit'] = his['revenue'] - his['expense']

                histories_object.append(his)
            gross_profit = gross_revenue - accrued_expenses
            return render(request,'doctors/doctor_cal_benefit.html',{"histories_object":histories_object,"gross_revenue":gross_revenue,"accrued_expense":accrued_expenses,"gross_profit":gross_profit,"pk_doctor":pk_doctor,"form":form})
        else:
            if user.doctor.settingsservice.password:
                return redirect(reverse("cal_benefit_protect",kwargs={"pk_doctor":pk_doctor}))
            form = CalculateBenefitForm()
            return render(request,'doctors/doctor_cal_benefit.html',{"pk_doctor":pk_doctor,"form":form})




# search on navbar

def search_navbar(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        form = SearchNavBarForm(request.GET)
        if form.is_valid():
            search_value = form.cleaned_data['search_navbar']

            try:
                results = []
                date_obj = datetime.strptime(search_value,'%d/%m/%Y')
                mrecords = MedicalRecord.objects.filter(doctor=user)
                if mrecords.count() > 0:
                    for mrecord in mrecords:
                        if mrecord.medicalhistory_set.all().filter(date__date=date_obj):
                            results.append(mrecord)
            except ValueError:
                results = MedicalRecord.objects.filter(Q(doctor=user),Q (full_name__icontains=form.cleaned_data['search_navbar']))
                
            object_list = []
            for ob in results:
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
            results = object_list

            return render(request,'doctors/doctor_search_navbar.html',{"results":results,"pk_doctor":pk_doctor})


# medicine list protect
# def medicine_list_protect(request,pk_doctor,context):
#     return password_protect(request,"doctors/doctor_medicine_list.html","doctors/doctor_medicine_list_protect.html",context)
# Medicine List view
class MedicineList(MedicineMixin,PageLinksMixin):
    model = Medicine
    template_name = 'doctors/doctor_medicine_list.html'
    paginate_by = 10

# Search medicine
def search_drugs(request,pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        form = SearchDrugForm(request.GET)
        if form.is_valid():

            search_drug_value = form.cleaned_data["search_drug"]

            drug_results = Medicine.objects.filter(Q(name__icontains=search_drug_value)| Q(full_name__icontains=search_drug_value))

            return render(request,'doctors/doctor_search_drugs.html',{"pk_doctor":pk_doctor,"drug_results":drug_results,"search_drug_value":search_drug_value})

# Medicine create view
def medicine_create(request,pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        form_upload_excel = UploadMedicineForm()
        if request.method == "POST":
            form = MedicineForm(request.POST)
            
            if form.is_valid():
                full_name = form.cleaned_data['full_name']
                
                try:
                    Medicine.objects.filter(doctor=doctor).get(full_name__iexact=full_name)
                    error = True

                    # form = MedicineForm(initial={"name":form.cleaned_data['name'],'full_name':form.cleaned_data['full_name'],'sale_price':form.cleaned_data['sale_price'],'import_price':form.cleaned_data['import_price'],'quantity':form.cleaned_data['quantity']})

                    return render(request,'doctors/doctor_medicine_create.html',{'form':form, "form_upload_excel":form_upload_excel,'pk_doctor':pk_doctor,"error":error})
                except:

                    form = form.save(commit=False)
                    form.doctor = doctor
                    form.save()
                    return redirect(reverse('medicine_list',kwargs={'pk_doctor':pk_doctor}))
        else:
            form = MedicineForm()
            return render(request,'doctors/doctor_medicine_create.html',{'form':form, "form_upload_excel":form_upload_excel,'pk_doctor':pk_doctor})

# Medicine edit view
def medicine_edit(request,pk_doctor,pk_medicine):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        medicine = Medicine.objects.get(pk=pk_medicine)
        if request.method == "POST":
            form = MedicineEditForm(request.POST)
            if form.is_valid():
                
                all_medicine = Medicine.objects.filter(doctor=doctor).exclude(pk=pk_medicine)

                try:
                    all_medicine.get(full_name__iexact=form.cleaned_data['full_name'])
                    error = True

                    return render(request,'doctors/doctor_medicine_edit.html',{'form':form,'pk_doctor':pk_doctor,'pk_medicine':pk_medicine, "error":error,"medicine":medicine})
                except:

                    medicine.name = form.cleaned_data['name']
                    medicine.full_name = form.cleaned_data['full_name']
                    medicine.sale_price = form.cleaned_data['sale_price']
                    medicine.import_price = form.cleaned_data['import_price']
                    medicine.date_expired = form.cleaned_data['date_expired']
                    if form.cleaned_data['add_quantity']:
                        medicine.quantity = str(int(form.cleaned_data['add_quantity'])+int(medicine.quantity))
                    medicine.save()

                return redirect(reverse('medicine_edit',kwargs={'pk_doctor':pk_doctor,'pk_medicine':pk_medicine}))
        else:
            date_expired = lambda x: x.strftime("%d/%m/%Y") if (x) else ""
            form = MedicineEditForm(initial={"name":medicine.name,'full_name':medicine.full_name,'sale_price':medicine.sale_price,'import_price':medicine.import_price,'date_expired':date_expired(medicine.date_expired)})
            return render(request,'doctors/doctor_medicine_edit.html',{'form':form,'pk_doctor':pk_doctor,'pk_medicine':pk_medicine,"medicine":medicine})

# Medicine del view
def medicine_del(request,pk_doctor,pk_medicine):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        medicine_del = Medicine.objects.get(pk=pk_medicine)
        medicine_del.delete()

        return redirect(reverse('medicine_list',kwargs={'pk_doctor':pk_doctor}))

# upload medicine from excel file
def upload_medicine_excel(request,pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        if request.method == "POST":
            form = UploadMedicineForm(request.POST,request.FILES)
            if form.is_valid():
                file_excel = form.cleaned_data['file_excel']

                wb = xlrd.open_workbook(filename=None,file_contents = file_excel.read())

                # number of sheets
                sheets = wb.nsheets
                data_error = []
                for s in range(sheets):
                    # get sheets by index
                    sheet = wb.sheet_by_index(s)
                    # number of rows and columns
                    num_rows = sheet.nrows
                    num_columns = sheet.ncols
                    
                    for r in range(1,num_rows):
                        row = []
                        
                        for c in range(num_columns):
                            row.append(sheet.cell(r,c).value)
                        
                        if (type(row[2])==str or row[2]=="") or (type(row[3])==str or row[3]=="") or (type(row[4])==str or row[4]==0 or row[4]=="") or not check_date_format(row[5]):
                            data_error.append(row)
                            continue
                        
                        row[2] = int(row[2]) 
                        row[3] = int(row[3]) 
                        row[4] = int(row[4]) 

                        try:
                            medicine = Medicine.objects.get(full_name__iexact=str(row[1]),doctor=doctor)
                            medicine.name = str(row[0])
                            medicine.sale_price = str(row[2])
                            medicine.import_price = str(row[3])
                            medicine.quantity = str(row[4])
                            medicine.date_expired = datetime.strptime(row[5],"%d/%m/%Y").strftime("%Y-%m-%d")
                            medicine.save()
                        except:
                            Medicine.objects.create(name=str(row[0]),full_name=str(row[1]),sale_price=str(row[2]),import_price=str(row[3]),quantity=str(row[4]),date_expired = datetime.strptime(row[5],"%d/%m/%Y").strftime("%Y-%m-%d") ,doctor=doctor)

                if data_error:
                    return render(request,'doctors/doctor_alert_upload.html',{"pk_doctor":pk_doctor,"data_error":data_error})
                return redirect(reverse("medicine_list",kwargs={"pk_doctor":pk_doctor}))

        # form = UploadMedicineForm()
        # return render(request,'doctors/doctor_upload_medicine_excel.html',{"pk_doctor":pk_doctor,'form':form})





# doctor profile view
class DoctorProfileView(DoctorProfileMixin,PageLinksMixin):
    model = MedicalRecord
    template_name = 'doctors/doctor_profile.html'
    paginate_by = 7

#  Medical Record create view
def medical_record_create(request,pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)

    if doctor == request.user:
        if request.method == "POST":
            form = MedicalRecordForm(request.POST,doctor=doctor)
            print(form)
            if form.is_valid():
                form = form.save(commit=False)
                # form.birth_date = datetime.strptime(form.birth_date,'%d/%m/%Y')
                
                form.doctor = doctor
                form.save()

                return redirect(reverse("medical_record_view",kwargs={"pk_doctor":pk_doctor,"pk_mrecord":form.id}))
            else:
                return render(request,'doctors/doctor_medical_record_create.html',{"form":form,'pk_doctor':pk_doctor})
        else:
            form = MedicalRecordForm()
            return render(request,'doctors/doctor_medical_record_create.html',{"form":form,'pk_doctor':pk_doctor})

# Medical record edit view
def medical_record_edit(request,pk_doctor,pk_mrecord):
    doctor = User.objects.get(pk=pk_doctor)

    if doctor == request.user:
        mrecord  = MedicalRecord.objects.get(pk=pk_mrecord)
        if request.method == "POST":
            form = MedicalRecordForm(request.POST,doctor=doctor,pk_mrecord=pk_mrecord)
            if form.is_valid():
                
                form = form.save(commit=False)
                # print(form.cleaned_data['sex'])
                
                mrecord.full_name = form.full_name
                mrecord.birth_date = form.birth_date
                mrecord.address = form.address
                mrecord.sex = form.sex
                mrecord.phone = form.phone
                
                mrecord.save()
                return redirect(reverse('medical_record_view',kwargs={"pk_doctor":pk_doctor,"pk_mrecord":pk_mrecord}))
            else:
                return render(request,"doctors/doctor_medical_record_edit.html",{"form":form,"pk_doctor":pk_doctor,"mrecord":mrecord})
        else:
            form = MedicalRecordForm(initial={"full_name":mrecord.full_name,"birth_date":mrecord.birth_date.year,"address":mrecord.address,"phone":mrecord.phone})
            return render(request,"doctors/doctor_medical_record_edit.html",{"form":form,"pk_doctor":pk_doctor,"mrecord":mrecord})
# Medical record edit back history view
def medical_record_edit_back_history(request,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)

    if doctor == request.user:
        mrecord  = MedicalRecord.objects.get(pk=pk_mrecord)
        if request.method == "POST":
            form = MedicalRecordForm(request.POST,doctor=doctor,pk_mrecord=pk_mrecord)
            print(form)
            if form.is_valid():
                
                form = form.save(commit=False)
                
                mrecord.full_name = form.full_name
                mrecord.birth_date = form.birth_date
                mrecord.address = form.address
                mrecord.sex = form.sex
                mrecord.phone = form.phone
                
                mrecord.save()
                return redirect(reverse('medical_record_back_view',kwargs={"pk_doctor":pk_doctor,"pk_mrecord":pk_mrecord,"pk_history":pk_history}))
            else:
                return render(request,"doctors/doctor_medical_record_edit_back_history.html",{"form":form,"pk_doctor":pk_doctor,"mrecord":mrecord,"pk_history":pk_history})
        else:
            birth_date = lambda x: x.year if (x) else ""
            form = MedicalRecordForm(initial={"full_name":mrecord.full_name,"birth_date":birth_date(mrecord.birth_date),"address":mrecord.address,"phone":mrecord.phone})
            return render(request,"doctors/doctor_medical_record_edit_back_history.html",{"form":form,"pk_doctor":pk_doctor,"mrecord":mrecord,"pk_history":pk_history})



# Medical record delete view
def medical_record_del(request,pk_doctor,pk_mrecord):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        mrecord_del = MedicalRecord.objects.get(pk=pk_mrecord)
        mrecord_del.delete()
        return redirect(reverse("doctor_profile",kwargs={"pk_doctor":pk_doctor}))


# Medical record view
def medical_record_view(request, pk_mrecord, pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)

    if request.user == doctor:
        mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
        try:
            settings_time = doctor.doctor.settings_time
        except:
            settings_time = SettingsTime.objects.create(examination_period="0",doctor=doctor.doctor)
        if request.method == "POST":
            form = MedicalHistoryFormMix(request.POST,request.FILES)
            if form.is_valid():
                form = form.save(commit=False)
                form.medical_record = mrecord

                if form.is_waiting:
                    # form.is_waiting = True
                    today = date.today()
                        
                    date_book = date(year=today.year,month=today.month,day=today.day)
                    
                    if settings_time.enable_voice:

                        days_detail = get_days_detail(settings_time.weekday_set.all(),date_book,settings_time.examination_period)

                        if not days_detail:
                            return render(request,"doctors/doctor_not_setting_opening_day.html",{"weekday":date_book.weekday(),"pk_mrecord":pk_mrecord,"pk_doctor":pk_doctor})

                        total_patients = 0
                        for day_detail in days_detail:
                            total_patients += day_detail["total_patients"]
                            closing_time = day_detail["closing_time"]

                        try:
                            info_bookedday = BookedDay.objects.get(doctor=doctor.doctor,date=date_book)
                            info_bookedday.max_patients = total_patients
                            info_bookedday.save()
                            if int(info_bookedday.current_patients) < int(info_bookedday.max_patients):
                                full_booked = False
                                total_patients_prevday = 0
                                for day_detail in days_detail:
                                    if int(info_bookedday.current_patients) < (day_detail["total_patients"]+total_patients_prevday):
                                        info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                                        info_bookedday.save()

                                        datetime_book = datetime.combine(date_book,day_detail["opening_time"]) + timedelta(minutes=(int(info_bookedday.current_patients)-total_patients_prevday-1)*int(doctor.doctor.settings_time.examination_period))
                                        break
                                    else:
                                        total_patients_prevday += day_detail["total_patients"]
                                    
                            else:
                                full_booked = True

                                info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                                info_bookedday.save()

                                datetime_book = datetime.combine(date_book,closing_time) + timedelta(minutes=(int(info_bookedday.current_patients)- int(info_bookedday.max_patients))*int(doctor.doctor.settings_time.examination_period))
                                print("max")
                            
                            form.date_booked = datetime_book
                            form.ordinal_number = info_bookedday.current_patients
                            form.save()

                        except ObjectDoesNotExist:
                            full_booked = False

                            BookedDay.objects.create(doctor=doctor.doctor,date=date_book,max_patients=str(total_patients),current_patients="1")
                            datetime_book = datetime.combine(date_book,days_detail[0]["opening_time"])

                            form.date_booked = datetime_book
                            form.ordinal_number = '1'
                            form.save()
                    else:
                        full_booked = False
                        try:
                            info_bookedday = BookedDay.objects.get(doctor=doctor.doctor,date=date_book)
                            info_bookedday.current_patients = str(int(info_bookedday.current_patients) + 1)
                            info_bookedday.save()
                            
                        except ObjectDoesNotExist:
                            info_bookedday = BookedDay.objects.create(doctor=doctor.doctor,date=date_book,max_patients="limitless",current_patients="1")

                        form.date_booked = datetime.now()
                        form.ordinal_number = info_bookedday.current_patients
                        form.save()
                        


                    histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=True).filter(date_booked__date__lte=date_book).order_by("date_booked")
                    
                    html_patients = render_to_string("doctors/doctor_list_patients.html",{"pk_doctor":pk_doctor,"histories":histories,"full_booked":full_booked})

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "patients"+str(pk_doctor),
                        {
                            "type":"patient_update",
                            "html_patients":html_patients,
                        }
                    )

                    return redirect(reverse("list_examination",kwargs={"pk_doctor": pk_doctor}))
                else:
                    # form.is_waiting = False
                    if form.service == 'khám phụ khoa':
                        # if form.cleaned_data['co_tu_cung_pk']:
                        #     form.co_tu_cung_pk = True
                        # if form.cleaned_data['am_dao_pk']:
                        #     form.am_dao_pk = True
                        # if form.cleaned_data['chuan_doan_khac_pk']:
                        #     form.chuan_doan_khac_pk = True
                        form.co_tu_cung_ps = False
                        form.note_co_tu_cung_ps = ''
                        form.tim_thai_ps = False
                        form.note_tim_thai_ps = ''
                        form.can_go_ps = False
                        form.note_con_go_ps = ''

                    else:
                        # if form.cleaned_data['co_tu_cung_ps']:
                        #     form.co_tu_cung_ps = True
                        # if form.cleaned_data['tim_thai_ps']:
                        #     form.tim_thai_ps = True
                        # if form.cleaned_data['can_go_ps']:
                        #     form.can_go_ps = True
                        form.co_tu_cung_pk = False
                        form.note_co_tu_cung_pk = ''
                        form.am_dao_pk = False
                        form.note_am_dao_pk = ''
                        
                    
                    form.date_booked = datetime.now()
                    form.save()
                # history = MedicalHistory.objects.create(disease_symptom=disease_symptom,diagnostis=diagnostis,
                # service=service,service_detail=service_detail,PARA=PARA,contraceptive=contraceptive,last_menstrual_period=last_menstrual_period,note=note,medical_record = mrecord,co_tu_cung_pk=co_tu_cung_pk,am_dao_pk=am_dao_pk,chuan_doan_khac_pk=chuan_doan_khac_pk,co_tu_cung_ps=co_tu_cung_ps,tim_thai_ps=tim_thai_ps,can_go_ps=can_go_ps)

                    return redirect(reverse("prescription_drug", kwargs={"pk_doctor": pk_doctor, "pk_mrecord": pk_mrecord, "pk_history": form.pk}))
            else:
                return render(request,"doctors/doctor_errors_file_upload.html",{"form":form})
        else:
            try:
                settings_service = doctor.doctor.settingsservice
            except:
                settings_service = SettingsService.objects.create(doctor=doctor.doctor)
            form = MedicalHistoryFormMix()
            return render(request, "doctors/doctor_medical_record.html", {"mrecord": mrecord, "doctor": doctor, "form": form,"settings_service":settings_service})

# Medical record back view


def medical_record_back_view(request, pk_mrecord, pk_doctor, pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        if request.method == "POST":
            form = MedicalHistoryFormMix(request.POST,request.FILES)
            if form.is_valid():
                history_edit = MedicalHistory.objects.get(pk=pk_history)

                history_edit.disease_symptom = form.cleaned_data["disease_symptom"]
                history_edit.diagnostis =form.cleaned_data["diagnostis"]
                history_edit.service = form.cleaned_data['service']
                history_edit.is_waiting = form.cleaned_data['is_waiting']
                
                if form.cleaned_data['service']== 'khám phụ khoa':
                    if form.cleaned_data['co_tu_cung_pk']:
                        history_edit.co_tu_cung_pk = True
                        history_edit.note_co_tu_cung_pk = form.cleaned_data['note_co_tu_cung_pk']
                    else:
                        history_edit.co_tu_cung_pk = False
                        history_edit.note_co_tu_cung_pk = ''
                    if form.cleaned_data['am_dao_pk']:
                        history_edit.am_dao_pk = True
                        history_edit.note_am_dao_pk = form.cleaned_data['note_am_dao_pk']
                    else:
                        history_edit.am_dao_pk = False
                        history_edit.note_am_dao_pk = ''

                    history_edit.co_tu_cung_ps = False
                    history_edit.note_co_tu_cung_ps = ''
                    history_edit.tim_thai_ps = False
                    history_edit.note_tim_thai_ps = ''
                    history_edit.can_go_ps = False
                    history_edit.note_con_go_ps = ''
                else:
                    if form.cleaned_data['co_tu_cung_ps']:
                        history_edit.co_tu_cung_ps = True
                        history_edit.note_co_tu_cung_ps = form.cleaned_data['note_co_tu_cung_ps']
                    else:
                        history_edit.co_tu_cung_ps = False
                        history_edit.note_co_tu_cung_ps = ''
                    if form.cleaned_data['tim_thai_ps']:
                        history_edit.tim_thai_ps = True
                        history_edit.note_tim_thai_ps = form.cleaned_data['note_tim_thai_ps']
                    else:
                        history_edit.tim_thai_ps = False
                        history_edit.note_tim_thai_ps = ''
                    if form.cleaned_data['can_go_ps']:
                        history_edit.can_go_ps = True
                        history_edit.note_con_go_ps = form.cleaned_data['note_con_go_ps']
                    else:
                        history_edit.can_go_ps = False
                        history_edit.note_can_go_ps = ''

                    history_edit.co_tu_cung_pk = False
                    history_edit.note_co_tu_cung_pk = ''
                    history_edit.am_dao_pk = False
                    history_edit.note_am_dao_pk = ''
                    


                history_edit.PARA = form.cleaned_data['PARA']
                history_edit.contraceptive = form.cleaned_data['contraceptive']
                history_edit.last_menstrual_period = form.cleaned_data['last_menstrual_period']
                history_edit.blood_pressure = form.cleaned_data['blood_pressure']
                history_edit.weight = form.cleaned_data['weight']
                history_edit.glycemic = form.cleaned_data['glycemic']
                history_edit.ph_meter = form.cleaned_data['ph_meter']

                history_edit.medical_ultrasonography = form.cleaned_data['medical_ultrasonography']
                if "medical_ultrasonography_file" in request.FILES:
                    if history_edit.medical_ultrasonography_file:
                        try:
                            os.remove(history_edit.medical_ultrasonography_file.path)
                        except FileNotFoundError:
                            pass 
                    history_edit.medical_ultrasonography_file = request.FILES["medical_ultrasonography_file"]

                history_edit.endoscopy = form.cleaned_data['endoscopy']
                if "endoscopy_file" in request.FILES:
                    if history_edit.endoscopy_file:
                        try:
                            os.remove(history_edit.endoscopy_file.path)
                        except FileNotFoundError:
                            pass
                    history_edit.endoscopy_file = request.FILES["endoscopy_file"]
                
                history_edit.save()

                if history_edit.is_waiting:
                    return redirect(reverse("list_examination",kwargs={"pk_doctor": pk_doctor}))

                histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=True).filter(date_booked__date__lte=date.today()).order_by("date_booked")
                html_patients = render_to_string("doctors/doctor_list_patients.html",{"pk_doctor":pk_doctor,"histories":histories})

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "patients"+str(pk_doctor),
                    {
                        "type":"patient_update",
                        "html_patients":html_patients,
                    }
                )

                return redirect(reverse("prescription_drug", kwargs={"pk_doctor": pk_doctor, "pk_mrecord": pk_mrecord, "pk_history": history_edit.pk}))
            else:
                # return HttpResponse("<h1>File upload của bạn trên 5M. Làm ơn chọn file dưới 5M!</h1>")
                return render(request,"doctors/doctor_errors_file_upload.html",{"form":form})

        else:
            mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
            history_edit = MedicalHistory.objects.get(pk=pk_history)
            last_menstrual_period = lambda x: x.strftime("%d/%m/%Y") if (x) else ""
            
            histories = mrecord.medicalhistory_set.exclude(pk=pk_history)
            settings_service = doctor.doctor.settingsservice
            form = MedicalHistoryFormMix(initial={
                                    "disease_symptom": history_edit.disease_symptom, "diagnostis": history_edit.diagnostis,"service":history_edit.service,"PARA":history_edit.PARA,"contraceptive":history_edit.contraceptive,"last_menstrual_period":last_menstrual_period(history_edit.last_menstrual_period)})
            
            return render(request, 'doctors/doctor_medical_record_back_view.html', {"histories": histories, "history_edit": history_edit, "form": form,"mrecord":mrecord,"doctor":doctor,"settings_service":settings_service})

# List examination
def list_examination(request,pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)
    histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=True).filter(date_booked__date__lte=date.today()).order_by("date_booked")

    return render(request,"doctors/doctor_list_examination.html",{"pk_doctor":pk_doctor,"histories":histories,"full_booked":False})

# download medical_ultrasonography file
def download_medical_ultrasonography(request,pk_doctor,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        history = MedicalHistory.objects.get(pk=pk_history)
        return download_medical_ultrasonography_file(history)
        
# download endoscopy file
def download_endoscopy(request,pk_doctor,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        history = MedicalHistory.objects.get(pk=pk_history)
        return download_endoscopy_file(history)


# Delete history medical 

def medical_history_del(request,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        settings_time = doctor.doctor.settings_time
        history_del = MedicalHistory.objects.get(pk=pk_history)
        date_book = history_del.date.date()
        is_waiting = history_del.is_waiting
        drugs_history_del = history_del.prescriptiondrug_set.all()
        for drug in drugs_history_del:
            drug.medicine.quantity = str(int(drug.medicine.quantity)+ int(drug.quantity))
            drug.medicine.save()
        history_del.delete()
        if is_waiting:
            if settings_time.enable_voice:
                try:
                    info_bookedday = BookedDay.objects.get(doctor=doctor.doctor,date=date_book)
                    info_bookedday.current_patients = str(int(info_bookedday.current_patients) - 1)
                    info_bookedday.save()
                except ObjectDoesNotExist:
                    pass

            histories = MedicalHistory.objects.filter(medical_record__doctor=doctor,is_waiting=True).filter(date_booked__date__lte=date.today())
            html_patients = render_to_string("doctors/doctor_list_patients.html",{"pk_doctor":pk_doctor,"histories":histories})

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "patients"+str(pk_doctor),
                {
                    "type":"patient_update",
                    "html_patients":html_patients,
                }
            )
            
            return redirect(reverse("list_examination",kwargs={"pk_doctor": pk_doctor}))
        else:
            return redirect(reverse("medical_record_view",kwargs={"pk_doctor":pk_doctor,"pk_mrecord":pk_mrecord}))

# Prescription Drug view
def prescription_drug(request, pk_doctor, pk_mrecord, pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        history = MedicalHistory.objects.get(pk=pk_history)
        medicine_list = Medicine.objects.filter(doctor=doctor)
        
        return render(request, "doctors/doctor_prescription.html", {"pk_doctor": pk_doctor, "pk_mrecord": pk_mrecord, "pk_history": pk_history,"history":history,"medicine_list":medicine_list})

# Take drug to prescription view

def take_drug(request,pk_doctor,pk_mrecord,pk_history,pk_drug):
    
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        drug = Medicine.objects.get(pk=pk_drug)
        if request.method == "POST":
            form = TakeDrugForm(request.POST)
            if form.is_valid():
                history = MedicalHistory.objects.get(pk=pk_history)
                form = form.save(commit=False)

                duplicate = False
                for pres_drug in history.prescriptiondrug_set.all():
                    if pres_drug.medicine == drug:
                        if int(form.quantity) >= int(drug.quantity):
                            pres_drug.quantity = str(int(pres_drug.quantity)+int(drug.quantity))
                            drug.quantity = "0"
                        else:
                            pres_drug.quantity = str(int(pres_drug.quantity)+int(form.quantity))
                            drug.quantity = str(int(drug.quantity) - int(form.quantity))
                        pres_drug.time_take_medicine = form.time_take_medicine
                        pres_drug.dose = form.dose
                        
                        pres_drug.save()
                        drug.save()
                        duplicate = True
                        break
                
                if not duplicate:
                    if int(form.quantity) >= int(drug.quantity):
                        form.quantity = drug.quantity
                        drug.quantity = "0"
                    else:
                        drug.quantity = str(int(drug.quantity) - int(form.quantity))
                    form.cost = str(int(drug.sale_price)*int(form.quantity))
                    
                    form.medical_history = history
                    form.medicine = drug

                    form.save()

                    form.medicine.save()

                return redirect(reverse("prescription_drug", kwargs={"pk_doctor": pk_doctor, "pk_mrecord": pk_mrecord, "pk_history": pk_history}))

        return render(request,'doctors/doctor_take_drug.html',{"drug":drug,"pk_doctor":pk_doctor,"pk_history":pk_history, "pk_mrecord":pk_mrecord})
#  remove drug out of prescription drug

def remove_drug(request,pk_prescriptiondrug,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        prescription_drug = PrescriptionDrug.objects.get(pk=pk_prescriptiondrug)

        prescription_drug.medicine.quantity = str(int(prescription_drug.medicine.quantity) + int(prescription_drug.quantity))
        prescription_drug.medicine.save()

        prescription_drug.delete()

        return redirect(reverse("prescription_drug",kwargs={"pk_doctor":pk_doctor,"pk_mrecord":pk_mrecord,"pk_history":pk_history}))

# final table infomation view
def final_info(request,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
        history = MedicalHistory.objects.get(pk=pk_history)
        settings_service = doctor.doctor.settingsservice
        total_cost = 0
        for drug in history.prescriptiondrug_set.all():
            total_cost += int(drug.cost)

        return render(request,'doctors/doctor_final_info.html',{"doctor":doctor,"mrecord":mrecord,"history":history,"total_cost":total_cost,"settings_service":settings_service})

# export to excel file
def export_final_info_excel(request,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
        history = MedicalHistory.objects.get(pk=pk_history)
        settings_service = doctor.doctor.settingsservice
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output,{'remove_timezone': True})

        ws = wb.add_worksheet("Bệnh nhân")
        ws.fit_to_pages(1,1)
        ws.set_paper(11)

        ws1 = wb.add_worksheet("Bác sĩ")
        ws1.fit_to_pages(1,1)
        ws1.set_paper(11)

        # set row disease_symptom and dianostis
        # ws.set_row(8,50)
        # ws.set_row(9,50)
        
        # format 
        header_style = wb.add_format({"bold":True,"font_name":'Times New Roman','font_size':15, 'bold':True,'text_wrap':True,"valign":"vcenter"})
        normal_style = wb.add_format({"font_name":'Times New Roman','font_size':13,'text_wrap':True,"valign":"vcenter"})
        number_style = wb.add_format({"font_name":'Times New Roman','font_size':13,"border":1,'text_wrap':True,"align":"center","valign":"vcenter","num_format":'#,##0 ;[Red]General'})

        # information doctor at worksheet patient #
        ws.merge_range('A2:K2',"Phòng Khám "+(doctor.doctor.get_kind_display()).upper()+" - "+doctor.doctor.full_name.upper(),header_style)
        ws.merge_range("A3:K3","Địa chỉ: "+doctor.doctor.clinic_address,normal_style)
        ws.merge_range("A4:I4","Điện thoại đăng ký khám bệnh: "+doctor.doctor.phone,normal_style)
        # information doctor at worksheet doctor #
        ws1.merge_range('A2:I2',"Phòng Khám "+(doctor.doctor.get_kind_display()).upper()+" - "+doctor.doctor.full_name.upper(),header_style)
        ws1.merge_range("A3:K3","Địa chỉ: "+doctor.doctor.clinic_address,normal_style)
        ws1.merge_range("A4:I4","Điện thoại đăng ký khám bệnh: "+doctor.doctor.phone,normal_style)


        # artical at worksheet patient #
        ws.merge_range("E6:F6","TOA THUỐC",header_style)
        # artical at worksheet doctor #
        ws1.merge_range("E6:F6","TOA THUỐC",header_style)

        # information patient at worksheet patient #
        ws.merge_range("A9:G9","Họ và tên: "+mrecord.full_name.upper(),header_style)
        ws.merge_range("I9:K9","Năm sinh: "+str(mrecord.birth_date.year),header_style)
        ws.merge_range("A11:H11","Địa chỉ: "+mrecord.address,normal_style)
        ws.merge_range("A12:H12","Chẩn đoán: "+history.diagnostis,normal_style)
        # information patient at worksheet doctor #
        ws1.merge_range("A9:G9","Họ và tên: "+mrecord.full_name.upper(),header_style)
        ws1.merge_range("I9:K9","Năm sinh: "+str(mrecord.birth_date.year),header_style)
        ws1.merge_range("A11:H11","Địa chỉ: "+mrecord.address,normal_style)
        ws1.merge_range("A12:H12","Chẩn đoán: "+history.diagnostis,normal_style)

        # information prescription drug worksheet patient #
        ws.merge_range("A13:G13","Chỉ định dùng thuốc:",normal_style)

        row_drug = 14
        total_cost = 0
        index = 1

        for drug in history.prescriptiondrug_set.all():
            ws.merge_range("B{}:F{}".format(str(row_drug),str(row_drug)),str(index)+". "+drug.medicine.full_name,header_style)
            ws.merge_range("J{}:K{}".format(str(row_drug),str(row_drug)),drug.quantity+" viên",normal_style)
            index += 1

            ws.merge_range("C{}:K{}".format(str(row_drug+1),str(row_drug+1)),"Mỗi lần "+drug.dose+" viên"+", "+drug.time_take_medicine,normal_style)
            row_drug += 2
            total_cost += int(drug.cost)
        # information prescription drug worksheet doctor #
        ws1.merge_range("A13:G13","Chỉ định dùng thuốc:",normal_style)

        row_drug1 = 14
        total_import_price = 0
        index = 1

        for drug in history.prescriptiondrug_set.all():
            ws1.merge_range("B{}:F{}".format(str(row_drug1),str(row_drug1)),str(index)+". "+drug.medicine.full_name,header_style)
            ws1.merge_range("J{}:K{}".format(str(row_drug1),str(row_drug1)),drug.quantity+" viên",normal_style)
            index += 1

            ws1.merge_range("B{}:K{}".format(str(row_drug1+1),str(row_drug1+1)),"Mỗi lần "+drug.dose+" viên"+", "+drug.time_take_medicine,normal_style)

            ws1.merge_range("B{}:C{}".format(str(row_drug1+2),str(row_drug1+2)),"Giá bán (VNĐ)",normal_style)
            ws1.merge_range("D{}:F{}".format(str(row_drug1+2),str(row_drug1+2)),int(drug.cost),number_style)


            ws1.merge_range("G{}:H{}".format(str(row_drug1+2),str(row_drug1+2)),"Giá mua (VNĐ)",normal_style)
            ws1.merge_range("I{}:K{}".format(str(row_drug1+2),str(row_drug1+2)),int(drug.medicine.import_price)*int(drug.quantity),number_style)
            row_drug1 += 3
            total_import_price += int(drug.medicine.import_price)*int(drug.quantity)
            

        # informtation total cost at worksheet patient #
        ws.merge_range("A{}:C{}".format(str(row_drug+1),str(row_drug+1)),"Tổng tiền thuốc (VNĐ)",normal_style)
        ws.merge_range("D{}:G{}".format(str(row_drug+1),str(row_drug+1)),total_cost,number_style)

        if settings_service.medical_ultrasonography_cost:
            ws.merge_range("A{}:C{}".format(str(row_drug+2),str(row_drug+2)),"Tiền siêu âm (VNĐ)",normal_style)
            ws.merge_range("D{}:G{}".format(str(row_drug+2),str(row_drug+2)),int(settings_service.medical_ultrasonography_cost),number_style)
        if settings_service.endoscopy_cost:
            ws.merge_range("A{}:C{}".format(str(row_drug+3),str(row_drug+3)),"Tiền nội soi (VNĐ)",normal_style)
            ws.merge_range("D{}:G{}".format(str(row_drug+3),str(row_drug+3)),int(settings_service.endoscopy_cost),number_style)

        # informtation total benefit at worksheet doctor #
        ws1.merge_range("A{}:C{}".format(str(row_drug1+1),str(row_drug1+1)),"Tổng giá bán (VNĐ)",normal_style)
        ws1.merge_range("D{}:G{}".format(str(row_drug1+1),str(row_drug1+1)),total_cost,number_style)

        ws1.merge_range("A{}:C{}".format(str(row_drug1+2),str(row_drug1+2)),"Tổng giá mua (VNĐ)",normal_style)
        ws1.merge_range("D{}:G{}".format(str(row_drug1+2),str(row_drug1+2)),total_import_price,number_style)

        ws1.merge_range("A{}:C{}".format(str(row_drug1+3),str(row_drug1+3)),"Tổng lợi nhuận thuốc (VNĐ)",normal_style)
        ws1.merge_range("D{}:G{}".format(str(row_drug1+3),str(row_drug1+3)),total_cost-total_import_price,number_style)

        if settings_service.medical_ultrasonography_cost:
            ws1.merge_range("A{}:C{}".format(str(row_drug1+4),str(row_drug1+4)),"Tiền siêu âm (VNĐ)",normal_style)
            ws1.merge_range("D{}:G{}".format(str(row_drug1+4),str(row_drug1+4)),int(settings_service.medical_ultrasonography_cost),number_style)
        if settings_service.endoscopy_cost:
            ws1.merge_range("A{}:C{}".format(str(row_drug1+5),str(row_drug1+5)),"Tiền nội soi (VNĐ)",normal_style)
            ws1.merge_range("D{}:G{}".format(str(row_drug1+5),str(row_drug1+5)),int(settings_service.endoscopy_cost),number_style)

        # information date in worksheet patient #
        day_name={0:"Thứ Hai",1:"Thứ Ba",2:"Thứ Tư",3:"Thứ Năm",4:"Thứ Sáu",5:"Thứ Bảy",6:"Chủ Nhật"}
        ws.merge_range("H{}:K{}".format(str(row_drug+5),str(row_drug+5)),day_name[history.date.weekday()]+", ngày "+str(history.date.day)+", tháng "+str(history.date.month)+", năm "+str(history.date.year))
        # information date in worksheet doctor #
        ws1.merge_range("H{}:K{}".format(str(row_drug1+7),str(row_drug1+7)),day_name[history.date.weekday()]+", ngày "+str(history.date.day)+", tháng "+str(history.date.month)+", năm "+str(history.date.year))


        wb.close()

        output.seek(0)

        response = HttpResponse(output, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=test.xlsx'

        return response


