from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import ProfileVisit, Skill, StudentProfile, User

@admin.register(User)
class PlatformUserAdmin(UserAdmin):
    list_display = ("email", "name", "role", "is_staff", "is_active")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name", "first_name", "last_name", "role")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "role", "password1", "password2"),
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
    filter_horizontal = ("skills",)


@admin.register(ProfileVisit)
class ProfileVisitAdmin(admin.ModelAdmin):
    list_display = ("student", "visitor", "visited_at")
    list_filter = ("visited_at",)
    readonly_fields = ("student", "visitor", "visited_at")
