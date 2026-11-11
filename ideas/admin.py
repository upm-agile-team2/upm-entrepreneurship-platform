from django.contrib import admin

from .models import Category, Feedback, Idea, Reply


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
    list_display = ["idea", "author", "is_private", "status", "timestamp"]
    list_filter = ["is_private", "status"]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ["feedback", "author", "timestamp"]
