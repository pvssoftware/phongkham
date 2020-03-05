from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, SettingsTime, SettingsService, Payment, License
from .forms import CustomUserChangeForm, CustomUserCreationForm

# Register your models here.

# class CustomUserAdmin(admin.ModelAdmin):

# 	# add_form = UserCreationForm
# 	#form = UserChangeForm
# 	list_display = ["email","is_staff","is_active","doctor"]
# 	model = User
# 	ordering = ["email",]

class CustomUserAdmin(UserAdmin):

	add_form = CustomUserCreationForm
	form = CustomUserChangeForm
	list_display = ["email","is_staff","is_active","doctor","pk"]
	model = User
	ordering = ["email",]
	fieldsets = (
        (None, {'fields': ('email',)}),
        ('Password', {'fields': ('password',)}),
		('dates',{'fields':('last_login',)}),
		('relatetionship',{'fields':('doctor',)}),
        ('Permissions', {'fields': ('is_admin','is_staff','is_active','is_superuser','user_permissions','groups')}),
    )
	add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'doctor','is_admin','is_staff','is_active','is_superuser','user_permissions','groups')}
        ),
    )
	search_fields = ('email',"pk")
	

class DoctorProfileAdmin(admin.ModelAdmin):
	model = DoctorProfile
	list_display = ["full_name","phone","kind"]
	ordering = ["full_name","kind",]
	search_fields = ('full_name','phone')

class SettingsTimeAdmin(admin.ModelAdmin):
	model = SettingsTime
	list_display = ["doctor","examination_period"]

class SettingsServiceAdmin(admin.ModelAdmin):
	model = SettingsService
	list_display = ["doctor",]

class PaymentAdmin(admin.ModelAdmin):
	model = Payment
	list_display = ["email","license","order_id"]
	search_fields = ('email',"order_id")

class LicenseAdmin(admin.ModelAdmin):
	model = License
	list_display = ["doctor","license_end","id"]
	search_fields = ("doctor",)

admin.site.register(User,CustomUserAdmin)
admin.site.register(DoctorProfile,DoctorProfileAdmin)
admin.site.register(SettingsTime,SettingsTimeAdmin)
admin.site.register(SettingsService,SettingsServiceAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(License,LicenseAdmin)
