from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

from django.http import HttpResponse, Http404
from django.db.models import Q
from django.contrib.auth import (
    get_user, get_user_model, logout)
from django.contrib.auth.decorators import \
    login_required
from django.contrib.auth.tokens import \
    default_token_generator as token_generator
from django.contrib.messages import error, success
from django.urls import reverse_lazy, reverse
from django.template.response import \
    TemplateResponse
from django.utils.decorators import \
    method_decorator
from django.utils.encoding import force_text
from django.utils.http import \
    urlsafe_base64_decode
from django.views.decorators.cache import \
    never_cache
from django.views.decorators.csrf import \
    csrf_protect
from django.views.decorators.debug import \
    sensitive_post_parameters
from django.template.loader import get_template
from django.core.mail import EmailMessage, send_mail, get_connection
from django.views.generic import View

from .forms import UserCreationFormMix, ResendActivationEmailForm, VerifyEmailForm, AuthenticationFormMix
from .models import DoctorProfile

from .utils import MailContextViewMixin
from .vnpay.forms_vnpay import ProductForm
from  .cart.cart import Cart
# Create your views here.

def license_page(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            cart = Cart(request)
            cart.choose(form.cleaned_data['license'],form.cleaned_data["money"],form.cleaned_data['order_desc'])

            return redirect("verify_email")
    return render(request,"user/license_product.html",{})

def verify_email(request):
    form = VerifyEmailForm()
    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            
            email = form.cleaned_data["email"]
            try:
                doctor = DoctorProfile.objects.get(user__email=email)
                cart = Cart(request)
                # check whether doctor bought ultrasound adn buy again
                if doctor.license_ultrasound and cart.cart["license"] == "ultrasound_app":
                    form.errors["email"] = ["Bạn đã mua license ultrasound app"] 
                    return render(request,"user/verify_email.html",{"form":form})

                cart.add_email(email)
                return redirect(reverse("payment"))
            except DoctorProfile.DoesNotExist:
                form.errors["email"] = ["Bạn chưa đăng ký email này"]
                return render(request,"user/verify_email.html",{"form":form})
    return render(request,"user/verify_email.html",{"form":form})


class LoginViewMix(LoginView):
    template_name = "user/login.html"
    form_class = AuthenticationFormMix
    def get_success_url(self):
        user = self.request.user
        # return reverse_lazy("doctor_profile",kwargs={"pk_doctor":user.pk})
        if user.doctor.kind == "obstetrician-gynecologist":
            return reverse_lazy("doctor_profile",kwargs={"pk_doctor":user.pk})
    # def get(self,request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect("doctor_profile")
    #     else:
    #         return self.render_to_response(self.get_context_data())

class ActivateAccount(View):
    success_url = reverse_lazy('login')
    template_name = 'user/link_activation_invalid.html'

    @method_decorator(never_cache)
    def get(self, request, uidb64, token):
        User = get_user_model()
        try:
            # urlsafe_base64_decode()
            #     -> bytestring in Py3
            uid = force_text(
                urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError,
                OverflowError, User.DoesNotExist):
            user = None
        if (user is not None
                and token_generator
                .check_token(user, token)):
            user.is_active = True
            user.save()
            success(
                request,
                'User Activated! '
                'You may now login.')
            return redirect(self.success_url)
        else:
            return TemplateResponse(
                request,
                self.template_name)

class CreateAccount(MailContextViewMixin, View):
    form_class = UserCreationFormMix
    success_url = reverse_lazy(
        'create_account_done')
    template_name = 'user/sign_up_for_trial.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        return TemplateResponse(
            request,
            self.template_name,
            {'form': self.form_class()})

    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters(
        'password1', 'password2'))
    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            # not catching returned user
            bound_form.save(
                **self.get_save_kwargs(request))
            if bound_form.mail_sent:  # mail sent?
                return redirect(self.success_url)
            else:
                errs = (
                    bound_form.non_field_errors())
                for err in errs:
                    error(request, err)
                # TODO: redirect to email resend
                return redirect("user:resend_activation")
        return TemplateResponse(
            request,
            self.template_name,
            {'form': bound_form})

class ResendActivationEmail(
        MailContextViewMixin, View):
    form_class = ResendActivationEmailForm
    success_url = reverse_lazy('login')
    template_name = 'user/resend_email_activation.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        return TemplateResponse(
            request,
            self.template_name,
            {'form': self.form_class()})

    @method_decorator(csrf_protect)
    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            user = bound_form.save(
                **self.get_save_kwargs(request))
            if (user is not None
                    and not bound_form.mail_sent):
                errs = (
                    bound_form.non_field_errors())
                for err in errs:
                    error(request, err)
                if errs:
                    bound_form.errors.pop(
                        '__all__')
                return TemplateResponse(
                    request,
                    self.template_name,
                    {'form': bound_form})
        success(
            request,
            'Activation Email Sent!')
        return redirect(self.success_url)

