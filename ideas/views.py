from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import IdeaForm


def home(request):
    # Placeholder start page; it becomes the discovery page in T15 (US003).
    return render(request, "ideas/home.html")


@login_required(login_url=reverse_lazy("accounts:login"))
def publish_idea(request):
    if not request.user.is_student:
        raise PermissionDenied
    form = IdeaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        idea = form.save(commit=False)
        idea.owner = request.user
        idea.save()
        messages.success(request, _("Your idea has been published."))
        return redirect("ideas:home")
    return render(request, "ideas/idea_form.html", {"form": form})
