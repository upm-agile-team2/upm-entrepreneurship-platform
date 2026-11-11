# Proposal

## Why

T31 (#63), linked to US009 (#47), needs a persistent model for students to maintain profile information that can showcase their skills and projects to potential investors. The existing custom user model has no profile or skill models, so the data foundation is not yet available for the later profile creation, display, and editing work.

## What Changes

- Add `StudentProfile` and `Skill` models to the existing `accounts` app.
- Associate one profile with each user, validate that the associated user is a student, and store optional bio, skills, portfolio projects, and experience using the agreed field types.
- Enforce case-insensitive uniqueness for skill names, following the existing `Lower`-based uniqueness constraints.
- Add an accounts migration and focused Django model tests.

This change is limited to the data model. Profile creation and editing views or forms, profile pages, investor-facing profile display, skill filtering, following, notifications, analytics, and feedback functionality are out of scope.

Refs #63; parent user story US009 (#47).

## Capabilities

### New Capabilities

- `student-profiles`: persistent student profile data and associated skills.

### Modified Capabilities

None.

## Impact

- `accounts/models.py`: add `StudentProfile` and `Skill`.
- `accounts/migrations/`: add the schema migration.
- `accounts/tests.py`: add focused model tests.
- No views, forms, templates, routes, dependencies, or project settings change.
