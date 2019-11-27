import os
from rest_framework import serializers
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

    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography","medical_ultrasonography_file")
        read_only_fields = ("id",)
    def update(self, instance, validated_data):
        instance.medical_ultrasonography = validated_data.get("medical_ultrasonography",instance.medical_ultrasonography)
        if instance.medical_ultrasonography_file:
            try:
                os.remove(instance.medical_ultrasonography_file.path)
            except FileNotFoundError:
                pass 
        instance.medical_ultrasonography_file = validated_data.get("medical_ultrasonography_file",None)
        instance.save()
        return instance
