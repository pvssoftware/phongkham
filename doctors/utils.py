from user.models import User
from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Q
from .forms import SearchDrugForm
from .models import Medicine





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
        doctor = User.objects.get(pk=pk_doctor)
        
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
    def get(self,request,pk_doctor,*args,**kwargs):
        doctor = User.objects.get(pk=pk_doctor)

        if doctor == request.user:
            self.object_list = self.get_queryset().filter(doctor=doctor)

            page = request.GET.get('page')
            order = request.GET.get('order')

            if order == 'desc':
                self.object_list = self.object_list.order_by('-full_name')

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

            context = self.get_context_data()
            context.update({"doctor":doctor,"page":page,"order":order})

            return self.render_to_response(context)

    def post(self,request,pk_doctor):
        doctor = User.objects.get(pk=pk_doctor)
        if doctor == request.user:
            form = SearchDrugForm(request.POST)
            if form.is_valid():
                search_drug_value = form.cleaned_data["search_drug"]

                drug_results = Medicine.objects.filter(Q(name__icontains=search_drug_value)| Q(full_name__icontains=search_drug_value))

                return render(request,'doctors/doctor_search_drugs.html',{"pk_doctor":pk_doctor,"drug_results":drug_results})


            