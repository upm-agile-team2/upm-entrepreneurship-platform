# Design

## Context

See proposal.md for motivation. The `accounts` app defines the configured custom `User` model and its `Role` choices. The `ideas` app and `User` model already use `UniqueConstraint(Lower("name" or "email"))` for case-insensitive uniqueness, while model tests cover that behavior with `IntegrityError` inside `transaction.atomic()`.

## Goals / Non-Goals

**Goals:**
- Represent the agreed profile fields with Django relationships and JSON list fields.
- Make student-role validation explicit at the model-validation boundary.
- Keep skills reusable and queryable for the separately scoped future filtering work.

**Non-Goals:**
- Define the structure of individual project or experience list entries.
- Add profile workflows, pages, search/filter behavior, or user-facing validation.

## Decisions

- Add `StudentProfile` and `Skill` in `accounts/models.py`, next to the custom user. Use `StudentProfile.user = OneToOneField(settings.AUTH_USER_MODEL, related_name="student_profile", ...)`, so each user can have at most one profile. Proposed user deletion behavior is `CASCADE`, matching the existing `Idea.owner` convention for user-owned data. Neither #63 nor #47 states a retention policy, so confirm this proposed deletion behavior before implementation.
- Define `bio` as `TextField(blank=True)`, representing an optional value as an empty string when omitted. Keep `portfolio_projects` and `experience` as `JSONField(default=list)`. A callable default gives each profile its own empty list; no separate project or experience models are introduced.
- Define `Skill` with a `name` `CharField` using the existing `Category.name` length convention (`max_length=100`) and a `UniqueConstraint(Lower("name"), ...)`. A normalized many-to-many relationship lets profiles share skills and gives the future US012 (#50) filtering work in T37 (#69) a queryable relation. This change adds no filtering behavior.
- Add `StudentProfile.skills` as a many-to-many field to `Skill`, with a `profiles` reverse name. No additional skill metadata is introduced.
- Validate the student-only rule in `StudentProfile.clean()` using the configured user's existing student-role convention. Django calls `clean()` from `full_clean()`, but `save()` does not automatically call `full_clean()`. This is model-level validation only; it is not a database-level constraint. Tests must call `full_clean()` for the investor rejection case.
- Create one additive migration in `accounts`. No existing profile data requires backfilling.

## Risks / Trade-offs

- [A direct `save()` can bypass student-role validation] → Later profile creation/editing code must validate the model (or enforce the role in its form/service); this T31 change does not claim a database-level role constraint.
- [User deletion removes the associated profile under the proposed `CASCADE` behavior] → This follows the existing user-owned `Idea` relationship, but the issues do not define retention. Confirm this proposal assumption before implementation.
- [JSON list entries have no schema] → Keep them as lists as requested; define entry structure only if a later task requires it.

## Migration Plan

Generate an `accounts` migration for `Skill`, `StudentProfile`, their uniqueness constraint, one-to-one and many-to-many relationships, and JSON fields. Apply it through the normal migration workflow after approval. Rollback is the reverse migration, which removes the new tables and their data.
