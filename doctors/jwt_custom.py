# from datetime import datetime
# from django.conf import settings
# from django.utils.timezone import is_naive, make_aware
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.views import TokenObtainPairView

# def make_utc(dt):
#     if settings.USE_TZ and is_naive(dt):
#         return make_aware(dt)
#     return dt


# def datetime_from_epoch(ts):
#     return make_utc(datetime.utcfromtimestamp(ts))



# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         token = self.get_token(self.user)
#         data["maPK"] = self.user.pk
#         data["dcPK"] = self.user.doctor.clinic_address
#         data["soDT"] = self.user.doctor.phone
#         data["tenBS"] = self.user.doctor.full_name
#         data["loaiBS"] = self.user.doctor.get_kind_display()
#         data["expired_date"] = datetime_from_epoch(token["exp"]).strftime("%d/%m/%Y %H:%M")

#         return data


# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer