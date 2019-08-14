from django.contrib import admin
from .models import User, DoctorProfile

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):

	# add_form = UserCreationForm
	#form = UserChangeForm
	list_display = ["email","is_staff","is_active","doctor"]
	model = User
	ordering = ["email",]

class DoctorProfileAdmin(admin.ModelAdmin):
	model = DoctorProfile
	list_display = ["full_name","phone","kind"]
	ordering = ["full_name","kind",]



admin.site.register(User,CustomUserAdmin)
admin.site.register(DoctorProfile,DoctorProfileAdmin)
