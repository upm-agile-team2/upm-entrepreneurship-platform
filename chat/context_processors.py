from django.db.models import Q

from .models import Message


def unread_message_count(request):
    if not request.user.is_authenticated:
        return {"unread_message_count": 0}

    return {
        "unread_message_count": Message.objects.filter(
            conversation__participants=request.user,
            is_read=False,
        )
        .filter(Q(sender__isnull=True) | ~Q(sender=request.user))
        .distinct()
        .count()
    }
