from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Skill, StudentProfile, User


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


class JSONListField(forms.JSONField):
    """Accept JSON arrays and normalize blank complete-form values to a list."""

    default_error_messages = {
        **forms.JSONField.default_error_messages,
        "invalid_list": _("Enter a JSON array."),
    }

    class ListTextarea(forms.Textarea):
        def value_omitted_from_data(self, data, files, name):
            # An omitted optional list in a complete form means [], rather
            # than "leave the existing model value unchanged".
            return False

    widget = ListTextarea(attrs={"rows": 4})

    def bound_data(self, data, initial):
        if data in self.empty_values:
            return []
        return super().bound_data(data, initial)

    def to_python(self, value):
        if value in self.empty_values:
            return []
        value = super().to_python(value)
        if not isinstance(value, list):
            raise ValidationError(self.error_messages["invalid_list"], code="invalid_list")
        return value


class OptionalSkillChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        if value in self.empty_values or value == [""]:
            value = []
        return super().clean(value)


class StudentProfileForm(BootstrapFormMixin, forms.ModelForm):
    skills = OptionalSkillChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        widget=forms.SelectMultiple,
    )
    portfolio_projects = JSONListField(
        required=False,
    )
    experience = JSONListField(
        required=False,
    )

    class Meta:
        model = StudentProfile
        fields = ("bio", "skills", "portfolio_projects", "experience")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skills"].queryset = Skill.objects.all()
        self.fields["portfolio_projects"].help_text = _(
            "Enter a JSON array. Items may be any JSON values; leave blank if there are none."
        )
        self.fields["experience"].help_text = _(
            "Enter a JSON array. Items may be any JSON values; leave blank if there are none."
        )
        if not self.fields["skills"].queryset.exists():
            self.fields["skills"].help_text = _("No skills are available to select yet.")

    def _update_errors(self, errors):
        # StudentProfile.clean() reports an invalid role on its excluded user
        # field. Surface that model error as a form-level error instead.
        if hasattr(errors, "error_dict") and "user" in errors.error_dict:
            error_dict = errors.error_dict.copy()
            error_dict[NON_FIELD_ERRORS] = error_dict.pop("user")
            errors = ValidationError(error_dict)
        super()._update_errors(errors)
