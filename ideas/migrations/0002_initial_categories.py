from django.db import migrations

INITIAL_CATEGORIES = [
    "Technology",
    "Health",
    "Education",
    "Sustainability",
    "Finance",
    "Social impact",
    "Other",
]


def add_categories(apps, schema_editor):
    Category = apps.get_model("ideas", "Category")
    for name in INITIAL_CATEGORIES:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model("ideas", "Category")
    Category.objects.filter(name__in=INITIAL_CATEGORIES, ideas__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ideas", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]
