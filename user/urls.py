from django.conf.urls import url
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .views import LoginViewMix




urlpatterns = [
    url(r"^login/$",LoginViewMix.as_view(),name="login"),
    url(r'^logout/$',
        auth_views.LogoutView.as_view(),
        name='logout'),
    url(r'^change/$',
        auth_views.PasswordChangeView.as_view(
            template_name='user/password_change_form.html',
            success_url=reverse_lazy(
                'pw_change_done')),
        name='pw_change'),
    url(r'^change/done/$',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='user/password_change_done.html'),
        name='pw_change_done'),
]