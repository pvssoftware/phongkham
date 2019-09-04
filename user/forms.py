from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User



class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('email','doctor','is_staff','is_active','is_admin')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email','doctor','is_staff','is_active','is_admin','password',)

