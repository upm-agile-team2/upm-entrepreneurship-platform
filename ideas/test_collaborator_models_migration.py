from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class CollaboratorModelsMigrationTests(TransactionTestCase):
    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        self.latest_targets = executor.loader.graph.leaf_nodes()
        self.addCleanup(self.restore_latest_schema)

        # Keep the other apps at their current schema while testing this upgrade.
        other_targets = [
            target for target in self.latest_targets if target[0] != "ideas"
        ]
        old_targets = other_targets + [("ideas", "0006_notification")]
        self.new_targets = other_targets + [("ideas", "0007_add_collaborator_models")]
        executor.migrate(old_targets)
        self.old_apps = executor.loader.project_state(old_targets).apps

    def restore_latest_schema(self):
        MigrationExecutor(connection).migrate(self.latest_targets)

    def test_existing_user_and_idea_survive_with_empty_collaboration_relations(self):
        OldUser = self.old_apps.get_model("accounts", "User")
        OldCategory = self.old_apps.get_model("ideas", "Category")
        OldIdea = self.old_apps.get_model("ideas", "Idea")
        owner = OldUser.objects.create(
            email="migration-owner@example.com",
            name="Existing Student",
            role="student",
            password="!",
        )
        category = OldCategory.objects.create(name="Migration test category")
        idea = OldIdea.objects.create(
            title="Existing campus project",
            description="Published before collaboration models existed.",
            owner_id=owner.pk,
            category_id=category.pk,
            demo_key="collaboration-migration-existing-idea",
        )
        user_fields = ("id", "email", "name", "role", "password", "date_joined")
        idea_fields = (
            "id", "title", "description", "owner_id", "category_id",
            "published_at", "demo_key",
        )
        original_user = OldUser.objects.values(*user_fields).get(pk=owner.pk)
        original_idea = OldIdea.objects.values(*idea_fields).get(pk=idea.pk)

        executor = MigrationExecutor(connection)
        executor.migrate(self.new_targets)
        new_apps = executor.loader.project_state(self.new_targets).apps
        NewUser = new_apps.get_model("accounts", "User")
        NewIdea = new_apps.get_model("ideas", "Idea")
        Collaborator = new_apps.get_model("ideas", "Collaborator")
        CollaboratorRequest = new_apps.get_model("ideas", "CollaboratorRequest")

        self.assertEqual(
            NewUser.objects.values(*user_fields).get(pk=owner.pk), original_user
        )
        self.assertEqual(
            NewIdea.objects.values(*idea_fields).get(pk=idea.pk), original_idea
        )
        upgraded_idea = NewIdea.objects.get(pk=idea.pk)
        upgraded_owner = NewUser.objects.get(pk=owner.pk)
        self.assertFalse(upgraded_idea.collaborators.exists())
        self.assertFalse(upgraded_owner.collaborating_ideas.exists())
        self.assertFalse(Collaborator.objects.exists())
        self.assertFalse(CollaboratorRequest.objects.exists())
