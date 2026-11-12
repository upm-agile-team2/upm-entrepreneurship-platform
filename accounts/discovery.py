"""Student-profile discovery for US012."""

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Lower
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET

from .forms import BootstrapFormMixin
from .models import Skill, StudentProfile, User


class StudentProfileFilterForm(BootstrapFormMixin, forms.Form):
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.order_by(Lower("name"), "pk"),
        required=False,
        empty_label=_("All skills"),
        label=_("Skill or expertise"),
        help_text=_("Choose one skill to find matching students."),
        error_messages={"invalid_choice": _("Choose a skill from the list.")},
    )


def student_profiles(skill=None):
    """Return saved profiles of active students, optionally matching one skill."""
    profiles = StudentProfile.objects.filter(
        user__is_active=True,
        user__role=User.Role.STUDENT,
    )
    if skill is not None:
        profiles = profiles.filter(skills=skill)
    return (
        profiles.select_related("user")
        .prefetch_related("skills")
        .order_by(Lower("user__name"), "user_id")
    )


@require_GET
@login_required(login_url=reverse_lazy("accounts:login"))
def student_discovery(request):
    if not request.user.is_investor:
        raise PermissionDenied

    form = StudentProfileFilterForm(request.GET or None)
    selected_skill = None
    profiles = student_profiles()
    if form.is_bound:
        if form.is_valid():
            selected_skill = form.cleaned_data["skill"]
            profiles = student_profiles(selected_skill)
        else:
            profiles = profiles.none()

    if not form.fields["skill"].queryset.exists():
        form.fields["skill"].help_text = _("No skills are available to filter yet.")
    profiles = list(profiles)
    return render(request, "accounts/student_discovery.html", {
        "filter_form": form,
        "profiles": profiles,
        "profile_count": len(profiles),
        "selected_skill": selected_skill,
        "has_filter": bool(request.GET.get("skill")),
    })
