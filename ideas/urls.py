from django.urls import path

from . import views

app_name = "ideas"

urlpatterns = [
    path("", views.home, name="home"),
    path("ideas/new/", views.publish_idea, name="publish"),
]
