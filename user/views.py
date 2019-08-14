from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
# Create your views here.


def login(request):
    return render(request, "user/login.html", {})


class LoginViewMix(LoginView):
    template_name = "user/login.html"

    def get_success_url(self):
        user = self.request.user
        return reverse_lazy("doctor_profile",kwargs={"pk_doctor":user.pk})
        if user.doctor:
            return reverse_lazy("doctor_profile",kwargs={"pk_doctor":user.pk})
    # def get(self,request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect("doctor_profile")
    #     else:
    #         return self.render_to_response(self.get_context_data())

