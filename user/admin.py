from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, SettingsTime, SettingsService, Payment, License
from .forms import CustomUserChangeForm, CustomUserCreationForm


# Mixin class

class DoctorMixin:
	search_fields = ("doctor__full_name","doctor__user__email","doctor__user__pk")

	def get_email(self, obj):
		return obj.doctor.user.email
	get_email.short_description = 'email'

	def get_id(self, obj):
		return obj.doctor.user.id
	get_id.short_description = 'id_doctor'

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
	list_display = ["full_name","phone","get_email","get_id"]
	ordering = ["full_name","kind",]
	search_fields = ('full_name','user__email','user__pk')

	def get_email(self, obj):
		return obj.user.email
	get_email.short_description = 'email'

	def get_id(self, obj):
		return obj.user.id
	get_id.short_description = 'id_doctor'

class SettingsTimeAdmin(DoctorMixin,admin.ModelAdmin):
	model = SettingsTime
	list_display = ["doctor","examination_period","get_email","get_id"]

class SettingsServiceAdmin(DoctorMixin,admin.ModelAdmin):
	model = SettingsService
	list_display = ["doctor","get_email","get_id"]

	

class PaymentAdmin(admin.ModelAdmin):
	model = Payment
	list_display = ["email","license","order_id"]
	search_fields = ('email',"order_id")

class LicenseAdmin(DoctorMixin,admin.ModelAdmin):
	model = License
	list_display = ["doctor","license_end","get_email","get_id"]
	
	
	

admin.site.register(User,CustomUserAdmin)
admin.site.register(DoctorProfile,DoctorProfileAdmin)
admin.site.register(SettingsTime,SettingsTimeAdmin)
admin.site.register(SettingsService,SettingsServiceAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(License,LicenseAdmin)
