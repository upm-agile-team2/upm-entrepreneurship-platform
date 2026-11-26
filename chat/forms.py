from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Message

User = get_user_model()


class StartConversationForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label=_("Start a conversation with"),
        empty_label=_("Select a person"),
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": _("Choose someone to start a conversation."),
            "invalid_choice": _("Choose an active account other than your own."),
        },
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recipient"].queryset = (
            User.objects.filter(is_active=True)
            .exclude(pk=user.pk)
            .order_by("name", "pk")
        )


class MessageForm(forms.ModelForm):
    text = forms.CharField(
        label=_("Message"),
        strip=True,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        error_messages={"required": _("Enter a message before sending.")},
    )

    class Meta:
        model = Message
        fields = ("text",)
