from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import LoginViewMix




urlpatterns = [
    url(r"^login/$",LoginViewMix.as_view(),name="login"),
    url(r'^logout/$',
        auth_views.LogoutView.as_view(),
        name='logout'),
]