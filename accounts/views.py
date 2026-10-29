from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .forms import EmailAuthenticationForm, SignUpForm


class AccountLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = False
    next_page = reverse_lazy("ideas:home")


def signup(request):
    if request.user.is_authenticated:
        return redirect("ideas:home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _("Your account has been created successfully."))
        return redirect("ideas:home")
    return render(request, "registration/signup.html", {"form": form})


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("ideas:home")
