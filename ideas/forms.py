from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Feedback, Idea, Reply


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["title", "description", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
        error_messages = {
            "title": {"required": _("Please enter a title for your idea.")},
            "description": {"required": _("Please enter a description for your idea.")},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = _("Select a category")

    def full_clean(self):
        super().full_clean()
        for name in self.errors:
            widget = self.fields[name].widget
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} is-invalid".strip()


class CollaboratorRequestForm(forms.Form):
    idea = forms.ModelChoiceField(
        queryset=Idea.objects.none(),
        label=_("Your project"),
        empty_label=_("Select a project"),
        help_text=_("Choose the project you want this student to help develop."),
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": _("Please select one of your published projects."),
            "invalid_choice": _("Select one of your own published projects."),
        },
    )

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        if owner.is_authenticated and owner.is_student and owner.pk is not None:
            self.fields["idea"].queryset = Idea.objects.filter(owner=owner).order_by(
                "title", "pk"
            )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["text", "is_private"]
        widgets = {
            "text": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "is_private": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        error_messages = {
            "text": {"required": _("Please enter feedback.")},
        }

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise forms.ValidationError(_("Please enter feedback."))
        return text


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }
        error_messages = {
            "text": {"required": _("Please enter a reply.")},
        }

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise forms.ValidationError(_("Please enter a reply."))
        return text
