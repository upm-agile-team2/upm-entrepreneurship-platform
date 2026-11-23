from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_http_methods

from ideas.models import Feedback

from .forms import BootstrapFormMixin, InvestorProfileForm
from .models import InvestorInterest, InvestorProfile, User


class InvestorInterestFilterForm(BootstrapFormMixin, forms.Form):
    interest = forms.ModelChoiceField(
        queryset=InvestorInterest.objects.all(),
        required=False,
        empty_label=_("All interests"),
        label=_("Interest or area of expertise"),
        error_messages={"invalid_choice": _("Choose an interest from the list.")},
    )


def _active_investor_profiles():
    return InvestorProfile.objects.filter(
        user__is_active=True, user__role=User.Role.INVESTOR
    ).select_related("user").prefetch_related("interests")


def find_investor_profiles(interest=None):
    profiles = _active_investor_profiles()
    if interest is not None:
        profiles = profiles.filter(interests=interest)
    return profiles.order_by(Lower("user__name"), "user_id")


@require_GET
@login_required(login_url=reverse_lazy("accounts:login"))
def investor_profile_detail(request, investor_id):
    if not request.user.is_student:
        raise PermissionDenied

    profile = get_object_or_404(_active_investor_profiles(), user_id=investor_id)
    public_feedback = (
        Feedback.objects.filter(author_id=investor_id, is_private=False)
        .select_related("idea")
        .order_by("-timestamp", "-pk")
    )
    return render(
        request,
        "accounts/investor_profile_detail.html",
        {"investor": profile.user, "profile": profile, "public_feedback": public_feedback},
    )


@require_GET
@login_required(login_url=reverse_lazy("accounts:login"))
def my_investor_profile(request):
    if not request.user.is_investor:
        raise PermissionDenied

    profile = InvestorProfile.objects.filter(user=request.user).prefetch_related("interests").first()
    return render(
        request,
        "accounts/investor_profile_detail.html",
        {"investor": request.user, "profile": profile, "is_own_profile": True},
    )


@require_http_methods(["GET", "POST"])
@login_required(login_url=reverse_lazy("accounts:login"))
def edit_investor_profile(request):
    if not request.user.is_investor:
        raise PermissionDenied

    profile = InvestorProfile.objects.filter(user=request.user).first()
    form = InvestorProfileForm(
        request.POST if request.method == "POST" else None, instance=profile
    )
    if request.method == "POST" and form.is_valid():
        form.save_for(request.user)
        messages.success(request, _("Your profile has been saved."))
        return redirect("accounts:my_investor_profile")

    return render(
        request, "accounts/investor_profile_form.html", {"form": form, "profile": profile}
    )
