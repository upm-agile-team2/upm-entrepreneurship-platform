from django.urls import path

from . import views

app_name = "ideas"

urlpatterns = [
    path("", views.home, name="home"),
    path("ideas/new/", views.publish_idea, name="publish"),
    path("ideas/<int:idea_id>/", views.idea_detail, name="detail"),
    path("ideas/<int:idea_id>/feedback/", views.submit_feedback, name="feedback"),
    path("feedback/<int:feedback_id>/reply/", views.submit_reply, name="reply"),
    path(
        "feedback/<int:feedback_id>/status/",
        views.toggle_feedback_status,
        name="feedback-status",
    ),
    path("ideas/<int:idea_id>/edit/", views.edit_idea, name="edit"),
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notifications/read-all/",
        views.mark_notifications_read,
        name="mark-notifications-read",
    ),
    path(
        "notifications/<int:notification_id>/dismiss/",
        views.dismiss_notification,
        name="dismiss-notification",
    ),
    path(
        "notifications/<int:notification_id>/",
        views.open_notification,
        name="open-notification",
    ),
]
