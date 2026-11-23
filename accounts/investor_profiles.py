from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .forms import InvestorProfileForm
from .models import InvestorProfile


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
        return redirect("accounts:edit_investor_profile")

    return render(
        request, "accounts/investor_profile_form.html", {"form": form, "profile": profile}
    )
