"""Healthy_Care URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from user import urls as user_urls
from user.vnpay import urls_vnpay
from user.views import LoginViewMix
from doctors import urls as doctor_urls
from doctors import urls_api as doctor_api

urlpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'^$', LoginViewMix.as_view(), name='login'),
    url(r"^user/", include(user_urls)),
    url(r"^payment-license/", include(urls_vnpay)),
    url(r"^doctor/", include(doctor_urls)),
    url(r"^doctor-api/api/", include(doctor_api)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)