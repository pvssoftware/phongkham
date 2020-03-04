from django import forms

from user.models import Payment, DoctorProfile

class PaymentForm(forms.ModelForm):
    
    class Meta:
        model = Payment
        fields= ["email","bank_code"]

    def clean_email(self):
        email = self.cleaned_data["email"]

        try:
            DoctorProfile.objects.get(user__email=email)
            return email
        except:
            raise forms.ValidationError('Bạn chưa đăng ký tài khoản bác sĩ.',
                code='invalid_email',)
                




class ProductForm(forms.Form):
    license = forms.CharField(max_length=50)
    money = forms.CharField()
    order_desc = forms.CharField()

