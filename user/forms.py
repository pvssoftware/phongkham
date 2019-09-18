import re, logging
from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .utils import ActivationMailFormMixin
from .models import User, DoctorProfile

logger = logging.getLogger(__name__)


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('email','doctor','is_staff','is_active','is_admin')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email','doctor','is_staff','is_active','is_admin','password',)

class UserCreationFormMix(
        ActivationMailFormMixin,
        UserCreationForm):
    KIND_DOCTOR = [
        ("obstetrician-gynecologist","bác sĩ sản phụ khoa"),
        ("Oral maxillofacial surgeon","bác sĩ ngoại răng hàm mặt"),
    ]

    full_name = forms.CharField(label="Họ và tên",
        max_length=100, help_text='Họ và tên đầy đủ.')

    error_messages ={
        'invalid_phone':"Số điện thoại không hợp lệ.",
        'password_mismatch':"Xác nhận mật khẩu không khớp với mật khẩu ở trên."
    }

    phone = forms.CharField(label="Số điện thoại",max_length=14,help_text="Số điện thoại cá nhân.")
    clinic_address = forms.CharField(label="Địa chỉ",max_length=70,help_text="Địa chỉ của phòng khám.")
    kind = forms.ChoiceField(label="Chuyên nghành",help_text="Chuyên nghành khám chữa bệnh.",widget=forms.Select,choices=KIND_DOCTOR)


    password1 = forms.CharField(label=("Mật khẩu"),
        widget=forms.PasswordInput,help_text="<ul><li>Mật khẩu không được giống thông tin cá nhân.</li><li>Mật khẩu phải có ít nhất 8 ký tự.</li><li>Mật khẩu không được là mật khẩu quá thông dụng.</li><li>Mật khẩu không được chứa toàn bộ ký hiệu số.</li></ul>")

    password2 = forms.CharField(label=("Xác nhận mật khẩu"),
        widget=forms.PasswordInput,
        help_text=("Nhập lại mật khẩu giống với mật khẩu ở trên để xác nhận."))

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('full_name', 'email','clinic_address','phone','kind')

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        
        valid_phone = re.match(r"^(0|\+84)(9|3|7|8|5)([0-9]{8})$",phone)
        if not valid_phone:
            raise forms.ValidationError(self.error_messages['invalid_phone'],
                code='invalid_phone',)
        return phone

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, **kwargs):
        user = super().save(commit=False)
        if not user.pk:
            user.is_active = False
            send_mail = True
        else:
            send_mail = False
        
        user.doctor=DoctorProfile.objects.create(phone= self.cleaned_data['phone'], full_name= self.cleaned_data['full_name'], clinic_address= self.cleaned_data['clinic_address'], kind= self.cleaned_data['kind'],is_trial=True,time_start_trial = date.today())
        user.save()
        self.save_m2m()
        if send_mail:
            self.send_mail(user=user, **kwargs)
        return user


class SetPasswordFormMix(SetPasswordForm):
    new_password1 = forms.CharField(
        label=("Mật khẩu mới"),
        widget=forms.PasswordInput(),
        strip=False,
        help_text="<ul><li>Mật khẩu không được giống thông tin cá nhân.</li><li>Mật khẩu phải có ít nhất 8 ký tự.</li><li>Mật khẩu không được là mật khẩu quá thông dụng.</li><li>Mật khẩu không được chứa toàn bộ ký hiệu số.</li></ul>",
    )

    new_password2 = forms.CharField(
        label=("Xác nhận mật khẩu mới"),
        strip=False,
        widget=forms.PasswordInput(),
        help_text="Nhập lại mật khẩu mới giống với mật khẩu ở trên để xác nhận."
    )

    error_messages ={
        'password_mismatch':"Xác nhận mật khẩu mới không khớp với mật khẩu ở trên.",
    }

class ResendActivationEmailForm(
        ActivationMailFormMixin, forms.Form):

    email = forms.EmailField()

    mail_validation_error = (
        'Could not re-send activation email. '
        'Please try again later. (Sorry!)')

    def save(self, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(
                email=self.cleaned_data['email'])
        except:
            logger.warning(
                'Resend Activation: No user with '
                'email: {} .'.format(
                    self.cleaned_data['email']))
            return None
        self.send_mail(user=user, **kwargs)
        return user

