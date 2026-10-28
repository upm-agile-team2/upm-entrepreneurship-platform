from django.db import migrations, models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


def migrate_existing_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    for user in User.objects.all():
        name = " ".join(
            part for part in (user.first_name, user.last_name) if part
        ).strip() or user.email
        user.name = name
        user.role = "student"
        user.save(update_fields=["name", "role"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="name",
            field=models.CharField(_("name"), max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                _("role"),
                choices=[("student", _("Student")), ("investor", _("Investor/Expert"))],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                _("email address"), max_length=254, unique=True
            ),
        ),
        migrations.RunPython(migrate_existing_users, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(_("name"), max_length=150),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                _("role"),
                choices=[("student", _("Student")), ("investor", _("Investor/Expert"))],
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
            ),
        ),
    ]
