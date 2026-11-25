# Proposal

## Why

T77 (#130), part of US0034 (#105), provides persistent social account URLs so users can share more about their background. Profile editing needs optional storage and backend validation before T78 can expose those links on ordinary pages.

## What Changes

- Extend the existing student profile with optional Instagram, Twitter, YouTube, and GitHub URL fields and a database migration.
- Include those fields in the existing profile form so valid submitted URLs can be created, updated, or cleared.
- Validate URL format and allow HTTP/HTTPS links; reject invalid submissions without saving profile changes.
- Preserve saved social URLs when an existing client omits their fields.
- Cover model, form, and request-level persistence and validation with Django tests.

## Documentation Status

This is retrospective documentation of the implemented T77 change. The original T77 PR (#135) has not merged. Its implementation commit `054f36c`, the T78 UI, and both documentation packages are included in the `T77-T78-profile-social-media` branch for one combined PR. These documents do not claim proposal review before coding.

## Delivery

Submit `T77-T78-profile-social-media` to `main` as one PR covering T77 (#130) and T78 (#131), with `Closes #130`, `Closes #131`, and `Supersedes #135` in its description. Close the superseded backend-only PR without merging it. Keep separate backend and UI documentation packages so their scopes and acceptance evidence remain clear.

## Out of Scope

- Editor layout, public-profile social icons, and external navigation: T78 (#131) records these in `profile-social-links-ui`.
- Registration fields, investor-owned profiles, and profile access-permission changes.
- Platform-domain restrictions, real-account verification, social authentication, or image uploads.
- Reapplying the already-created migration or making a second schema change as part of this documentation update.

## Capabilities

### New Capabilities

- `profile-social-links`: persist and validate optional URLs associated with student social accounts. The companion T78 delta uses the same capability path for its distinct editing and display requirements.

### Modified Capabilities

None. The current main specs describe authentication and ideas; general student-profile requirements remain in earlier pending changes.

## Impact

The implemented T77 change affects `accounts/models.py`, `accounts/forms.py`, `accounts/migrations/0009_add_profile_social_urls.py`, and `accounts/tests.py`. It uses the existing student-only editor and requires no new endpoint or dependency.

This documentation follow-up adds OpenSpec documents only. It does not change application behavior or the existing migration. A combined T77/T78 PR must include the pending backend commit as well as the UI changes and both documentation packages.

Refs #130; user story US0034 (#105); implementation PR #135; companion presentation task T78 (#131).
