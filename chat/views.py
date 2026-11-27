from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import MessageForm, StartConversationForm
from .models import Conversation, Message
from .services import InvalidConversationParticipants, get_or_create_conversation

User = get_user_model()


def _conversation_list(user):
    latest_message_at = (
        Message.objects.filter(conversation_id=OuterRef("pk"))
        .order_by("-timestamp", "-pk")
        .values("timestamp")[:1]
    )
    unread_messages = Q(messages__is_read=False) & (
        Q(messages__sender__isnull=True) | ~Q(messages__sender=user)
    )
    return (
        Conversation.objects.filter(participants=user)
        .distinct()
        .annotate(
            last_activity=Coalesce(Subquery(latest_message_at), "created_at"),
            unread_count=Count("messages", filter=unread_messages, distinct=True),
        )
        .prefetch_related(
            Prefetch("participants", queryset=User.objects.order_by("name", "pk")),
            Prefetch(
                "messages",
                queryset=Message.objects.select_related("sender").order_by(
                    "-timestamp", "-pk"
                )[:1],
                to_attr="latest_messages",
            ),
        )
        .order_by("-last_activity", "-pk")
    )


@login_required(login_url=reverse_lazy("accounts:login"))
@require_GET
def conversation_list(request):
    return render(
        request,
        "chat/conversation_list.html",
        {
            "conversations": _conversation_list(request.user),
            "start_form": StartConversationForm(user=request.user),
            "selected_conversation": None,
        },
    )


@login_required(login_url=reverse_lazy("accounts:login"))
@require_POST
def start_conversation(request):
    form = StartConversationForm(request.POST, user=request.user)
    if form.is_valid():
        try:
            conversation, _created = get_or_create_conversation(
                request.user, form.cleaned_data["recipient"]
            )
        except InvalidConversationParticipants:
            form.add_error("recipient", _("Choose another active account."))
        else:
            return redirect("chat:detail", conversation_id=conversation.pk)

    return render(
        request,
        "chat/conversation_list.html",
        {
            "conversations": _conversation_list(request.user),
            "start_form": form,
            "selected_conversation": None,
        },
    )


@login_required(login_url=reverse_lazy("accounts:login"))
@require_http_methods(["GET", "POST"])
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=request.user)
        .distinct()
        .prefetch_related(
            Prefetch("participants", queryset=User.objects.order_by("name", "pk")),
            Prefetch(
                "messages",
                queryset=Message.objects.select_related("sender").order_by(
                    "timestamp", "pk"
                ),
            ),
        ),
        pk=conversation_id,
    )
    conversation.messages.filter(is_read=False).filter(
        Q(sender__isnull=True) | ~Q(sender=request.user)
    ).update(is_read=True)
    form = MessageForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect("chat:detail", conversation_id=conversation.pk)
        form.fields["text"].widget.attrs.update(
            {"aria-invalid": "true", "aria-describedby": "id_text_error"}
        )

    other_participants = [
        participant
        for participant in conversation.participants.all()
        if participant.pk != request.user.pk
    ]
    return render(
        request,
        "chat/conversation_detail.html",
        {
            "conversation": conversation,
            "selected_conversation": conversation,
            "conversations": _conversation_list(request.user),
            "start_form": StartConversationForm(user=request.user),
            "other_participants": other_participants,
            "chat_messages": conversation.messages.all(),
            "form": form,
        },
    )
