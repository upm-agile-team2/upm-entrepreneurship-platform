# Proposal

## Why

T33 (#65) and T34 (#66) complete the presentation layer for student profiles. T32 already provides student-only profile creation and updating; students still need a usable editor and an own-profile view, while investors need an authorized way to open and read student profile information.

T33 belongs to US009 (#47), which covers creating, viewing, and editing a student's profile. T34 belongs to US010 (#48), which covers investors opening a student's profile, viewing skills, projects, and experience, and handling incomplete profiles.

## What Changes

- Replace the T32 form scaffold with a Bootstrap-styled student profile editor using the existing `StudentProfileForm` and its supported fields.
- Add a read-only view for the signed-in student's own profile, with a route back to editing.
- Add an investor-only profile view reachable from a student's name on an idea detail page.
- Render absent profile data with clear empty states, including students who have not created a profile yet.
- Add tests for presentation, route access, profile content, privacy, incomplete data, and existing T32 behavior.

This change uses the existing `StudentProfile` and `Skill` models and T32 form. It does not alter the database schema.

## Out of Scope

- Profile discovery, search, filtering, or following (T35/T37 and later tasks).
- Student-created free-text skills or skill catalogue seed data.
- Structured portfolio/experience schemas; T31 leaves JSON list entries unconstrained.
- Editing by investors, profile analytics, notifications, or feedback functionality.
- Changes to authentication, account roles, or model relationships.

## References

Refs #65, #66; US009 (#47); US010 (#48); depends on T31 (#63) and T32 (#64).

## Capabilities

### Modified Capabilities

- `student-profiles`: add student-facing profile editing/viewing and investor-facing profile viewing.

## Impact

- `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`: add editor guidance and read-only own-profile and investor-profile routes.
- `templates/accounts/`: implement the editor and profile detail presentation.
- `templates/base.html`, `templates/ideas/idea_detail.html`, `ideas/views.py`: add student navigation and a profile link for investors.
- `accounts/forms.py`: add only presentation help text if needed for the existing fields.
- `accounts/tests.py`, `ideas/tests.py`: cover UI behavior and access rules.
- No model, migration, dependency, or settings changes.
