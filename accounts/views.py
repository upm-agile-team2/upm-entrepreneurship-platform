from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .forms import EmailAuthenticationForm, SignUpForm, StudentProfileForm
from .models import StudentProfile


class AccountLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = False
    next_page = reverse_lazy("ideas:home")


def signup(request):
    if request.user.is_authenticated:
        return redirect("ideas:home")
    form = SignUpForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _("Your account has been created successfully."))
        return redirect("ideas:home")
    return render(request, "registration/signup.html", {"form": form})


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("ideas:home")


@require_http_methods(["GET", "POST"])
@login_required(login_url=reverse_lazy("accounts:login"))
def student_profile(request):
    if not request.user.is_student:
        raise PermissionDenied

    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile(user=request.user)

    form = StudentProfileForm(
        request.POST if request.method == "POST" else None,
        instance=profile,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:student_profile")

    return render(
        request,
        "accounts/student_profile_form.html",
        {"form": form, "profile": profile},
    )
