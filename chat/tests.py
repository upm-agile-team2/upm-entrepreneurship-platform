from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Conversation, Message

User = get_user_model()


class MessageModelTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="chat-student@example.com",
            password="A-valid-password-123!",
            name="Chat Student",
            role=User.Role.STUDENT,
        )
        self.investor = User.objects.create_user(
            email="chat-investor@example.com",
            password="A-valid-password-123!",
            name="Chat Investor",
            role=User.Role.INVESTOR,
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.student, self.investor)

    def test_message_is_stored_with_conversation_sender_text_and_timestamp(self):
        before = timezone.now()

        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.student,
            text="Would you like to see our prototype?",
        )
        message.refresh_from_db()

        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.sender, self.student)
        self.assertEqual(message.text, "Would you like to see our prototype?")
        self.assertIsNotNone(message.timestamp)
        self.assertGreaterEqual(message.timestamp, before)
        self.assertLessEqual(message.timestamp, timezone.now())
        self.assertCountEqual(
            self.conversation.participants.all(), [self.student, self.investor]
        )

    def test_message_remains_without_sender_when_sender_is_deleted(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.investor,
            text="Happy to help with the business plan.",
        )

        self.investor.delete()
        message.refresh_from_db()

        self.assertIsNone(message.sender)
        self.assertIn(message, self.conversation.messages.all())

    def test_empty_message_text_fails_validation(self):
        message = Message(
            conversation=self.conversation, sender=self.student, text=""
        )

        with self.assertRaises(ValidationError) as context:
            message.full_clean()

        self.assertIn("text", context.exception.message_dict)

    def test_conversation_messages_are_returned_in_chronological_order(self):
        now = timezone.now()
        first = Message.objects.create(
            conversation=self.conversation, sender=self.student, text="First"
        )
        second = Message.objects.create(
            conversation=self.conversation, sender=self.investor, text="Second"
        )
        third = Message.objects.create(
            conversation=self.conversation, sender=self.student, text="Third"
        )
        # Create order differs from send time so the test proves the ordering.
        Message.objects.filter(pk=first.pk).update(timestamp=now - timedelta(minutes=5))
        Message.objects.filter(pk=second.pk).update(timestamp=now - timedelta(minutes=10))
        Message.objects.filter(pk=third.pk).update(timestamp=now - timedelta(minutes=1))

        messages = list(self.conversation.messages.all())

        self.assertEqual(messages, [second, first, third])
        self.assertEqual(
            [message.sender for message in messages],
            [self.investor, self.student, self.student],
        )
