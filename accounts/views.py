import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import EmailAuthenticationForm, SignUpForm, StudentProfileForm
from .models import Follow, StudentProfile

User = get_user_model()


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


def _profile_display_context(student):
    profile = (
        StudentProfile.objects.filter(user=student)
        .prefetch_related("skills")
        .first()
    )

    def format_entries(values):
        if not isinstance(values, list):
            return []
        return [json.dumps(value, ensure_ascii=False, indent=2) for value in values]

    return {
        "student": student,
        "profile": profile,
        "skills": profile.skills.all() if profile else [],
        "portfolio_projects": format_entries(profile.portfolio_projects) if profile else [],
        "experience_entries": format_entries(profile.experience) if profile else [],
    }


@require_GET
@login_required(login_url=reverse_lazy("accounts:login"))
def my_profile(request):
    if not request.user.is_student:
        raise PermissionDenied

    context = _profile_display_context(request.user)
    context["is_own_profile"] = True
    return render(request, "accounts/student_profile_detail.html", context)


@require_GET
@login_required(login_url=reverse_lazy("accounts:login"))
def investor_profile(request, student_id):
    if not request.user.is_investor:
        raise PermissionDenied

    student = get_object_or_404(
        User.objects.filter(role=User.Role.STUDENT),
        pk=student_id,
    )
    context = _profile_display_context(student)
    context["is_own_profile"] = False
    return render(request, "accounts/student_profile_detail.html", context)

@login_required(login_url=reverse_lazy("accounts:login"))
@require_POST
def follow_student(request, student_id):
    if not request.user.is_investor:
        raise PermissionDenied

    student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
    follow, created = Follow.objects.get_or_create(investor=request.user, student=student)
    if created:
        messages.success(request, _("You are now following %(name)s.") % {"name": student.name})
    return redirect("accounts:investor_profile", student_id=student.pk)


@login_required(login_url=reverse_lazy("accounts:login"))
@require_POST
def unfollow_student(request, student_id):
    if not request.user.is_investor:
        raise PermissionDenied

    student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
    deleted, details = Follow.objects.filter(investor=request.user, student=student).delete()
    if deleted:
        messages.success(request, _("You have unfollowed %(name)s.") % {"name": student.name})
    return redirect("accounts:investor_profile", student_id=student.pk)
