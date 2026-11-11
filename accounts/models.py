from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Create users using email instead of a username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The email address is required."))
        user = self.model(email=email.strip().casefold(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", _("Student")
        INVESTOR = "investor", _("Investor/Expert")

    username = None
    name = models.CharField(_("name"), max_length=150)
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(_("role"), max_length=20, choices=Role.choices)
    demo_key = models.CharField(
        _("demo key"), max_length=100, unique=True, null=True, blank=True, editable=False
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "role"]

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
            ),
            models.CheckConstraint(
                condition=Q(role__in=["student", "investor"]),
                name="accounts_user_valid_role",
            ),
        ]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().casefold()
        super().save(*args, **kwargs)

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_investor(self):
        return self.role == self.Role.INVESTOR


class Skill(models.Model):
    name = models.CharField(_("name"), max_length=100)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="accounts_skill_name_ci_unique",
            ),
        ]

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    bio = models.TextField(_("bio"), blank=True)
    skills = models.ManyToManyField(
        Skill,
        verbose_name=_("skills"),
        related_name="profiles",
    )
    portfolio_projects = models.JSONField(
        _("portfolio projects"), blank=True, default=list
    )
    experience = models.JSONField(_("experience"), blank=True, default=list)

    def clean(self):
        super().clean()
        if self.user_id and not self.user.is_student:
            raise ValidationError(
                {"user": _("Only student accounts can have a student profile.")}
            )

    def __str__(self):
        return f"{self.user} profile"
