from copy import deepcopy

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from .models import Skill, StudentProfile, User
from .profile_entries import ENTRY_FIELDS, entry_fields, present_entry


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


class ProfileEntryForm(BootstrapFormMixin, forms.Form):
    heading = forms.CharField(required=False)
    organization = forms.CharField(required=False, label=_("Organization"))
    period = forms.CharField(required=False, label=_("Period"))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    url = forms.CharField(required=False, label=_("Project link"), widget=forms.URLInput)

    def __init__(self, *args, kind, original=None, is_existing=False, **kwargs):
        self.kind = kind
        self.original = original
        self.is_existing = is_existing
        self.read_only_entry = is_existing and not isinstance(original, (dict, str))
        initial, self.entry_keys = entry_fields(original, kind)
        kwargs.setdefault("initial", initial)
        super().__init__(*args, **kwargs)
        self.preview = present_entry(original, kind) if is_existing else None
        for field_name in list(self.fields):
            if self.read_only_entry or field_name not in ENTRY_FIELDS[kind]:
                del self.fields[field_name]
        if not self.read_only_entry:
            self.fields["heading"].label = _("Project title") if kind == "project" else _("Role")
        if "url" in self.fields:
            self.fields["url"].help_text = _("A full link starting with https:// or http://.")
        if "period" in self.fields:
            self.fields["period"].widget.attrs["placeholder"] = _("For example, 2025–2026")

    def clean_url(self):
        value = self.cleaned_data["url"]
        if value and (not self.is_existing or value != self.initial.get("url", "")):
            try:
                URLValidator(schemes=["http", "https"])(value)
            except ValidationError:
                raise ValidationError(_("Enter a full link starting with https:// or http://."))
        return value

    def clean(self):
        data = super().clean()
        if not self.read_only_entry and self.has_changed() and not data.get("heading"):
            message = _("Enter a project title or remove this entry.") if self.kind == "project" else _("Enter a role or remove this entry.")
            self.add_error("heading", message)
        return data

    def to_entry(self):
        if self.read_only_entry or (self.is_existing and not self.has_changed()):
            return deepcopy(self.original)
        if isinstance(self.original, str) and not any(
            self.cleaned_data.get(field) for field in ENTRY_FIELDS[self.kind] if field != "heading"
        ):
            return self.cleaned_data["heading"]
        entry = deepcopy(self.original) if isinstance(self.original, dict) else {}
        for field, key in self.entry_keys.items():
            value = self.cleaned_data.get(field, "")
            if not self.is_existing or value != self.initial.get(field, ""):
                if value:
                    entry[key] = value
                else:
                    entry.pop(key, None)
        return entry


class BaseProfileEntryFormSet(forms.BaseFormSet):
    default_error_messages = {
        **forms.BaseFormSet.default_error_messages,
        "missing_management_form": _("These entries could not be read. Reload the page and try again."),
    }

    def __init__(self, *args, entries, kind, **kwargs):
        self.entries = entries if isinstance(entries, list) else []
        self.kind = kind
        kwargs["initial"] = [entry_fields(entry, kind)[0] for entry in self.entries]
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        is_existing = index is not None and index < len(self.entries)
        kwargs.update(kind=self.kind, is_existing=is_existing, original=self.entries[index] if is_existing else None)
        return kwargs

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["DELETE"].label = _("Remove this entry when saving")
        form.fields["DELETE"].widget.attrs["class"] = "form-check-input"

    def clean(self):
        super().clean()
        if self.management_form.is_valid() and (
            self.initial_form_count() != len(self.entries) or self.total_form_count() < len(self.entries)
        ):
            raise ValidationError(_("These entries have changed or could not be read. Reload the page and try again."))

    def to_entries(self):
        return [
            form.to_entry()
            for form in self.forms
            if not self._should_delete_form(form) and (form.is_existing or form.has_changed())
        ]


ProfileEntryFormSet = forms.formset_factory(
    ProfileEntryForm, formset=BaseProfileEntryFormSet, extra=1, can_delete=True
)
