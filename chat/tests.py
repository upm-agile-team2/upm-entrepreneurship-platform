from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Conversation, Message
from .services import InvalidConversationParticipants, get_or_create_conversation

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


class DirectConversationServiceTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="chat-service-student@example.com",
            name="Service Student",
            role=User.Role.STUDENT,
        )
        self.investor = User.objects.create_user(
            email="chat-service-investor@example.com",
            name="Service Investor",
            role=User.Role.INVESTOR,
        )

    def test_creates_conversation_with_exactly_two_participants(self):
        conversation, created = get_or_create_conversation(self.student, self.investor)

        self.assertTrue(created)
        self.assertCountEqual(
            conversation.participants.all(), [self.student, self.investor]
        )
        self.assertEqual(conversation.participants.count(), 2)

    def test_returns_existing_pair_in_either_order_without_creating_duplicate(self):
        conversation, first_created = get_or_create_conversation(
            self.student, self.investor
        )
        returned, second_created = get_or_create_conversation(
            self.investor, self.student
        )

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(returned, conversation)
        self.assertEqual(Conversation.objects.count(), 1)

    def test_does_not_reuse_a_conversation_with_additional_participants(self):
        malformed = Conversation.objects.create()
        third_user = User.objects.create_user(
            email="chat-service-third@example.com",
            name="Third User",
            role=User.Role.STUDENT,
        )
        malformed.participants.add(self.student, self.investor, third_user)

        conversation, created = get_or_create_conversation(self.student, self.investor)

        self.assertTrue(created)
        self.assertNotEqual(conversation, malformed)
        self.assertCountEqual(
            conversation.participants.all(), [self.student, self.investor]
        )
        self.assertEqual(Conversation.objects.count(), 2)

    def test_rejects_self_and_inactive_participants(self):
        with self.assertRaises(InvalidConversationParticipants):
            get_or_create_conversation(self.student, self.student)
        with self.assertRaises(InvalidConversationParticipants):
            get_or_create_conversation(
                User(name="Unpersisted", email="unpersisted@example.com"),
                self.student,
            )

        self.investor.is_active = False
        self.investor.save(update_fields=["is_active"])
        with self.assertRaises(InvalidConversationParticipants):
            get_or_create_conversation(self.student, self.investor)

        self.assertFalse(Conversation.objects.exists())


class ChatViewTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="chat-view-student@example.com",
            password="A-valid-password-123!",
            name="View Student",
            role=User.Role.STUDENT,
        )
        self.investor = User.objects.create_user(
            email="chat-view-investor@example.com",
            password="A-valid-password-123!",
            name="View Investor",
            role=User.Role.INVESTOR,
        )
        self.other = User.objects.create_user(
            email="chat-view-other@example.com",
            password="A-valid-password-123!",
            name="Other Account",
            role=User.Role.STUDENT,
        )
        self.list_url = reverse("chat:list")
        self.start_url = reverse("chat:start")

    def test_anonymous_user_is_redirected_from_chat(self):
        response = self.client.get(self.list_url)

        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.list_url}"
        )

    def test_students_and_investors_can_start_a_direct_conversation(self):
        for sender, recipient in (
            (self.student, self.investor),
            (self.investor, self.student),
        ):
            with self.subTest(sender=sender):
                self.client.force_login(sender)
                response = self.client.post(self.start_url, {"recipient": recipient.pk})

                self.assertEqual(response.status_code, 302)
                conversation = Conversation.objects.get()
                self.assertEqual(response.url, reverse("chat:detail", args=[conversation.pk]))
                self.assertCountEqual(
                    conversation.participants.all(), [self.student, self.investor]
                )
        self.assertEqual(Conversation.objects.count(), 1)

    def test_invalid_recipient_does_not_create_a_conversation(self):
        self.client.force_login(self.student)
        inactive = User.objects.create_user(
            email="chat-view-inactive@example.com",
            name="Inactive Account",
            role=User.Role.INVESTOR,
            is_active=False,
        )

        for recipient_id in (self.student.pk, inactive.pk, 999999):
            with self.subTest(recipient_id=recipient_id):
                response = self.client.post(self.start_url, {"recipient": recipient_id})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Choose an active account")
                self.assertFalse(Conversation.objects.exists())

    def test_conversation_list_contains_only_the_current_users_conversations(self):
        own, _ = get_or_create_conversation(self.student, self.investor)
        foreign, _ = get_or_create_conversation(self.other, User.objects.create_user(
            email="chat-view-foreign@example.com",
            name="Foreign Account",
            role=User.Role.INVESTOR,
        ))
        self.client.force_login(self.student)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["conversations"]), [own])
        self.assertContains(response, self.investor.name)
        self.assertNotContains(response, "Foreign Account")
        self.assertNotIn(self.student, foreign.participants.all())

    def test_nonparticipant_cannot_view_or_send_to_another_conversation(self):
        conversation, _ = get_or_create_conversation(self.student, self.investor)
        self.client.force_login(self.other)
        detail_url = reverse("chat:detail", args=[conversation.pk])

        self.assertEqual(self.client.get(detail_url).status_code, 404)
        self.assertEqual(
            self.client.post(detail_url, {"text": "Not authorized"}).status_code, 404
        )
        self.assertFalse(conversation.messages.exists())

    def test_participant_can_send_message_and_empty_or_whitespace_text_is_rejected(self):
        conversation, _ = get_or_create_conversation(self.student, self.investor)
        detail_url = reverse("chat:detail", args=[conversation.pk])
        self.client.force_login(self.student)

        for text in ("", "   ", "\n \t"):
            with self.subTest(text=repr(text)):
                response = self.client.post(detail_url, {"text": text})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Enter a message before sending.")
                self.assertEqual(conversation.messages.count(), 0)

        response = self.client.post(detail_url, {"text": "Hello from chat."})

        self.assertEqual(response.status_code, 302)
        message = conversation.messages.get()
        self.assertEqual(message.text, "Hello from chat.")
        self.assertEqual(message.sender, self.student)

    def test_thread_displays_messages_in_order_and_keeps_invalid_form_context(self):
        conversation, _ = get_or_create_conversation(self.student, self.investor)
        earlier = Message.objects.create(
            conversation=conversation, sender=self.student, text="First message"
        )
        later = Message.objects.create(
            conversation=conversation, sender=self.investor, text="Second message"
        )
        Message.objects.filter(pk=earlier.pk).update(
            timestamp=timezone.now() - timedelta(minutes=10)
        )
        Message.objects.filter(pk=later.pk).update(
            timestamp=timezone.now() - timedelta(minutes=5)
        )
        self.client.force_login(self.student)
        detail_url = reverse("chat:detail", args=[conversation.pk])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["chat_messages"]), [earlier, later])
        earlier.refresh_from_db()
        later.refresh_from_db()
        self.assertContains(response, self.student.name)
        self.assertContains(response, self.investor.name)
        self.assertContains(
            response,
            f'datetime="{timezone.localtime(earlier.timestamp).isoformat()}"',
        )
        self.assertContains(
            response,
            f'datetime="{timezone.localtime(later.timestamp).isoformat()}"',
        )
        self.assertLess(
            response.content.index(b"First message"),
            response.content.index(b"Second message"),
        )

        invalid = self.client.post(detail_url, {"text": "   "})
        self.assertEqual(invalid.status_code, 200)
        self.assertContains(invalid, "Enter a message before sending.")
        self.assertContains(invalid, 'aria-invalid="true"')
        self.assertContains(invalid, 'aria-describedby="id_text_error"')
        self.assertContains(invalid, 'class="invalid-feedback d-block" role="alert"')
        self.assertContains(invalid, 'id="id_text_error"')
        self.assertContains(invalid, 'id="id_text_error"', count=1)
        self.assertContains(invalid, "First message")
        self.assertContains(invalid, "Second message")

    def test_chat_navigation_and_empty_state_are_available_to_both_roles(self):
        for user in (self.student, self.investor):
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(reverse("ideas:home"))
                self.assertContains(response, self.list_url)
                chat_page = self.client.get(self.list_url)
                self.assertContains(chat_page, "No conversations yet")
                self.assertContains(chat_page, "Start a conversation")
