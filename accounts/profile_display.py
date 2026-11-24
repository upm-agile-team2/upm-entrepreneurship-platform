"""Shared student profile data for profile views and invitation responses."""

from ideas.forms import CollaboratorRequestForm

from .models import StudentProfile
from .profile_entries import present_entries


def profile_display_context(student):
    profile = (
        StudentProfile.objects.filter(user=student)
        .prefetch_related("skills")
        .first()
    )
    return {
        "student": student,
        "profile": profile,
        "skills": profile.skills.all() if profile else [],
        "portfolio_projects": (
            present_entries(profile.portfolio_projects, "project") if profile else []
        ),
        "experience_entries": (
            present_entries(profile.experience, "experience") if profile else []
        ),
    }


def collaborator_profile_context(viewer, student, *, form=None):
    if form is None:
        form = CollaboratorRequestForm(owner=viewer)
    context = profile_display_context(student)
    context.update({
        "is_own_profile": False,
        "collaborator_request_form": form,
        "has_owned_ideas": form.fields["idea"].queryset.exists(),
    })
    return context
