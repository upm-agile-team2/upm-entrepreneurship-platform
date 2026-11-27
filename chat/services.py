"""Services for creating and finding direct conversations."""

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Conversation

User = get_user_model()


class InvalidConversationParticipants(ValueError):
    """Raised when a direct conversation cannot be created for the given users."""


def get_or_create_conversation(first_user, second_user):
    """Return the direct conversation for two active users, creating it if needed."""
    if (
        first_user.pk is None
        or second_user.pk is None
        or first_user.pk == second_user.pk
    ):
        raise InvalidConversationParticipants("Choose another user to start a conversation.")
    participant_ids = sorted((first_user.pk, second_user.pk))

    with transaction.atomic():
        participants = list(
            User.objects.select_for_update()
            .filter(pk__in=participant_ids, is_active=True)
            .order_by("pk")
        )
        if len(participants) != 2:
            raise InvalidConversationParticipants("Both participants must be active users.")

        possible_conversations = (
            Conversation.objects.filter(participants__in=participants)
            .distinct()
            .prefetch_related("participants")
        )
        expected_ids = set(participant_ids)
        for conversation in possible_conversations:
            existing_ids = {participant.pk for participant in conversation.participants.all()}
            if existing_ids == expected_ids:
                return conversation, False

        conversation = Conversation.objects.create()
        conversation.participants.add(*participants)
        return conversation, True
