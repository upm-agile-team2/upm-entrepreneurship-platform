from django.urls import path

from .discovery import student_discovery
from .views import (
    AccountLoginView,
    AccountLogoutView,
    investor_profile,
    my_profile,
    signup,
    student_profile,
)

app_name = "accounts"

urlpatterns = [
    path("students/", student_discovery, name="student_discovery"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("signup/", signup, name="signup"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("profile/", student_profile, name="student_profile"),
    path("profile/me/", my_profile, name="my_profile"),
    path("students/<int:student_id>/profile/", investor_profile, name="investor_profile"),
]
