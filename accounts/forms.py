from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class BootstrapFormMixin:
    """Keep authentication widgets consistent with the shared form presentation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            style = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = style


class EmailAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip().casefold()


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("name", "email", "role", "password1", "password2")
        labels = {
            "name": _("Name"),
            "email": _("Email"),
            "role": _("Role"),
        }
        help_texts = {"role": _("Choose the type of account you want to create.")}
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise ValidationError(_("Name is required."))
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().casefold()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _("This email is already registered. Please sign in or use another address.")
            )
        return email
