# Proposal

## Why

T32 (#64), linked to US009 (#47), adds the backend needed for a signed-in student to create and update their own profile. T31 supplies the `StudentProfile` and `Skill` models, but the application currently has no profile form, routes, or views to save and retrieve that data.

## What Changes

- Add a profile `ModelForm` for bio, existing skills, portfolio projects, and experience.
- Add authenticated student-only view and URL behavior that creates a profile for the current student or updates that student's existing profile, and makes saved data available for later viewing.
- Validate project and experience values as JSON lists without imposing a schema on individual entries; use the existing `Skill` relationship for skill selection.
- If the server-rendered endpoint needs a template before T33, add only an unstyled functional scaffold; T33 owns the final editor and profile-view layout.
- Add focused tests for create, retrieve, update, validation, login and role restrictions, and protection against editing another student's profile.

This change is backend functionality only. T33 (#65) owns the editor screen and profile-view layout. Investor-facing profile pages, skill filtering, following, notifications, analytics, and feedback functionality are out of scope.

Experience handling follows the field provided by T31 (#63); it is not a separate acceptance criterion in US009 (#47). JSON-list validation is a model-compatible form behavior, not an additional user-story criterion.

Refs #64; parent user story US009 (#47). This change depends on T31 (#63) and extends its pending `student-profiles` capability on the stacked branch.

## Capabilities

### New Capabilities

- `student-profiles`: create, retrieve, and update the signed-in student's profile data, extending the capability introduced by T31 (#63).

### Modified Capabilities

None.

## Impact

- `accounts/forms.py`: add profile form validation.
- `accounts/views.py` and `accounts/urls.py`: add own-profile create/update and retrieval behavior.
- `accounts/tests.py`: test profile persistence, validation, and access restrictions.
- `templates/accounts/`: only a minimal unstyled form scaffold if needed for the backend endpoint.
- No model, migration, settings, or final visual layout changes; T31 owns the model and migration, and T33 owns the designed templates.
