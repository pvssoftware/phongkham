import os
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# from rest_framework.utils import model_meta
from django.conf import settings
from .models import MedicalRecord, MedicalHistory
from .custom_serializers import CustomHyperlinkedIdentityField, CustomHyperlinkedRelatedField, RecordSerializerField, validated_file, remove_file, update_file_serializer, BirthDateSerializerField, PhoneSerializerField
from user.utils import get_price_app_or_setting
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
    # birth_date = serializers.DateField(format="%Y")
    birth_date = BirthDateSerializerField()
    phone = PhoneSerializerField()
    class Meta:
        model = MedicalRecord
        fields = ("id","full_name","sex","birth_date","address","phone")
# list ultrasound examination patients
class ExaminationPatientsUltrasoundSerializer(serializers.ModelSerializer):

    medical_record = MedicalRecordExaminationSerializer()
    date_booked = serializers.DateTimeField(format="%d/%m/%Y %H:%M",input_formats=["%d/%m/%Y %H:%M",])
    class Meta:
        model = MedicalHistory
        fields = ("id","date_booked","ordinal_number","medical_ultrasonography","medical_ultrasonography_file","medical_ultrasonography_cost","medical_ultrasonography_2","medical_ultrasonography_file_2","medical_ultrasonography_cost_2","medical_ultrasonography_3","medical_ultrasonography_file_3","medical_ultrasonography_cost_3","medical_record")


# upload medical ultrasonography file
class UploadMedicalUltrasonographySerializer(serializers.ModelSerializer):
    # link = serializers.SerializerMethodField()
    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography","medical_ultrasonography_file","medical_ultrasonography_cost","is_waiting")
        read_only_fields = ("id",)

    # def get_link(self, history):
    #     request = self.context.get('request')
    #     link = history.medical_ultrasonography_file.url
    #     return request.build_absolute_uri(link)

    def update(self, instance, validated_data):
        # name the file upload
        file_upload = validated_data.get("medical_ultrasonography_file",None)

        # validate file
        validated_file(file_upload)
        # remove old file
        remove_file(instance.medical_ultrasonography_file)

        
        # instance.medical_ultrasonography_file = file_upload
        # print(list(self.fields.keys())[3])
        # print(validated_data.items())

        # instance.medical_ultrasonography = validated_data.get("medical_ultrasonography",instance.medical_ultrasonography)
        # # get price from app or settings
        # instance.medical_ultrasonography_cost = get_price_ultrasound_app_or_setting(instance.medical_record.doctor,validated_data.get("medical_ultrasonography_cost","0"))

        # instance.is_waiting = self.context.get("is_waiting")
        # instance.save()

        return update_file_serializer(
            instance,
            validated_data.get("medical_ultrasonography",instance.medical_ultrasonography),
            file_upload,
            get_price_app_or_setting(instance.medical_record.doctor.doctor.settingsservice.medical_ultrasonography_cost,validated_data.get("medical_ultrasonography_cost","0")),
            self.context.get("is_waiting"),
            list(self.fields.keys())
        )

# upload medical ultrasonography file 2
class UploadMedicalUltrasonographySerializer2(serializers.ModelSerializer):
    
    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography_2","medical_ultrasonography_file_2","medical_ultrasonography_cost_2","is_waiting")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        # name the file upload
        file_upload = validated_data.get("medical_ultrasonography_file_2",None)

        # validate file
        validated_file(file_upload)
        # remove old file
        remove_file(instance.medical_ultrasonography_file_2)

        return update_file_serializer(
            instance,
            validated_data.get("medical_ultrasonography_2",instance.medical_ultrasonography_2),
            file_upload,
            get_price_app_or_setting(instance.medical_record.doctor.doctor.settingsservice.medical_ultrasonography_cost,validated_data.get("medical_ultrasonography_cost_2","0")),
            self.context.get("is_waiting"),
            list(self.fields.keys())
        )

# upload medical ultrasonography file 3
class UploadMedicalUltrasonographySerializer3(serializers.ModelSerializer):
    
    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography_3","medical_ultrasonography_file_3","medical_ultrasonography_cost_3","is_waiting")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        # name the file upload
        file_upload = validated_data.get("medical_ultrasonography_file_3",None)

        # validate file
        validated_file(file_upload)
        # remove old file
        remove_file(instance.medical_ultrasonography_file_3)

        return update_file_serializer(
            instance,
            validated_data.get("medical_ultrasonography_3",instance.medical_ultrasonography_3),
            file_upload,
            get_price_app_or_setting(instance.medical_record.doctor.doctor.settingsservice.medical_ultrasonography_cost,validated_data.get("medical_ultrasonography_cost_3","0")),
            self.context.get("is_waiting"),
            list(self.fields.keys())
        )
#  Response data ultrasound
class ResponseUploadMedicalUltrasonographySerializer(ExaminationPatientsUltrasoundSerializer):
    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography","medical_ultrasonography_file","medical_ultrasonography_cost","medical_ultrasonography_2","medical_ultrasonography_file_2","medical_ultrasonography_cost_2","medical_ultrasonography_3","medical_ultrasonography_file_3","medical_ultrasonography_cost_3","is_waiting","date_booked","medical_record","ordinal_number")
        read_only_fields = ("id",)

# Create new history when upload ultrasound file
class CreateUploadMedicalUltrasonographySerializer(ExaminationPatientsUltrasoundSerializer):
    # birth_date = serializers.DateField(format="%Y")
    
    class Meta:
        model = MedicalHistory
        fields=("id","medical_ultrasonography","medical_ultrasonography_file","medical_ultrasonography_cost","is_waiting","date_booked","medical_record","ordinal_number")
        read_only_fields = ("id",)

    def get_fields(self, *args, **kwargs):
        fields = super(CreateUploadMedicalUltrasonographySerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "POST":
            fields['medical_record'].required = False
            
        return fields

    def create(self,validated_data):
        file_upload = validated_data.get("medical_ultrasonography_file",None)
        # validate file
        validated_file(file_upload)


        instance = MedicalHistory.objects.create(medical_record=self.context.get("medical_record"),date_booked=validated_data.get("date_booked",None),medical_ultrasonography=validated_data.get("medical_ultrasonography",None),is_waiting=validated_data.get("is_waiting"),ordinal_number=validated_data.get("ordinal_number",None),medical_ultrasonography_cost=get_price_app_or_setting(self.context.get("request").user.doctor.settingsservice.medical_ultrasonography_cost,validated_data.get("medical_ultrasonography_cost","0")))

        instance.medical_ultrasonography_file=file_upload
        instance.save()

        return instance



# list medical test examination patients
class ExaminationPatientsMedicalTestSerializer(serializers.ModelSerializer):

    medical_record = MedicalRecordExaminationSerializer()
    date_booked = serializers.DateTimeField(format="%d/%m/%Y %H:%M",input_formats=["%d/%m/%Y %H:%M",])
    class Meta:
        model = MedicalHistory
        fields = ("id","date_booked","ordinal_number","medical_test","medical_test_file","medical_test_cost","medical_test_2","medical_test_file_2","medical_test_cost_2","medical_test_3","medical_test_file_3","medical_test_cost_3","medical_record")

# upload medical test file
class UploadMedicalTestSerializer(serializers.ModelSerializer):
    # link = serializers.SerializerMethodField()
    class Meta:
        model = MedicalHistory
        fields=("id","medical_test","medical_test_file","medical_test_cost","is_waiting")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        # name the file upload
        file_upload = validated_data.get("medical_test_file",None)

        # validate file
        validated_file(file_upload)
        # remove old file
        remove_file(instance.medical_test_file)

        return update_file_serializer(
            instance,
            validated_data.get("medical_test",instance.medical_test),
            file_upload,
            get_price_app_or_setting(instance.medical_record.doctor.doctor.settingsservice.medical_test_cost,validated_data.get("medical_test_cost","0")),
            self.context.get("is_waiting"),
            list(self.fields.keys())
        )


# upload medical test file 2
class UploadMedicalTestSerializer2(serializers.ModelSerializer):
    # link = serializers.SerializerMethodField()
    class Meta:
        model = MedicalHistory
        fields=("id","medical_test_2","medical_test_file_2","medical_test_cost_2","is_waiting")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        # name the file upload
        file_upload = validated_data.get("medical_test_file_2",None)

        # validate file
        validated_file(file_upload)
        # remove old file
        remove_file(instance.medical_test_file_2)

        return update_file_serializer(
            instance,
            validated_data.get("medical_test_2",instance.medical_test_2),
            file_upload,
            get_price_app_or_setting(instance.medical_record.doctor.doctor.settingsservice.medical_test_cost,validated_data.get("medical_test_cost_2","0")),
            self.context.get("is_waiting"),
            list(self.fields.keys())
        )


# upload medical test file 3
class UploadMedicalTestSerializer3(serializers.ModelSerializer):
    # link = serializers.SerializerMethodField()
    class Meta:
        model = MedicalHistory
        fields=("id","medical_test_3","medical_test_file_3","medical_test_cost_3","is_waiting")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        # name the file upload
        file_upload = validated_data.get("medical_test_file_3",None)

        # validate file
        validated_file(file_upload)
        # remove old file
        remove_file(instance.medical_test_file_3)

        return update_file_serializer(
            instance,
            validated_data.get("medical_test_3",instance.medical_test_3),
            file_upload,
            get_price_app_or_setting(instance.medical_record.doctor.doctor.settingsservice.medical_test_cost,validated_data.get("medical_test_cost_3","0")),
            self.context.get("is_waiting"),
            list(self.fields.keys())
        )

#  Response data medical test
class ResponseUploadMedicalTestSerializer(ExaminationPatientsMedicalTestSerializer):
    class Meta:
        model = MedicalHistory
        fields=("id","medical_test","medical_test_file","medical_test_cost","medical_test_2","medical_test_file_2","medical_test_cost_2","medical_test_3","medical_test_file_3","medical_test_cost_3","is_waiting","date_booked","medical_record","ordinal_number")
        read_only_fields = ("id",)

# Create new history when upload ultrasound file
class CreateUploadMedicalTestSerializer(ExaminationPatientsMedicalTestSerializer):
    # birth_date = serializers.DateField(format="%Y")
    
    class Meta:
        model = MedicalHistory
        fields=("id","medical_test","medical_test_file","medical_test_cost","is_waiting","date_booked","medical_record","ordinal_number")
        read_only_fields = ("id",)

    def get_fields(self, *args, **kwargs):
        fields = super(CreateUploadMedicalTestSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "POST":
            fields['medical_record'].required = False
            
        return fields

    def create(self,validated_data):
        file_upload = validated_data.get("medical_test_file",None)
        # validate file
        validated_file(file_upload)

        
        instance = MedicalHistory.objects.create(medical_record=self.context.get("medical_record"),date_booked=validated_data.get("date_booked",None),medical_test=validated_data.get("medical_test",None),is_waiting=validated_data.get("is_waiting"),ordinal_number=validated_data.get("ordinal_number",None),medical_test_cost=get_price_app_or_setting(self.context.get("request").user.doctor.settingsservice.medical_test_cost,validated_data.get("medical_test_cost","0")))

        instance.medical_test_file=file_upload
        instance.save()

        return instance
