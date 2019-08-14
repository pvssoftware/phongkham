import xlsxwriter, io
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.db.models import Q

from user.models import User
from .models import MedicalRecord, MedicalHistory, Medicine, PrescriptionDrug
from .utils import PageLinksMixin, DoctorProfileMixin, MedicineMixin
from .forms import MedicalHistoryForm, SearchDrugForm, TakeDrugForm, MedicalRecordForm, SearchNavBarForm, MedicineForm

# search on navbar

def search_navbar(request,pk_doctor):
    user = User.objects.get(pk=pk_doctor)
    if user.doctor:
        form = SearchNavBarForm(request.GET)
        if form.is_valid():
            results = MedicalRecord.objects.filter(Q(doctor=user),Q (full_name__icontains=form.cleaned_data['search_navbar']) | Q(identity_card__icontains=form.cleaned_data["search_navbar"]))

            return render(request,'doctors/doctor_search_navbar.html',{"results":results,"pk_doctor":pk_doctor})

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

            return render(request,'doctors/doctor_search_drugs.html',{"pk_doctor":pk_doctor,"drug_results":drug_results})

# Medicine create view
def medicine_create(request,pk_doctor):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        if request.method == "POST":
            form = MedicineForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.doctor = doctor
                form.save()
                return redirect(reverse('medicine_list',kwargs={'pk_doctor':pk_doctor}))
        else:
            form = MedicineForm()
            return render(request,'doctors/doctor_medicine_create.html',{'form':form,'pk_doctor':pk_doctor})

# Medicine edit view
def medicine_edit(request,pk_doctor,pk_medicine):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        medicine = Medicine.objects.get(pk=pk_medicine)
        if request.method == "POST":
            form = MedicineForm(request.POST)
            if form.is_valid():
                medicine.name = form.cleaned_data['name']
                medicine.full_name = form.cleaned_data['full_name']
                medicine.sale_price = form.cleaned_data['sale_price']
                medicine.import_price = form.cleaned_data['import_price']
                medicine.quantity = form.cleaned_data['quantity']
                medicine.save()
                return redirect(reverse('medicine_list',kwargs={'pk_doctor':pk_doctor}))
        else:
            form = MedicineForm(initial={"name":medicine.name,'full_name':medicine.full_name,'sale_price':medicine.sale_price,'import_price':medicine.import_price,'quantity':medicine.quantity})
            return render(request,'doctors/doctor_medicine_edit.html',{'form':form,'pk_doctor':pk_doctor,'pk_medicine':pk_medicine})
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
            form = MedicalRecordForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                # form.birth_date = datetime.strptime(form.birth_date,'%d/%m/%Y')
                
                form.doctor = doctor
                form.save()

                return redirect(reverse("doctor_profile",kwargs={"pk_doctor":pk_doctor}))
        else:
            form = MedicalRecordForm()
            return render(request,'doctors/doctor_medical_record_create.html',{"form":form,'pk_doctor':pk_doctor})

# Medical record edit view
def medical_record_edit(request,pk_doctor,pk_mrecord):
    doctor = User.objects.get(pk=pk_doctor)

    if doctor == request.user:
        mrecord  = MedicalRecord.objects.get(pk=pk_mrecord)
        if request.method == "POST":
            form = MedicalRecordForm(request.POST)
            if form.is_valid():
                
                form = form.save(commit=False)
                # print(form.cleaned_data['sex'])
                
                mrecord.full_name = form.full_name
                mrecord.birth_date = form.birth_date
                mrecord.address = form.address
                mrecord.sex = form.sex
                print(form.sex)
                mrecord.height = form.height
                mrecord.identity_card = form.identity_card
                mrecord.save()
                return redirect(reverse('medical_record_view',kwargs={"pk_doctor":pk_doctor,"pk_mrecord":pk_mrecord}))
        else:
            form = MedicalRecordForm(initial={"full_name":mrecord.full_name,"birth_date":mrecord.birth_date.strftime("%d/%m/%Y"),"address":mrecord.address,"height":mrecord.height,"identity_card":mrecord.identity_card})
            return render(request,"doctors/doctor_medical_record_edit.html",{"form":form,"pk_doctor":pk_doctor,"mrecord":mrecord})

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
        if request.method == "POST":
            form = MedicalHistoryForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.medical_record = mrecord
                form.save()
                print(form)
                return redirect(reverse("prescription_drug", kwargs={"pk_doctor": pk_doctor, "pk_mrecord": pk_mrecord, "pk_history": form.pk}))
        else:
            form = MedicalHistoryForm()
            return render(request, "doctors/doctor_medical_record.html", {"mrecord": mrecord, "doctor": doctor, "form": form})

# Medical record back view


def medical_record_back_view(request, pk_mrecord, pk_doctor, pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        if request.method == "POST":
            form = MedicalHistoryForm(request.POST)
            if form.is_valid():
                history_edit = MedicalHistory.objects.get(pk=pk_history)
                history_edit.disease_symptom = form.cleaned_data["disease_symptom"]
                history_edit.diagnostis =form.cleaned_data["diagnostis"]
                history_edit.save()

                return redirect(reverse("prescription_drug", kwargs={"pk_doctor": pk_doctor, "pk_mrecord": pk_mrecord, "pk_history": history_edit.pk}))

        else:
            mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
            history_edit = MedicalHistory.objects.get(pk=pk_history)
            print(history_edit.disease_symptom)
            histories = mrecord.medicalhistory_set.exclude(pk=pk_history)
            form = MedicalHistoryForm(initial={
                                    "disease_symptom": history_edit.disease_symptom, "diagnostis": history_edit.diagnostis})
            
            return render(request, 'doctors/doctor_medical_record_back_view.html', {"histories": histories, "history_edit": history_edit, "form": form,"mrecord":mrecord,"doctor":doctor})

# Detail history medical




# Delete history medical 

def medical_history_del(request,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        history_del = MedicalHistory.objects.get(pk=pk_history)
        drugs_history_del = history_del.prescriptiondrug_set.all()
        for drug in drugs_history_del:
            drug.medicine.quantity = str(int(drug.medicine.quantity)+ int(drug.quantity))
            drug.medicine.save()
        history_del.delete()
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
        total_cost = 0
        for drug in history.prescriptiondrug_set.all():
            total_cost += int(drug.cost)

        return render(request,'doctors/doctor_final_info.html',{"doctor":doctor,"mrecord":mrecord,"history":history,"total_cost":total_cost})

def export_final_info_excel(request,pk_doctor,pk_mrecord,pk_history):
    doctor = User.objects.get(pk=pk_doctor)
    if doctor == request.user:
        mrecord = MedicalRecord.objects.get(pk=pk_mrecord)
        history = MedicalHistory.objects.get(pk=pk_history)
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output,{'remove_timezone': True})
        ws = wb.add_worksheet("Bệnh nhân")
        ws1 = wb.add_worksheet("Bác sĩ")

        # set row disease_symptom and dianostis
        # ws.set_row(8,50)
        # ws.set_row(9,50)
        
        # format 
        header_style = wb.add_format({"bold":True,"font_name":'Times New Roman','font_size':15, 'bold':True,'text_wrap':True,"valign":"vcenter"})
        normal_style = wb.add_format({"font_name":'Times New Roman','font_size':13,'text_wrap':True,"valign":"vcenter"})
        number_style = wb.add_format({"font_name":'Times New Roman','font_size':13,"border":1,'text_wrap':True,"align":"center","valign":"vcenter","num_format":'#,##0 ;[Red]General'})

        # information doctor at worksheet patient #
        ws.merge_range('A2:I2',"Phòng Khám "+doctor.doctor.kind.upper()+" - "+doctor.doctor.full_name.upper(),header_style)
        ws.merge_range("A3:K3","Địa chỉ: "+doctor.doctor.clinic_address,normal_style)
        ws.merge_range("A4:I4","Điện thoại đăng ký khám bệnh: "+doctor.doctor.phone,normal_style)
        # information doctor at worksheet doctor #
        ws1.merge_range('A2:I2',"Phòng Khám "+doctor.doctor.kind.upper()+" - "+doctor.doctor.full_name.upper(),header_style)
        ws1.merge_range("A3:K3","Địa chỉ: "+doctor.doctor.clinic_address,normal_style)
        ws1.merge_range("A4:I4","Điện thoại đăng ký khám bệnh: "+doctor.doctor.phone,normal_style)


        # artical at worksheet patient #
        ws.merge_range("E6:F6","TOA THUỐC",header_style)
        # artical at worksheet doctor #
        ws1.merge_range("E6:F6","TOA THUỐC",header_style)

        # information patient at worksheet patient #
        ws.merge_range("A9:G9","Họ và tên: "+mrecord.full_name.upper(),header_style)
        ws.merge_range("I9:K9","Năm sinh: "+mrecord.birth_date.strftime("%d/%m/%Y"),header_style)
        ws.merge_range("A11:H11","Địa chỉ: "+mrecord.address,normal_style)
        ws.merge_range("A12:H12","Chẩn đoán: "+history.diagnostis,normal_style)
        # information patient at worksheet doctor #
        ws1.merge_range("A9:G9","Họ và tên: "+mrecord.full_name.upper(),header_style)
        ws1.merge_range("I9:K9","Năm sinh: "+mrecord.birth_date.strftime("%d/%m/%Y"),header_style)
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

            ws.merge_range("C{}:K{}".format(str(row_drug+1),str(row_drug+1)),"Mỗi lần uống "+drug.dose+" viên"+", thời gian uống "+drug.time_take_medicine,normal_style)
            row_drug += 2
            total_cost += int(drug.cost)
        # information prescription drug worksheet doctor #
        ws1.merge_range("A13:G13","Chỉ định dùng thuốc:",normal_style)

        row_drug1 = 14
        total_import_price = 0

        for drug in history.prescriptiondrug_set.all():
            ws1.merge_range("B{}:F{}".format(str(row_drug1),str(row_drug1)),str(index)+". "+drug.medicine.full_name,header_style)
            ws1.merge_range("J{}:K{}".format(str(row_drug1),str(row_drug1)),drug.quantity+" viên",normal_style)
            index += 1

            ws1.merge_range("B{}:K{}".format(str(row_drug1+1),str(row_drug1+1)),"Mỗi lần uống "+drug.dose+" viên"+", thời gian uống "+drug.time_take_medicine,normal_style)

            ws1.merge_range("B{}:C{}".format(str(row_drug1+2),str(row_drug1+2)),"Giá bán (VNĐ)",normal_style)
            ws1.merge_range("D{}:F{}".format(str(row_drug1+2),str(row_drug1+2)),int(drug.cost),number_style)


            ws1.merge_range("G{}:H{}".format(str(row_drug1+2),str(row_drug1+2)),"Giá mua (VNĐ)",normal_style)
            ws1.merge_range("I{}:K{}".format(str(row_drug1+2),str(row_drug1+2)),int(drug.medicine.import_price)*int(drug.quantity),number_style)
            row_drug1 += 3
            total_import_price += int(drug.medicine.import_price)*int(drug.quantity)
            

        # informtation total cost at worksheet patient #
        ws.merge_range("A{}:C{}".format(str(row_drug+1),str(row_drug+1)),"Tổng tiền thuốc (VNĐ)",normal_style)
        ws.merge_range("D{}:G{}".format(str(row_drug+1),str(row_drug+1)),total_cost,number_style)
        # informtation total benefit at worksheet doctor #
        ws1.merge_range("A{}:C{}".format(str(row_drug1+1),str(row_drug1+1)),"Tổng giá bán (VNĐ)",normal_style)
        ws1.merge_range("D{}:G{}".format(str(row_drug1+1),str(row_drug1+1)),total_cost,number_style)

        ws1.merge_range("A{}:C{}".format(str(row_drug1+2),str(row_drug1+2)),"Tổng giá mua (VNĐ)",normal_style)
        ws1.merge_range("D{}:G{}".format(str(row_drug1+2),str(row_drug1+2)),total_import_price,number_style)

        ws1.merge_range("A{}:C{}".format(str(row_drug1+3),str(row_drug1+3)),"Tổng lợi nhuận (VNĐ)",normal_style)
        ws1.merge_range("D{}:G{}".format(str(row_drug1+3),str(row_drug1+3)),total_cost-total_import_price,number_style)


        # information date in worksheet patient #
        day_name={0:"Thứ Hai",1:"Thứ Ba",2:"Thứ Tư",3:"Thứ Năm",4:"Thứ Sáu",5:"Thứ Bảy",6:"Chủ Nhật"}
        ws.merge_range("H{}:K{}".format(str(row_drug+4),str(row_drug+4)),day_name[history.date.weekday()]+", ngày "+str(history.date.day)+", tháng "+str(history.date.month)+", năm "+str(history.date.year))
        # information date in worksheet dcotor #
        ws1.merge_range("H{}:K{}".format(str(row_drug1+6),str(row_drug1+6)),day_name[history.date.weekday()]+", ngày "+str(history.date.day)+", tháng "+str(history.date.month)+", năm "+str(history.date.year))


        wb.close()

        output.seek(0)

        response = HttpResponse(output, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=test.xlsx'

        return response


