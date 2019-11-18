from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.response import Response











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
