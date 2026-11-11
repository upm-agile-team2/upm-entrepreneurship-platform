from django.contrib import admin

from .models import Category, Feedback, Idea


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "owner", "published_at"]
    list_filter = ["category"]
    search_fields = ["title", "description"]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["idea", "author", "timestamp"]
