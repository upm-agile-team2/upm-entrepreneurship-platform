"""Shared student profile data for profile views and invitation responses."""

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from ideas.forms import CollaboratorRequestForm

from .models import StudentProfile
from .profile_entries import present_entries


def profile_display_context(student):
    profile = (
        StudentProfile.objects.filter(user=student)
        .prefetch_related("skills")
        .first()
    )
    social_links = []
    if profile:
        validate_url = URLValidator(schemes=["http", "https"])
        for platform, label in (
            ("instagram", "Instagram"), ("twitter", "Twitter"),
            ("youtube", "YouTube"), ("github", "GitHub"),
        ):
            url = getattr(profile, f"{platform}_url")
            if not url:
                continue
            try:
                validate_url(url)
            except ValidationError:
                continue
            social_links.append({"platform": platform, "label": label, "url": url})
    return {
        "student": student,
        "profile": profile,
        "social_links": social_links,
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
