from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class ProjectStageSupportMigrationTests(TransactionTestCase):
    migrate_from = ("ideas", "0006_notification")
    migrate_to = ("ideas", "0007_add_project_stage_support")

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        self.latest_targets = executor.loader.graph.leaf_nodes()
        self.addCleanup(self.restore_latest_schema)
        executor.migrate([self.migrate_from])
        self.old_apps = executor.loader.project_state([self.migrate_from]).apps

    def restore_latest_schema(self):
        MigrationExecutor(connection).migrate(self.latest_targets)

    def test_existing_project_is_preserved_with_empty_stage_and_support(self):
        owner = get_user_model().objects.create_user(
            email="migration-student@example.com",
            password="Migration-test-password-123!",
            name="Migration Student",
            role="student",
        )
        old_category = self.old_apps.get_model("ideas", "Category")
        category = old_category.objects.create(name="Migration category")
        old_idea = self.old_apps.get_model("ideas", "Idea")
        original = old_idea.objects.create(
            title="Existing project",
            description="This project was saved before stage and support existed.",
            owner_id=owner.pk,
            category_id=category.pk,
            demo_key="stage-support-migration-test",
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([self.migrate_to]).apps
        migrated_idea = new_apps.get_model("ideas", "Idea")
        migrated = migrated_idea.objects.get(pk=original.pk)

        self.assertEqual(migrated.title, original.title)
        self.assertEqual(migrated.description, original.description)
        self.assertEqual(migrated.owner_id, owner.pk)
        self.assertEqual(migrated.category_id, category.pk)
        self.assertEqual(migrated.demo_key, original.demo_key)
        self.assertEqual(migrated.published_at, original.published_at)
        self.assertEqual(migrated.development_stage, "")
        self.assertEqual(migrated.required_support, [])
