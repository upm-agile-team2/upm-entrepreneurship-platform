from django.conf import settings
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("name"), max_length=100)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="ideas_category_name_ci_unique",
            ),
        ]

    def __str__(self):
        return self.name


class Idea(models.Model):
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"))
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ideas",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
        related_name="ideas",
    )
    published_at = models.DateTimeField(_("published at"), auto_now_add=True)
    demo_key = models.CharField(
        _("demo key"), max_length=100, unique=True, null=True, blank=True, editable=False
    )

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class Feedback(models.Model):
    class Status(models.TextChoices):
        NORMAL = "normal", _("Normal")
        RESOLVED = "resolved", _("Resolved")

    idea = models.ForeignKey(
        Idea,
        verbose_name=_("idea"),
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="feedback",
    )
    text = models.TextField(_("text"), blank=False)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    is_private = models.BooleanField(_("private"), default=False)
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.NORMAL,
    )

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Feedback on {self.idea}"


class Reply(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        verbose_name=_("feedback"),
        on_delete=models.CASCADE,
        related_name="replies",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="feedback_replies",
    )
    text = models.TextField(_("text"), blank=False)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Reply to {self.feedback}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("recipient"),
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    feedback = models.ForeignKey(
        Feedback,
        verbose_name=_("feedback"),
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    is_read = models.BooleanField(_("read"), default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.recipient} about {self.feedback}"
