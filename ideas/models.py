from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import F, Q
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
    class DevelopmentStage(models.TextChoices):
        IDEA = "idea", _("Idea")
        PROTOTYPE = "prototype", _("Prototype")
        MVP = "mvp", _("MVP")
        LAUNCHED = "launched", _("Launched")
        GROWTH = "growth", _("Growth")

    class SupportType(models.TextChoices):
        FUNDING = "funding", _("Funding")
        TECHNICAL_SUPPORT = "technical_support", _("Technical support")
        MENTORING = "mentoring", _("Mentoring")
        MARKETING = "marketing", _("Marketing")
        TEAM_MEMBERS = "team_members", _("Team members")

    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"))
    development_stage = models.CharField(
        _("development stage"),
        max_length=20,
        choices=DevelopmentStage.choices,
        blank=True,
        default="",
    )
    required_support = models.JSONField(
        _("required support"), blank=True, default=list
    )
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
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("collaborators"),
        through="Collaborator",
        through_fields=("idea", "collaborator"),
        related_name="collaborating_ideas",
        blank=True,
    )

    class Meta:
        ordering = ["-published_at"]

    @property
    def required_support_labels(self):
        values = self.required_support if isinstance(self.required_support, list) else []
        return [label for value, label in self.SupportType.choices if value in values]

    def clean(self):
        super().clean()
        if not isinstance(self.required_support, list):
            raise ValidationError(
                {"required_support": _("Support needs must be a list.")}
            )
        if any(
            not isinstance(value, str) or value not in self.SupportType.values
            for value in self.required_support
        ):
            raise ValidationError(
                {"required_support": _("Select valid support types.")}
            )
        if len(self.required_support) != len(set(self.required_support)):
            raise ValidationError(
                {"required_support": _("Select each support type only once.")}
            )

    def __str__(self):
        return self.title


class Collaborator(models.Model):
    idea = models.ForeignKey(
        Idea,
        verbose_name=_("idea"),
        on_delete=models.CASCADE,
        related_name="collaborator_memberships",
    )
    collaborator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("collaborator"),
        on_delete=models.CASCADE,
        related_name="idea_collaborations",
    )
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        ordering = ["-timestamp", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["idea", "collaborator"],
                name="ideas_collab_unique_pair",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        # full_clean() reports missing/invalid foreign keys separately.
        try:
            collaborator = self.collaborator
        except ObjectDoesNotExist:
            collaborator = None
        try:
            idea = self.idea
        except ObjectDoesNotExist:
            idea = None

        if collaborator is not None and not collaborator.is_student:
            errors["collaborator"] = _("Only students can be project collaborators.")
        if idea is not None and self.collaborator_id == idea.owner_id:
            errors["collaborator"] = _(
                "The project owner cannot be added as a collaborator."
            )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.collaborator} collaborates on {self.idea}"


class CollaboratorRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        REJECTED = "rejected", _("Rejected")

    idea = models.ForeignKey(
        Idea,
        verbose_name=_("idea"),
        on_delete=models.CASCADE,
        related_name="collaborator_requests",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("sender"),
        on_delete=models.CASCADE,
        related_name="sent_collaborator_requests",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("receiver"),
        on_delete=models.CASCADE,
        related_name="received_collaborator_requests",
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        ordering = ["-timestamp", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["idea", "receiver"],
                name="ideas_request_unique_pair",
            ),
            models.CheckConstraint(
                condition=~Q(sender=F("receiver")),
                name="ideas_request_not_self",
            ),
            models.CheckConstraint(
                condition=Q(status__in=["pending", "accepted", "rejected"]),
                name="ideas_request_valid_status",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        try:
            idea = self.idea
        except ObjectDoesNotExist:
            idea = None
        try:
            sender = self.sender
        except ObjectDoesNotExist:
            sender = None
        try:
            receiver = self.receiver
        except ObjectDoesNotExist:
            receiver = None

        if sender is not None and not sender.is_student:
            errors["sender"] = _("Only students can send collaborator requests.")
        if idea is not None and self.sender_id is not None:
            if self.sender_id != idea.owner_id:
                errors["sender"] = _("Only the project owner can invite collaborators.")
        if receiver is not None and not receiver.is_student:
            errors["receiver"] = _("Only students can receive collaborator requests.")
        if self.sender_id is not None and self.sender_id == self.receiver_id:
            errors["receiver"] = _("You cannot send a collaborator request to yourself.")
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.sender} invites {self.receiver} to {self.idea}"


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
    class Type(models.TextChoices):
        FEEDBACK_RECEIVED = "feedback_received", _("Feedback received")
        IDEA_PUBLISHED = "idea_published", _("Idea published")
        FEEDBACK_REPLY = "feedback_reply", _("Feedback reply")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("recipient"),
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    feedback = models.ForeignKey(
        Feedback,
        verbose_name=_("feedback"),
        null=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    idea = models.ForeignKey(
        Idea,
        verbose_name=_("idea"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    reply = models.OneToOneField(
        Reply,
        verbose_name=_("reply"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notification",
    )
    type = models.CharField(
        _("type"),
        max_length=30,
        choices=Type.choices,
        default=Type.FEEDBACK_RECEIVED,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    is_read = models.BooleanField(_("read"), default=False)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        type="feedback_received",
                        feedback__isnull=False,
                        idea__isnull=True,
                        reply__isnull=True,
                    )
                    | Q(
                        type="idea_published",
                        feedback__isnull=True,
                        idea__isnull=False,
                        reply__isnull=True,
                    )
                    | Q(
                        type="feedback_reply",
                        feedback__isnull=True,
                        idea__isnull=True,
                        reply__isnull=False,
                    )
                ),
                name="ideas_notification_target_matches_type",
            ),
        ]

    def __str__(self):
        return f"{self.get_type_display()} notification for {self.recipient}"
