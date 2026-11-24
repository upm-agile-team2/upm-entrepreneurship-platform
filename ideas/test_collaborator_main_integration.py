from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.urls import reverse

from accounts.models import ProfileVisit, StudentProfile

from .models import Collaborator, CollaboratorRequest, Idea
from .test_collaborator_requests import CollaboratorRequestFixtures


class CollaborationMainIntegrationTests(CollaboratorRequestFixtures):
    def test_collaboration_profile_and_invalid_send_retain_social_links(self):
        profile = StudentProfile.objects.create(
            user=self.receiver, github_url="https://github.com/example-student",
        )
        self.client.force_login(self.owner)

        responses = [
            self.client.get(reverse("accounts:collaborator_profile", args=[self.receiver.pk])),
            self.client.post(
                reverse("ideas:send_collaborator_request", args=[self.receiver.pk]),
                {"idea": ""},
            ),
        ]

        for response in responses:
            with self.subTest(response=response):
                self.assertContains(response, f'href="{profile.github_url}"')
                self.assertContains(response, "Social media")
                self.assertContains(response, 'id="collaborator-request-form"')
        self.assertContains(responses[1], "Please select one of your published projects.")
        self.assertFalse(CollaboratorRequest.objects.exists())
        self.assertFalse(ProfileVisit.objects.exists())

    def test_collaboration_profile_filters_unsafe_stored_social_urls(self):
        StudentProfile.objects.create(
            user=self.receiver, github_url="javascript:alert(1)",
            youtube_url="https://www.youtube.com/@example-student",
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("accounts:collaborator_profile", args=[self.receiver.pk]))

        self.assertNotContains(response, "javascript:alert(1)")
        self.assertContains(response, 'href="https://www.youtube.com/@example-student"')

    def test_project_details_retain_stage_support_and_accepted_collaborators(self):
        self.idea.development_stage = Idea.DevelopmentStage.MVP
        self.idea.required_support = [Idea.SupportType.FUNDING]
        self.idea.save()
        Collaborator.objects.create(idea=self.idea, collaborator=self.receiver)
        self.client.force_login(self.owner)

        response = self.client.get(reverse("ideas:detail", args=[self.idea.pk]))

        self.assertContains(response, "MVP")
        self.assertContains(response, "Funding")
        self.assertContains(response, self.receiver.name)
        self.assertContains(response, 'id="collaborators-heading"')
        self.assertContains(response, reverse("ideas:edit", args=[self.idea.pk]))


class CollaborationMergeMigrationTests(TransactionTestCase):
    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        self.latest_targets = executor.loader.graph.leaf_nodes()
        self.other_targets = [target for target in self.latest_targets if target[0] != "ideas"]
        self.addCleanup(self.restore_latest_schema)
        # Remove both sibling migrations before testing either upgrade path.
        self.migrate_to("0006_notification")

    def restore_latest_schema(self):
        MigrationExecutor(connection).migrate(self.latest_targets)

    def migrate_to(self, name):
        targets = self.other_targets + [("ideas", name)]
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def create_user(self, apps, email):
        return apps.get_model("accounts", "User").objects.create(
            email=email, name="Existing student", role="student", password="!",
        )

    def test_collaboration_branch_preserves_invitation_and_membership_when_stage_is_added(self):
        old_apps = self.migrate_to("0007_add_collaborator_models")
        owner = self.create_user(old_apps, "merge-collab-owner@example.com")
        receiver = self.create_user(old_apps, "merge-collab-receiver@example.com")
        old_idea = old_apps.get_model("ideas", "Idea")
        idea = old_idea.objects.create(
            owner_id=owner.pk, title="Existing collaboration project",
            description="Created on the collaboration migration branch.",
        )
        old_membership = old_apps.get_model("ideas", "Collaborator")
        old_request = old_apps.get_model("ideas", "CollaboratorRequest")
        membership = old_membership.objects.create(idea_id=idea.pk, collaborator_id=receiver.pk)
        invitation = old_request.objects.create(
            idea_id=idea.pk, sender_id=owner.pk, receiver_id=receiver.pk, status="accepted",
        )
        original_idea = old_idea.objects.values().get(pk=idea.pk)
        original_membership = old_membership.objects.values().get(pk=membership.pk)
        original_request = old_request.objects.values().get(pk=invitation.pk)

        merged_apps = self.migrate_to("0008_merge_collaborators_and_project_stage")

        merged_idea = merged_apps.get_model("ideas", "Idea")
        self.assertEqual(merged_idea.objects.values(*original_idea).get(pk=idea.pk), original_idea)
        project = merged_idea.objects.get(pk=idea.pk)
        self.assertEqual(project.development_stage, "")
        self.assertEqual(project.required_support, [])
        self.assertEqual(list(project.collaborators.values_list("pk", flat=True)), [receiver.pk])
        self.assertEqual(
            merged_apps.get_model("ideas", "Collaborator").objects.values().get(pk=membership.pk),
            original_membership,
        )
        self.assertEqual(
            merged_apps.get_model("ideas", "CollaboratorRequest").objects.values().get(pk=invitation.pk),
            original_request,
        )

    def test_stage_branch_preserves_stage_and_support_when_collaboration_is_added(self):
        old_apps = self.migrate_to("0007_add_project_stage_support")
        owner = self.create_user(old_apps, "merge-stage-owner@example.com")
        old_idea = old_apps.get_model("ideas", "Idea")
        idea = old_idea.objects.create(
            owner_id=owner.pk, title="Existing MVP project",
            description="Created on the project-stage migration branch.",
            development_stage="mvp", required_support=["funding", "technical_support"],
        )
        original_idea = old_idea.objects.values().get(pk=idea.pk)

        merged_apps = self.migrate_to("0008_merge_collaborators_and_project_stage")

        merged_idea = merged_apps.get_model("ideas", "Idea")
        self.assertEqual(merged_idea.objects.values(*original_idea).get(pk=idea.pk), original_idea)
        self.assertFalse(merged_idea.objects.get(pk=idea.pk).collaborators.exists())
        self.assertFalse(merged_apps.get_model("ideas", "Collaborator").objects.exists())
        self.assertFalse(merged_apps.get_model("ideas", "CollaboratorRequest").objects.exists())
