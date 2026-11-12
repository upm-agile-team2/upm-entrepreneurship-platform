"""Student-profile discovery for US012."""

from django import forms
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from .forms import BootstrapFormMixin
from .models import Skill, StudentProfile, User


class StudentProfileFilterForm(BootstrapFormMixin, forms.Form):
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.order_by(Lower("name"), "pk"),
        required=False,
        empty_label=_("All skills"),
        label=_("Skill or expertise"),
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
