import os
from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


# validate file upload
def validated_file(file_upload, instance):
    if file_upload:
        content_type = file_upload.content_type.split("/")[1]
        if content_type in settings.CONTENT_TYPES:                
            if file_upload.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError("File upload của bạn trên 5M.")
        else:
            raise ValidationError("Bạn nên upload định dạng PDF.")

# remove file on server
def remove_file(file):
    if file:
        try:
            os.remove(file.path)
        except FileNotFoundError:
            pass
# name file upload
# def name_upload_file(instance,file,prefix=""):
#     if file != None:
#         filename = ("%s_%s_%s%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone, instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"),prefix)
#         file.name = filename
#     return file
# update ultrasound util
def update_ultrasound_serializer(instance,medical_ultrasonography,medical_ultrasonography_file,medical_ultrasonography_cost,is_waiting,fields):

    setattr(instance,fields[1],medical_ultrasonography)
    setattr(instance,fields[2],medical_ultrasonography_file)
    setattr(instance,fields[3],medical_ultrasonography_cost)
    setattr(instance,fields[4],is_waiting)
    
    instance.save()

    return instance





class CustomHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'pk_doctor': obj.doctor.pk,
            'pk_record': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

class CustomHyperlinkedRelatedField(serializers.HyperlinkedRelatedField):
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'pk_doctor': obj.medical_record.doctor.pk,
            'pk_history': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

class RecordSerializerField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = self.queryset
        if hasattr(self.root, 'pk_doctor'):
            queryset = queryset.filter(doctor__pk=self.root.pk_doctor)
        return queryset
