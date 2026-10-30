from django.urls import path

from . import views

app_name = "ideas"

urlpatterns = [
    path("", views.home, name="home"),
    path("ideas/new/", views.publish_idea, name="publish"),
    path("ideas/<int:idea_id>/", views.idea_detail, name="detail"),
    path("ideas/<int:idea_id>/edit/", views.edit_idea, name="edit"),
]
