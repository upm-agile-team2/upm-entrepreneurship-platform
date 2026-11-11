from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import FeedbackForm, IdeaForm, ReplyForm
from .models import Category, Feedback, Idea, Reply


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


def idea_detail(request, idea_id):
    idea = get_object_or_404(
        Idea.objects.select_related("category", "owner"),
        pk=idea_id,
    )
    visible_feedback = Feedback.objects.select_related("author").prefetch_related(
        Prefetch(
            "replies",
            queryset=Reply.objects.select_related("author"),
        )
    ).filter(idea=idea)
    if not request.user.is_authenticated:
        visible_feedback = visible_feedback.filter(is_private=False)
    elif idea.owner_id == request.user.pk:
        pass
    else:
        visible_feedback = visible_feedback.filter(
            Q(is_private=False) | Q(is_private=True, author=request.user)
        )
    can_edit = (
        request.user.is_authenticated
        and request.user.is_student
        and idea.owner_id == request.user.pk
    )
    can_submit_feedback = (
        request.user.is_authenticated and request.user.is_investor
    )
    return render(
        request,
        "ideas/idea_detail.html",
        {
            "idea": idea,
            "can_edit": can_edit,
            "can_submit_feedback": can_submit_feedback,
            "feedback_items": visible_feedback,
            "feedback_form": FeedbackForm(),
            "reply_form": None,
        },
    )


@login_required(login_url=reverse_lazy("accounts:login"))
def submit_feedback(request, idea_id):
    if not request.user.is_investor:
        raise PermissionDenied
    idea = get_object_or_404(Idea, pk=idea_id)
    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.idea = idea
        feedback.author = request.user
        feedback.save()
        messages.success(request, _("Your feedback has been submitted."))
        return redirect("ideas:detail", idea_id=idea.pk)
    return _render_idea_detail_with_feedback_form(request, idea, form)


@login_required(login_url=reverse_lazy("accounts:login"))
def submit_reply(request, feedback_id):
    feedback = get_object_or_404(
        Feedback.objects.select_related("idea"),
        pk=feedback_id,
    )
    if not request.user.is_student or feedback.idea.owner_id != request.user.pk:
        raise PermissionDenied
    form = ReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.feedback = feedback
        reply.author = request.user
        reply.save()
        messages.success(request, _("Your reply has been submitted."))
        return redirect("ideas:detail", idea_id=feedback.idea_id)
    return _render_idea_detail_with_reply_form(request, feedback.idea, feedback, form)


@login_required(login_url=reverse_lazy("accounts:login"))
def toggle_feedback_status(request, feedback_id):
    if request.method != "POST":
        raise PermissionDenied
    feedback = get_object_or_404(
        Feedback.objects.select_related("idea"),
        pk=feedback_id,
    )
    if not request.user.is_student or feedback.idea.owner_id != request.user.pk:
        raise PermissionDenied
    feedback.status = (
        Feedback.Status.NORMAL
        if feedback.status == Feedback.Status.RESOLVED
        else Feedback.Status.RESOLVED
    )
    feedback.save(update_fields=["status"])
    return redirect("ideas:detail", idea_id=feedback.idea_id)


def _visible_feedback(idea, user):
    feedback = Feedback.objects.select_related("author").prefetch_related(
        Prefetch("replies", queryset=Reply.objects.select_related("author"))
    ).filter(idea=idea)
    if not user.is_authenticated:
        return feedback.filter(is_private=False)
    if idea.owner_id == user.pk:
        return feedback
    return feedback.filter(Q(is_private=False) | Q(is_private=True, author=user))


def _render_idea_detail_with_feedback_form(request, idea, form):
    return render(
        request,
        "ideas/idea_detail.html",
        {
            "idea": idea,
            "can_edit": request.user.is_student and idea.owner_id == request.user.pk,
            "can_submit_feedback": request.user.is_investor,
            "feedback_items": _visible_feedback(idea, request.user),
            "feedback_form": form,
            "reply_form": None,
        },
    )


def _render_idea_detail_with_reply_form(request, idea, feedback, form):
    return render(
        request,
        "ideas/idea_detail.html",
        {
            "idea": idea,
            "can_edit": request.user.is_student and idea.owner_id == request.user.pk,
            "can_submit_feedback": request.user.is_investor,
            "feedback_items": _visible_feedback(idea, request.user),
            "feedback_form": FeedbackForm(),
            "reply_form": form,
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
