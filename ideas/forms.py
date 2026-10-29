from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Idea


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
