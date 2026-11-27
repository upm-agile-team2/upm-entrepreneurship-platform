from django.urls import path

from .discovery import student_discovery
from .investor_profiles import (
    edit_investor_profile,
    investor_discovery,
    investor_profile_detail,
    my_investor_profile,
)
from .views import (
    AccountLoginView,
    AccountLogoutView,
    upload_avatar,
    collaborator_profile,
    follow_student,
    following,
    investor_profile,
    my_profile,
    signup,
    student_profile,
    unfollow_student,
)

app_name = "accounts"

urlpatterns = [
    path("students/", student_discovery, name="student_discovery"),
    path("investors/", investor_discovery, name="investor_discovery"),
    path("investors/me/", my_investor_profile, name="my_investor_profile"),
    path("investors/me/edit/", edit_investor_profile, name="edit_investor_profile"),
    path("investors/<int:investor_id>/profile/", investor_profile_detail, name="investor_profile_detail"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("signup/", signup, name="signup"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("profile/", student_profile, name="student_profile"),
    path("profile/avatar/", upload_avatar, name="upload_avatar"),
    path("profile/me/", my_profile, name="my_profile"),
    path("following/", following, name="following"),
    path("students/<int:student_id>/profile/", investor_profile, name="investor_profile"),
    path(
        "students/<int:student_id>/collaborate/",
        collaborator_profile,
        name="collaborator_profile",
    ),
    path("students/<int:student_id>/follow/", follow_student, name="follow_student"),
    path("students/<int:student_id>/unfollow/", unfollow_student, name="unfollow_student"),
]
