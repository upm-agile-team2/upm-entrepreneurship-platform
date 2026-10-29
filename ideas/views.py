from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import IdeaForm
from .models import Category, Idea


def home(request):
    ideas = Idea.objects.select_related("category", "owner")
    category_id = request.GET.get("category")
    selected_category = None
    if category_id:
        selected_category = (
            Category.objects.filter(pk=category_id).first()
            if category_id.isdigit()
            else None
        )
        ideas = ideas.filter(category=selected_category) if selected_category else ideas.none()

    return render(
        request,
        "ideas/home.html",
        {
            "ideas": ideas,
            "categories": Category.objects.all(),
            "selected_category": selected_category,
        },
    )


@login_required(login_url=reverse_lazy("accounts:login"))
def publish_idea(request):
    if not request.user.is_student:
        raise PermissionDenied
    form = IdeaForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        idea = form.save(commit=False)
        idea.owner = request.user
        idea.save()
        messages.success(request, _("Your idea has been published."))
        return redirect("ideas:home")
    return render(
        request,
        "ideas/idea_form.html",
        {"form": form, "heading": _("Publish an idea"), "submit_label": _("Publish")},
    )


@login_required(login_url=reverse_lazy("accounts:login"))
def edit_idea(request, idea_id):
    if not request.user.is_student:
        raise PermissionDenied

    idea = get_object_or_404(Idea, pk=idea_id)
    if idea.owner_id != request.user.pk:
        raise PermissionDenied

    form = IdeaForm(
        request.POST if request.method == "POST" else None,
        instance=idea,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Your idea has been updated."))
        return redirect("ideas:home")
    return render(
        request,
        "ideas/idea_form.html",
        {"form": form, "heading": _("Edit idea"), "submit_label": _("Save changes")},
    )
