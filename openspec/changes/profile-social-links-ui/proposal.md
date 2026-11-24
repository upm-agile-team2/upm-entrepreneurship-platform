# Proposal

## Why

T78 (#131), part of US0034 (#105), lets students share their social and professional background through their profiles. T77 (#130) supplies storage and validation, but ordinary users need editable URL inputs and viewers need clickable platform icons.

## What Changes

- Add optional Instagram, Twitter, YouTube, and GitHub inputs to the existing student profile editor, reusing T77's form validation and persistence.
- Display the available links as platform icons with visible names on the shared own-profile and investor-facing profile page; omit empty links and omit the section when none are available.
- Open the saved external URL in a new tab and retain the current profile page.
- Reuse the existing Bootstrap presentation and bundle inline SVG icons with their license notice.
- Cover editing, visible validation errors, investor-facing display, missing links, and external link targets with Django tests.

## Documentation Status

These artifacts were written after the implementation and its automated tests. They record the actual change for review; they do not assert that a proposal was reviewed before coding. Team review, integrated-MVP acceptance, and Product Owner acceptance remain separate from local implementation and test completion.

## Delivery

Submit `T77-T78-profile-social-media` to `main` as one PR containing T77's pending backend, T78's UI, and both documentation packages. Use `Closes #130`, `Closes #131`, and `Supersedes #135` in the description. Close the superseded T77-only PR without merging it. The backend and UI documents continue to describe their individual task scopes.

## Out of Scope

- T77's model fields, migration, and backend form persistence: these are recorded separately under #130 and are included in the overall combined PR, rather than being additional T78 implementation work.
- Social URL inputs during registration, investor-owned profiles, or changes to existing profile access permissions.
- Platform-domain restrictions, account-existence checks, OAuth connections, or automatic platform detection from URLs.
- Avatars, chat, notifications, and collaborator features.

## Capabilities

### New Capabilities

- `profile-social-links`: edit and present external social links associated with student profiles, extending the storage requirements recorded separately in `profile-social-links-backend`.

### Modified Capabilities

None. The current main specs describe authentication and ideas; the existing general student-profile specifications are still in pending changes.

## Impact

- `accounts/views.py`: expose social form fields and prepare validated available links for the shared profile view.
- `templates/accounts/student_profile_form.html`: render the optional social input group with the shared field partial.
- `templates/accounts/student_profile_detail.html` and `templates/accounts/includes/social_icon.html`: render platform icon links.
- `docs/licenses/bootstrap-icons.txt`: retain the Bootstrap Icons license.
- `accounts/tests.py`: extend `StudentProfilePresentationTests` for the three acceptance criteria.
- `openspec/changes/profile-social-links-backend/`: include the retrospective T77 documentation alongside its pending backend implementation, which has not merged.
- Existing `prepare-sprint2-experiments` and `seed-demo-ideas` changes: add `skip_specs: true` metadata so OpenSpec 2.1.1 recognizes their already-declared lack of specification changes during repository-wide validation.
- T78 adds no further model, migration, route, JavaScript package, or authentication change beyond T77. The backend and UI are delivered together in the combined PR.

Refs #131; user story US0034 (#105); depends on T77 (#130).
