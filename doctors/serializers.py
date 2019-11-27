import os
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
from .models import MedicalRecord, MedicalHistory
from .custom_serializers import CustomHyperlinkedIdentityField, CustomHyperlinkedRelatedField, RecordSerializerField
from user.models import User, DoctorProfile




class MedicalRecordSerializer(serializers.HyperlinkedModelSerializer):

    url = CustomHyperlinkedIdentityField(view_name="medical_record_detail")
    doctor = serializers.SlugRelatedField(queryset=User.objects.exclude(doctor=None),slug_field="pk")
    medicalhistories = CustomHyperlinkedRelatedField(many=True,read_only=True,view_name="medical_history_detail")

    class Meta:
        model = MedicalRecord
        fields = ("url","phone","doctor","medicalhistories")

class MedicalHistorySerializer(serializers.HyperlinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        self.pk_doctor = kwargs.pop('pk_doctor')
        super().__init__(*args, **kwargs)

    medical_record = RecordSerializerField(queryset=MedicalRecord.objects.all(),slug_field="phone")
    date_booked = serializers.DateTimeField(format="%d/%m/%Y %H:%M",input_formats=["%d/%m/%Y %H:%M",])

    class Meta:
        model = MedicalHistory
        fields = ("date_booked","medical_record","ordinal_number","is_waiting")


class MedicalRecordExaminationSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalRecord
        fields = ("id","full_name","address","phone")
# list examination patients
class ExaminationPatientsSerializer(serializers.ModelSerializer):

    medical_record = MedicalRecordExaminationSerializer()
    date_booked = serializers.DateTimeField(format="%d/%m/%Y %H:%M",input_formats=["%d/%m/%Y %H:%M",])
    class Meta:
        model = MedicalHistory
        fields = ("id","date_booked","medical_record","ordinal_number")
# upload medical ultrasonography file
class UploadMedicalUltrasonographySerializer(serializers.ModelSerializer):
    # link = serializers.SerializerMethodField()
    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography","medical_ultrasonography_file",)
        read_only_fields = ("id",)

    # def get_link(self, history):
    #     request = self.context.get('request')
    #     link = history.medical_ultrasonography_file.url
    #     return request.build_absolute_uri(link)

    def update(self, instance, validated_data):
        file_upload = validated_data.get("medical_ultrasonography_file",None)
        if file_upload:
            content_type = file_upload.content_type.split("/")[1]
            if content_type in settings.CONTENT_TYPES:                
                if file_upload.size > settings.MAX_UPLOAD_SIZE:
                    raise ValidationError("File upload của bạn trên 5M.")
            else:
                raise ValidationError("Bạn nên upload định dạng PDF.")

        if instance.medical_ultrasonography_file:
            try:
                os.remove(instance.medical_ultrasonography_file.path)
            except FileNotFoundError:
                pass 
        instance.medical_ultrasonography_file = file_upload

        instance.medical_ultrasonography = validated_data.get("medical_ultrasonography",instance.medical_ultrasonography)
        instance.save()

        return instance
