from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("participants"),
        related_name="conversations",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conversation {self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        verbose_name=_("conversation"),
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("sender"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="sent_messages",
    )
    text = models.TextField(_("text"), blank=False)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    is_read = models.BooleanField(_("is read"), default=False)

    class Meta:
        ordering = ["timestamp", "id"]

    def __str__(self):
        return f"Message from {self.sender} in {self.conversation}"
