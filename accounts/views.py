import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import EmailAuthenticationForm, ProfileEntryFormSet, SignUpForm, StudentProfileForm
from .models import Follow, StudentProfile
from .profile_entries import present_entries

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

    editor_submission = request.method == "POST" and request.POST.get("profile_entries_editor") == "1"
    projects = ProfileEntryFormSet(
        request.POST if editor_submission else None,
        entries=profile.portfolio_projects, kind="project", prefix="projects",
    )
    experience = ProfileEntryFormSet(
        request.POST if editor_submission else None,
        entries=profile.experience, kind="experience", prefix="experience",
    )
    data = request.POST if request.method == "POST" else None
    entries_valid = True
    if editor_submission:
        entries_valid = all([projects.is_valid(), experience.is_valid()])
        data = request.POST.copy()
        data["portfolio_projects"] = json.dumps(projects.to_entries() if entries_valid else profile.portfolio_projects)
        data["experience"] = json.dumps(experience.to_entries() if entries_valid else profile.experience)
    form = StudentProfileForm(data, instance=profile)
    if request.method == "POST" and form.is_valid() and entries_valid:
        with transaction.atomic():
            form.save()
        messages.success(request, _("Your profile has been saved."))
        return redirect("accounts:student_profile")

    return render(
        request,
        "accounts/student_profile_form.html",
        {"form": form, "profile": profile, "profile_fields": [form["bio"], form["skills"]],
         "projects_formset": projects, "experience_formset": experience},
    )


def _profile_display_context(student):
    profile = (
        StudentProfile.objects.filter(user=student)
        .prefetch_related("skills")
        .first()
    )

    return {
        "student": student,
        "profile": profile,
        "skills": profile.skills.all() if profile else [],
        "portfolio_projects": present_entries(profile.portfolio_projects, "project") if profile else [],
        "experience_entries": present_entries(profile.experience, "experience") if profile else [],
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
    context["is_following"] = Follow.objects.filter(
        investor=request.user, student=student
    ).exists()
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
    if request.POST.get("source") == "following":
        return redirect("accounts:following")
    return redirect("accounts:investor_profile", student_id=student.pk)


@login_required(login_url=reverse_lazy("accounts:login"))
@require_GET
def following(request):
    if not request.user.is_investor:
        raise PermissionDenied

    follows = (
        Follow.objects.filter(investor=request.user, student__role=User.Role.STUDENT)
        .select_related("student", "student__student_profile")
        .prefetch_related("student__student_profile__skills")
    )
    return render(request, "accounts/following.html", {"follows": follows})
