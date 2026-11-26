import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

from .models import Collaborator, CollaboratorRequest, Idea, Notification

User = get_user_model()


class CollaboratorRequestFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="invitation-owner@example.com", name="Project Creator",
            role=User.Role.STUDENT,
        )
        cls.receiver = User.objects.create_user(
            email="invitation-receiver@example.com", name="Invited Student",
            role=User.Role.STUDENT,
        )
        cls.other_student = User.objects.create_user(
            email="invitation-other@example.com", name="Other Student",
            role=User.Role.STUDENT,
        )
        cls.investor = User.objects.create_user(
            email="invitation-investor@example.com", name="Investor",
            role=User.Role.INVESTOR,
        )
        cls.idea = Idea.objects.create(
            owner=cls.owner, title="Campus collaboration project",
            description="Build a useful service for students.\nWe need a designer.",
        )
        cls.list_url = reverse("ideas:collaborator_requests")
        cls.history_url = cls.list_url + "?tab=history"
        cls.sent_url = cls.list_url + "?tab=sent"

    def make_invitation(self, **overrides):
        fields = {
            "idea": self.idea, "sender": self.owner, "receiver": self.receiver,
        }
        fields.update(overrides)
        return CollaboratorRequest.objects.create(**fields)

    def another_idea(self, title, owner=None):
        return Idea.objects.create(
            owner=owner or self.owner, title=title, description="Another project.",
        )

    def decision_url(self, invitation):
        return reverse("ideas:respond_collaborator_request", args=[invitation.pk])


class CollaboratorRequestListTests(CollaboratorRequestFixtures):
    def setUp(self):
        self.client.force_login(self.receiver)

    def test_received_lists_all_own_pending_requests_with_idea_and_creator(self):
        first = self.make_invitation()
        second = self.make_invitation(idea=self.another_idea("Second pending project"))
        foreign = self.make_invitation(
            idea=self.another_idea("Private invitation to another student"),
            receiver=self.other_student,
        )
        for status in (CollaboratorRequest.Status.ACCEPTED, CollaboratorRequest.Status.REJECTED):
            self.make_invitation(idea=self.another_idea(f"Handled {status}"), status=status)

        response = self.client.get(self.list_url)

        self.assertEqual(list(response.context["invitations"]), [second, first])
        self.assertContains(response, first.idea.title)
        self.assertContains(response, "Build a useful service for students.")
        self.assertContains(response, "We need a designer.")
        self.assertContains(response, self.owner.name)
        self.assertContains(response, reverse("ideas:detail", args=[self.idea.pk]))
        self.assertContains(response, reverse("accounts:collaborator_profile", args=[self.owner.pk]))
        self.assertContains(response, 'name="action" value="accept"', count=2)
        self.assertContains(response, 'name="action" value="decline"', count=2)
        self.assertNotContains(response, foreign.idea.title)
        self.assertNotContains(response, "Handled accepted")
        self.assertNotContains(response, "Handled rejected")
        self.assertFalse(Collaborator.objects.exists())
        self.assertFalse(Notification.objects.exists())
        first.refresh_from_db()
        self.assertEqual(first.status, CollaboratorRequest.Status.PENDING)

    def test_received_empty_state_includes_no_decision_forms(self):
        response = self.client.get(self.list_url)

        self.assertContains(response, "No pending invitations")
        self.assertNotContains(response, 'name="action"')

    def test_history_lists_only_own_handled_invitations_without_actions_or_writes(self):
        pending = self.make_invitation()
        handled = [self.make_invitation(
            idea=self.another_idea(f"History {status}"), status=status,
        ) for status in (CollaboratorRequest.Status.ACCEPTED, CollaboratorRequest.Status.REJECTED)]
        foreign = self.make_invitation(
            idea=self.another_idea("Another receiver's history"),
            receiver=self.other_student, status=CollaboratorRequest.Status.REJECTED,
        )
        outgoing = self.make_invitation(
            idea=self.another_idea("My outgoing accepted invitation", owner=self.receiver),
            sender=self.receiver, receiver=self.other_student,
            status=CollaboratorRequest.Status.ACCEPTED,
        )
        membership = Collaborator.objects.create(idea=handled[0].idea, collaborator=self.receiver)
        original_requests = list(CollaboratorRequest.objects.values())

        response = self.client.get(self.history_url)

        self.assertEqual(response.context["request_tab"], "history")
        self.assertEqual(list(response.context["invitations"]), handled[::-1])
        for invitation in handled:
            self.assertContains(response, invitation.idea.title)
            self.assertContains(response, reverse("ideas:detail", args=[invitation.idea_id]))
        self.assertContains(response, self.owner.name)
        self.assertContains(response, "Accepted")
        self.assertContains(response, "Rejected")
        self.assertContains(response, "Another project.")
        for invitation in (pending, foreign, outgoing):
            self.assertNotContains(response, invitation.idea.title)
        self.assertNotContains(response, 'name="action"')
        self.assertNotContains(response, 'id="respond-request-')
        self.assertEqual(list(CollaboratorRequest.objects.values()), original_requests)
        self.assertEqual(list(Collaborator.objects.all()), [membership])

    def test_history_empty_state_has_active_navigation_and_no_decision_forms(self):
        self.make_invitation()

        response = self.client.get(self.history_url)

        self.assertContains(response, "No accepted or declined invitations yet")
        self.assertContains(response, f'href="{self.history_url}" class="nav-link active" aria-current="page"')
        self.assertNotContains(response, 'name="action"')

    def test_received_page_links_to_the_read_only_history(self):
        self.make_invitation()

        response = self.client.get(self.list_url)

        self.assertContains(response, f'href="{self.history_url}"')
        self.assertContains(response, "History")

    def test_sent_lists_own_invitations_in_every_status_and_no_decision_controls(self):
        invitations = [self.make_invitation()]
        for status in (CollaboratorRequest.Status.ACCEPTED, CollaboratorRequest.Status.REJECTED):
            invitations.append(self.make_invitation(
                idea=self.another_idea(f"Sent {status}"), status=status,
            ))
        foreign_idea = self.another_idea("Someone else's sent invitation", owner=self.receiver)
        self.make_invitation(idea=foreign_idea, sender=self.receiver, receiver=self.other_student)
        self.client.force_login(self.owner)

        response = self.client.get(self.sent_url)

        self.assertEqual(list(response.context["invitations"]), invitations[::-1])
        self.assertContains(response, self.receiver.name)
        for label in ("Pending", "Accepted", "Rejected"):
            self.assertContains(response, label)
        self.assertNotContains(response, foreign_idea.title)
        self.assertNotContains(response, 'name="action"')

    def test_sent_empty_state_links_to_student_discovery(self):
        response = self.client.get(self.sent_url)

        self.assertContains(response, "No sent invitations yet")
        self.assertContains(response, reverse("accounts:student_discovery"))

    def test_query_parameters_cannot_select_another_users_invitations(self):
        self.make_invitation(receiver=self.other_student)
        self.make_invitation(
            idea=self.another_idea("Other receiver's rejected record"),
            receiver=self.other_student, status=CollaboratorRequest.Status.REJECTED,
        )

        for tab in ("received", "history", "sent"):
            with self.subTest(tab=tab):
                response = self.client.get(self.list_url, {
                    "tab": tab, "receiver": self.other_student.pk, "sender": self.owner.pk,
                })
                self.assertEqual(list(response.context["invitations"]), [])

    def test_unknown_tab_defaults_to_received(self):
        invitation = self.make_invitation()

        response = self.client.get(self.list_url, {"tab": "unknown"})

        self.assertEqual(response.context["request_tab"], "received")
        self.assertEqual(list(response.context["invitations"]), [invitation])

    def test_equal_timestamps_have_stable_newest_id_order(self):
        first = self.make_invitation()
        second = self.make_invitation(idea=self.another_idea("Same-time invitation"))
        CollaboratorRequest.objects.filter(pk=second.pk).update(timestamp=first.timestamp)

        response = self.client.get(self.list_url)

        self.assertEqual(list(response.context["invitations"]), [second, first])

    def test_idea_and_creator_text_is_escaped(self):
        self.idea.title = '<script>alert("title")</script>'
        self.idea.description = '<img src=x onerror="alert(1)">'
        self.idea.save()
        self.owner.name = '<script>alert("creator")</script>'
        self.owner.save()
        self.make_invitation()

        response = self.client.get(self.list_url)

        self.assertNotContains(response, "<script>")
        self.assertNotContains(response, '<img src=x')
        self.assertContains(response, "&lt;script&gt;")
        self.assertContains(response, "&lt;img src=x")

    def test_anonymous_lists_redirect_to_login(self):
        self.client.logout()
        for url in (self.list_url, self.history_url, self.sent_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login") + "?next="))

    def test_investor_cannot_access_any_list(self):
        self.client.force_login(self.investor)
        for url in (self.list_url, self.history_url, self.sent_url):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_list_rejects_post_without_creating_or_handling_requests(self):
        invitation = self.make_invitation()

        response = self.client.post(self.list_url, {"action": "accept"})

        self.assertEqual(response.status_code, 405)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, CollaboratorRequest.Status.PENDING)
        self.assertFalse(Collaborator.objects.exists())

    def test_navigation_is_discoverable_for_students_only(self):
        response = self.client.get(reverse("ideas:home"))
        self.assertContains(response, f'href="{self.list_url}"')
        for user in (self.investor, None):
            with self.subTest(user=user):
                if user is None:
                    self.client.logout()
                else:
                    self.client.force_login(user)
                response = self.client.get(reverse("ideas:home"))
                self.assertNotContains(response, f'href="{self.list_url}"')

    def test_send_profile_links_to_sent_invitations(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("accounts:collaborator_profile", args=[self.receiver.pk]))

        self.assertContains(response, f'href="{self.sent_url}"')
        self.assertContains(response, "View sent invitations")


class CollaboratorRequestDecisionTests(CollaboratorRequestFixtures):
    def setUp(self):
        self.invitation = self.make_invitation()
        self.url = self.decision_url(self.invitation)
        self.client.force_login(self.receiver)

    def assert_pending_without_membership(self):
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.PENDING)
        self.assertFalse(Collaborator.objects.exists())

    def test_accept_adds_receiver_to_correct_idea_and_removes_pending_invitation(self):
        original_timestamp = self.invitation.timestamp

        response = self.client.post(self.url, {"action": "accept"}, follow=True)

        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "You are now a collaborator")
        self.assertEqual(list(response.context["invitations"]), [])
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.ACCEPTED)
        self.assertEqual(self.invitation.timestamp, original_timestamp)
        membership = Collaborator.objects.get()
        self.assertEqual(membership.idea, self.idea)
        self.assertEqual(membership.collaborator, self.receiver)
        self.assertFalse(Notification.objects.exists())

    def test_decline_rejects_invitation_without_adding_membership(self):
        response = self.client.post(self.url, {"action": "decline"}, follow=True)

        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "The collaborator request has been declined.")
        self.assertEqual(list(response.context["invitations"]), [])
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.REJECTED)
        self.assertFalse(Collaborator.objects.exists())

    def test_anonymous_decision_redirects_to_login_without_writes(self):
        self.client.logout()

        response = self.client.post(self.url, {"action": "accept"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:login") + "?next=" + self.url)
        self.assert_pending_without_membership()

    def test_investor_cannot_process_an_invitation(self):
        self.client.force_login(self.investor)

        for action in ("accept", "decline"):
            with self.subTest(action=action):
                self.assertEqual(self.client.post(self.url, {"action": action}).status_code, 403)
                self.assert_pending_without_membership()

    def test_sender_and_other_students_cannot_process_the_receivers_invitation(self):
        for actor in (self.owner, self.other_student):
            self.client.force_login(actor)
            for action in ("accept", "decline"):
                with self.subTest(actor=actor, action=action):
                    response = self.client.post(self.url, {"action": action, "receiver": actor.pk})
                    self.assertEqual(response.status_code, 404)
                    self.assert_pending_without_membership()

    def test_nonexistent_invitation_returns_404(self):
        url = reverse("ideas:respond_collaborator_request", args=[self.invitation.pk + 10000])

        self.assertEqual(self.client.post(url, {"action": "accept"}).status_code, 404)
        self.assert_pending_without_membership()

    def test_non_post_methods_cannot_process_an_invitation(self):
        for method in ("get", "head", "put", "patch", "delete", "options"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, 405)
                self.assert_pending_without_membership()

    def test_missing_or_unknown_action_does_not_change_invitation(self):
        for data in ({}, {"action": ""}, {"action": "accepted"}, {"action": "delete"}):
            with self.subTest(data=data):
                self.assertEqual(self.client.post(self.url, data).status_code, 400)
                self.assert_pending_without_membership()

    def test_decision_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.receiver)

        for action in ("accept", "decline"):
            with self.subTest(action=action):
                self.assertEqual(client.post(self.url, {"action": action}).status_code, 403)
                self.assert_pending_without_membership()

    def test_submitted_participants_idea_and_status_cannot_override_saved_request(self):
        foreign_idea = self.another_idea("Unrelated project", owner=self.other_student)

        response = self.client.post(self.url, {
            "action": "accept", "sender": self.other_student.pk,
            "receiver": self.owner.pk, "idea": foreign_idea.pk, "status": "rejected",
        })

        self.assertRedirects(response, self.list_url)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.sender, self.owner)
        self.assertEqual(self.invitation.receiver, self.receiver)
        self.assertEqual(self.invitation.idea, self.idea)
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.ACCEPTED)
        membership = Collaborator.objects.get()
        self.assertEqual(membership.idea, self.idea)
        self.assertEqual(membership.collaborator, self.receiver)

    def test_handled_invitations_preserve_outcome_for_repeated_and_conflicting_decisions(self):
        for status in (CollaboratorRequest.Status.ACCEPTED, CollaboratorRequest.Status.REJECTED):
            for action in ("accept", "decline"):
                with self.subTest(status=status, action=action):
                    idea = self.another_idea(f"Handled {status} then {action}")
                    invitation = self.make_invitation(idea=idea, status=status)
                    if status == CollaboratorRequest.Status.ACCEPTED:
                        Collaborator.objects.create(idea=idea, collaborator=self.receiver)
                    memberships_before = list(Collaborator.objects.values_list("pk", flat=True))

                    response = self.client.post(self.decision_url(invitation), {"action": action}, follow=True)

                    self.assertContains(response, "This collaborator request has already been handled.")
                    invitation.refresh_from_db()
                    self.assertEqual(invitation.status, status)
                    self.assertEqual(list(Collaborator.objects.values_list("pk", flat=True)), memberships_before)

    def test_accept_reuses_existing_membership_and_preserves_its_timestamp(self):
        membership = Collaborator.objects.create(idea=self.idea, collaborator=self.receiver)
        original_timestamp = membership.timestamp

        self.client.post(self.url, {"action": "accept"})

        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.ACCEPTED)
        self.assertEqual(Collaborator.objects.count(), 1)
        membership.refresh_from_db()
        self.assertEqual(membership.timestamp, original_timestamp)

    def test_decline_does_not_delete_an_existing_membership(self):
        membership = Collaborator.objects.create(idea=self.idea, collaborator=self.receiver)

        self.client.post(self.url, {"action": "decline"})

        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.REJECTED)
        self.assertTrue(Collaborator.objects.filter(pk=membership.pk).exists())

    def test_membership_failure_rolls_back_the_accepted_status(self):
        with patch("ideas.views.Collaborator.objects.get_or_create", side_effect=IntegrityError("Membership failed")):
            with self.assertRaises(IntegrityError):
                self.client.post(self.url, {"action": "accept"})

        self.assert_pending_without_membership()

    def test_competing_winning_decline_prevents_later_acceptance(self):
        original_update = QuerySet.update

        def decline_before_accept(queryset, **fields):
            if queryset.model is CollaboratorRequest and fields.get("status") == "accepted":
                original_update(queryset, status=CollaboratorRequest.Status.REJECTED)
            return original_update(queryset, **fields)

        with patch.object(QuerySet, "update", autospec=True, side_effect=decline_before_accept):
            response = self.client.post(self.url, {"action": "accept"}, follow=True)

        self.assertContains(response, "This collaborator request has already been handled.")
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CollaboratorRequest.Status.REJECTED)
        self.assertFalse(Collaborator.objects.exists())

    def test_changed_project_ownership_prevents_an_invalid_acceptance(self):
        self.idea.owner = self.other_student
        self.idea.save(update_fields=["owner"])

        response = self.client.post(self.url, {"action": "accept"}, follow=True)

        self.assertContains(response, "This collaborator request is no longer valid")
        self.assert_pending_without_membership()

    def test_changed_sender_role_prevents_an_invalid_acceptance(self):
        User.objects.filter(pk=self.owner.pk).update(role=User.Role.INVESTOR)

        response = self.client.post(self.url, {"action": "accept"}, follow=True)

        self.assertContains(response, "This collaborator request is no longer valid")
        self.assert_pending_without_membership()


class CollaboratorRequestRenderedWorkflowTests(CollaboratorRequestFixtures):
    def setUp(self):
        self.sender_client = Client(enforce_csrf_checks=True)
        self.receiver_client = Client(enforce_csrf_checks=True)
        self.sender_client.force_login(self.owner)
        self.receiver_client.force_login(self.receiver)
        self.profile_url = reverse("accounts:collaborator_profile", args=[self.receiver.pk])

    def rendered_form(self, response, form_id):
        match = re.search(
            rf'<form\b[^>]*id="{re.escape(form_id)}"[^>]*>.*?</form>',
            response.content.decode(), re.DOTALL,
        )
        self.assertIsNotNone(match, f"Missing form {form_id}")
        html = match.group(0)
        action = re.search(r'\baction="([^"]+)"', html).group(1)
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)
        return action, token

    def send_from_rendered_form(self):
        profile = self.sender_client.get(self.profile_url)
        action, token = self.rendered_form(profile, "collaborator-request-form")
        data = {"idea": self.idea.pk, "csrfmiddlewaretoken": token}

        response = self.sender_client.post(action, data, follow=True)

        self.assertContains(response, "Your collaborator request has been sent.")
        self.assertContains(response, f'href="{self.sent_url}"')
        invitation = CollaboratorRequest.objects.get()
        self.assertEqual(invitation.status, CollaboratorRequest.Status.PENDING)
        return invitation, action, data

    def test_sender_sends_receiver_accepts_and_both_can_see_the_result(self):
        invitation, send_action, send_data = self.send_from_rendered_form()
        sent = self.sender_client.get(self.sent_url)
        self.assertContains(sent, "Pending")
        self.assertContains(sent, self.receiver.name)
        inbox = self.receiver_client.get(self.list_url)
        self.assertContains(inbox, self.idea.title)
        self.assertContains(inbox, self.owner.name)
        action, token = self.rendered_form(inbox, f"respond-request-{invitation.pk}")

        accepted = self.receiver_client.post(action, {
            "action": "accept", "csrfmiddlewaretoken": token,
        }, follow=True)

        self.assertContains(accepted, "You are now a collaborator")
        self.assertContains(accepted, "No pending invitations")
        self.assertNotContains(accepted, f'id="respond-request-{invitation.pk}"')
        self.assertEqual(list(self.idea.collaborators.all()), [self.receiver])
        history = self.receiver_client.get(self.history_url)
        self.assertEqual(list(history.context["invitations"]), [invitation])
        self.assertContains(history, self.idea.title)
        self.assertContains(history, "Accepted")
        self.assertNotContains(history, 'name="action"')
        detail = self.receiver_client.get(reverse("ideas:detail", args=[self.idea.pk]))
        self.assertContains(detail, 'id="collaborators-heading"')
        self.assertContains(detail, self.receiver.name)
        self.assertNotContains(detail, reverse("ideas:edit", args=[self.idea.pk]))
        sent = self.sender_client.get(self.sent_url)
        self.assertContains(sent, "Accepted")
        self.assertNotContains(sent, 'name="action"')
        duplicate = self.sender_client.post(send_action, send_data)
        self.assertContains(duplicate, "You have already sent a collaborator request")
        self.assertEqual(CollaboratorRequest.objects.count(), 1)
        self.assertEqual(Collaborator.objects.count(), 1)

    def test_sender_sends_receiver_declines_and_sender_sees_rejected(self):
        invitation, send_action, send_data = self.send_from_rendered_form()
        inbox = self.receiver_client.get(self.list_url)
        action, token = self.rendered_form(inbox, f"respond-request-{invitation.pk}")

        declined = self.receiver_client.post(action, {
            "action": "decline", "csrfmiddlewaretoken": token,
        }, follow=True)

        self.assertContains(declined, "The collaborator request has been declined.")
        self.assertContains(declined, "No pending invitations")
        self.assertFalse(self.idea.collaborators.exists())
        self.assertFalse(Collaborator.objects.exists())
        history = self.receiver_client.get(self.history_url)
        self.assertEqual(list(history.context["invitations"]), [invitation])
        self.assertContains(history, self.idea.title)
        self.assertContains(history, "Rejected")
        self.assertNotContains(history, 'name="action"')
        sent = self.sender_client.get(self.sent_url)
        self.assertContains(sent, "Rejected")
        self.assertContains(sent, self.idea.title)
        duplicate = self.sender_client.post(send_action, send_data)
        self.assertContains(duplicate, "You have already sent a collaborator request")
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, CollaboratorRequest.Status.REJECTED)
        self.assertEqual(CollaboratorRequest.objects.count(), 1)


class CollaboratorMembershipPresentationTests(CollaboratorRequestFixtures):
    def setUp(self):
        self.detail_url = reverse("ideas:detail", args=[self.idea.pk])

    def test_detail_explains_when_no_collaborators_have_joined(self):
        response = self.client.get(self.detail_url)

        self.assertContains(response, "No collaborators yet.")

    def test_owner_sees_accepted_collaborators_and_retains_edit_action(self):
        Collaborator.objects.create(idea=self.idea, collaborator=self.receiver)
        self.client.force_login(self.owner)

        response = self.client.get(self.detail_url)

        self.assertContains(response, self.receiver.name)
        self.assertContains(response, reverse("accounts:collaborator_profile", args=[self.receiver.pk]))
        self.assertContains(response, reverse("ideas:edit", args=[self.idea.pk]))

    def test_membership_does_not_allow_collaborator_to_edit_the_idea(self):
        Collaborator.objects.create(idea=self.idea, collaborator=self.receiver)
        self.client.force_login(self.receiver)
        edit_url = reverse("ideas:edit", args=[self.idea.pk])

        self.assertEqual(self.client.get(edit_url).status_code, 403)
        self.assertEqual(self.client.post(edit_url, {"title": "Changed", "description": "Changed"}).status_code, 403)
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.title, "Campus collaboration project")

    def test_investor_and_anonymous_viewers_see_names_without_student_only_profile_links(self):
        Collaborator.objects.create(idea=self.idea, collaborator=self.receiver)
        profile_url = reverse("accounts:collaborator_profile", args=[self.receiver.pk])

        for actor in (self.investor, None):
            with self.subTest(actor=actor):
                if actor is None:
                    self.client.logout()
                else:
                    self.client.force_login(actor)
                response = self.client.get(self.detail_url)
                self.assertContains(response, self.receiver.name)
                self.assertNotContains(response, profile_url)
