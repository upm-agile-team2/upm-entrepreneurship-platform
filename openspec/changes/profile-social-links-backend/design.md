# Design

## Context

See `proposal.md` for motivation and the retrospective-documentation status. The existing `StudentProfile` is tied to a student account, and `StudentProfileForm` already handles profile editing through an authenticated, student-only endpoint. T77 extends those structures. T78 supplies the ordinary-page inputs and clickable icons; T77 alone does not satisfy the story's display and navigation criteria.

## Goals / Non-Goals

**Goals:** preserve URLs across saves, support optional values, and use the same validation rules for model validation and the profile form.

**Non-Goals:** introduce a second profile model, a separate API, or new account permissions. This follow-up documents existing code only.

## Decisions

### Extend the current model with four explicit fields

Use `instagram_url`, `twitter_url`, `youtube_url`, and `github_url` as `URLField` values on `StudentProfile`. Each has `max_length=500`, `blank=True`, and `default=""`. Explicit fields match the four requested platforms and allow the model form to derive the editor fields. A separate account-link model or JSON container would add unnecessary structure for the fixed set requested in #130.

Empty strings represent missing URLs; `null=True` is unnecessary for these text fields. The migration adds the columns while allowing existing profiles to keep their current data and begin with empty social links.

### Keep validation on the model fields and use the existing model form

Each field includes `URLValidator(schemes=["http", "https"])`. Include all four fields in `StudentProfileForm.Meta.fields`; the existing view then validates them through `form.is_valid()` and persists through `form.save()`. Invalid submissions keep the database unchanged, including other submitted profile values.

The 500-character limit is a field-size choice. Validation checks format and protocol, not platform domains or the existence of a social account. The icon identity in T78 is determined by the field, not by inspecting the host name.

### Preserve compatibility with older profile submissions

The fields have defaults, so an omitted social input can preserve an existing value through the model form's default-handling behavior. Explicit empty input clears the value. Existing profile-editor submissions therefore remain usable before T78's inputs are present. Tests distinguish omission from an intentional clear.

## Risks / Trade-offs

- Direct model `save()` and bulk updates do not run field validation. Scripts that need validation must call `full_clean()` or use a validated form. T78 also filters invalid stored URLs before rendering external links.
- The model supports student profiles only. Extending social links to investor-owned profiles would require a separate model and permission decision.
- The generic URL rule allows a valid HTTP/HTTPS host different from the named platform. Domain allowlists and account verification remain outside the agreed scope.

## Migration Plan

The implemented migration is `accounts/0009_add_profile_social_urls`, depending on `0008_merge_follow_profile_visit`. It contains four `AddField` operations. Run normal deployment migrations before application code relies on the columns. No data migration is required.

These retrospective documents do not create, rerun, or replace a migration. Reversing the schema migration would remove the stored URL columns and their data; documentation completion does not require that reversal.

## Verification Evidence

- T77 model tests cover saving, clearing, optional values, malformed URLs, disallowed protocols, and overlong input.
- T77 form tests cover create/update/clear, omitted values, preservation of existing URLs, and field errors.
- Request tests cover the actual editor submission and unchanged persisted data after invalid input.
- Recorded T77 results: 9 model, 11 form, and 13 workflow tests passed; the full T77 snapshot passed 235 tests and had no pending model changes.
- The combined T77/T78 implementation subsequently passed 239 tests. This documentation-only follow-up does not alter that implementation.
- The original backend-only PR (#135) has not merged and is superseded by the planned combined PR from `T77-T78-profile-social-media` to `main`. Review, merge, integrated-MVP verification, and Product Owner acceptance remain separate from local test results.
