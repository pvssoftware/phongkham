from django.conf.urls import url
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import (RedirectView, TemplateView)
from .views import LoginViewMix, CreateAccount, ActivateAccount, ResendActivationEmail, license_page, verify_email
from .forms import SetPasswordFormMix




urlpatterns = [

    url(r"^verify-email/$",verify_email,name="verify_email"),
    url(r"^license/$",license_page,name="license"),
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
    url(r'^create-account/$',
        CreateAccount.as_view(),
        name='create_account'),
    url(r'^create-account-done/$',
        TemplateView.as_view(
            template_name=('user/create_account_done.html')),
        name='create_account_done'),
    url(r'^activate/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}'
        r'-[0-9A-Za-z]{1,20})/$',
        ActivateAccount.as_view(),
        name='activate'),
    url(r'^activate/resend/$',
        ResendActivationEmail.as_view(),
        name='resend_activation'),
    url(r'^activate',
        RedirectView.as_view(
            pattern_name=(
                'resend_activation'),
            permanent=False)),
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='user/password_reset_form.html',
            email_template_name='user/password_reset_email.txt',
            subject_template_name='user/password_reset_subject.txt',
            success_url=reverse_lazy('pw_reset_send_email_success'),
            from_email="tech@pvs.com.vn"),
        name='pw_reset_form'),
    url(r'^reset/sent-email-success/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/password_reset_send_email_success.html'),
        name='pw_reset_send_email_success'),
    url(r'^reset/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}'
        r'-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html',
            form_class = SetPasswordFormMix,
            success_url=reverse_lazy(
                'pw_reset_complete')),
        name='pw_reset_confirm'),
    url(r'reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/password_reset_complete.html'),
        name='pw_reset_complete')

]