# Tasks

Retrospective record for T77 (#130), US0034 (#105), implementation commit `054f36c` and PR #135. That PR has not merged. Checked implementation items reflect code and test evidence, not a pre-implementation proposal review or a completed merge. T78's companion change records the story's display and open-link criteria and their presentation tests.

## 1. Profile storage and migration

- [x] 1.1 Extend `StudentProfile` with four optional URL fields. Verify `test_social_media_urls_are_saved_and_can_be_cleared`, `test_social_media_urls_are_optional`, and `test_social_media_urls_reject_invalid_values` cover persistence, empty defaults, protocol validation, and length limits.
- [x] 1.2 Add migration `0009_add_profile_social_urls` with four `AddField` operations and no replacement of existing profile data. Verify it depends on `0008_merge_follow_profile_visit`, the local migration applied successfully, and the model-drift check reported no changes.

## 2. Form validation and backend persistence

- [x] 2.1 Include all four social fields in `StudentProfileForm` and reuse the current student's editor save path. Verify `test_form_saves_updates_and_clears_social_media_urls` and `test_editor_post_creates_updates_and_clears_social_media_urls` cover the story's save criterion at form and request levels.
- [x] 2.2 Preserve compatibility with submissions lacking social fields while allowing explicit clearing. Verify `test_form_accepts_omitted_social_media_urls_for_new_profile` and `test_form_preserves_existing_social_media_urls_when_omitted` pass alongside the update/clear tests.
- [x] 2.3 Reject invalid URL submissions without persisting changes. Verify `test_form_reports_invalid_social_media_urls_on_each_field` and `test_invalid_social_media_post_preserves_existing_profile` report field errors and preserve the stored profile.

## 3. Documentation and integration verification

- [x] 3.1 Deliver the issue-linked retrospective proposal, backend spec, design, and this checklist. Verify the package distinguishes T77 storage/validation from T78 presentation and does not claim prior approval or a new schema change.
- [x] 3.2 Run `openspec validate profile-social-links-backend --strict`, `openspec validate profile-social-links-ui --strict`, `openspec validate --all`, and `git diff --check`. Both strict checks passed, repository-wide validation passed all 20 items, and the diff check passed.
- [x] 3.3 Run `python manage.py test` and `python manage.py makemigrations --check --dry-run`. Recorded T77 results were 235 passing tests and no model drift; the unchanged combined T77/T78 implementation later passed 239 tests. This follow-up changes documents only.
- [ ] 3.4 Check the README Definition of Done for the complete story: obtain teammate review of the implementation and new documents, merge the accepted changes, verify the integrated MVP and agreed wireframes with T78, and confirm Product Owner acceptance in Sprint Review. Local tests alone do not establish these remaining acceptance records.

## Workflow follow-up

- Submit the `T77-T78-profile-social-media` branch to `main` with both tasks' code and documentation. Use `Closes #130`, `Closes #131`, and `Supersedes #135`; close the superseded backend-only PR without merging it. The branch already contains T77 commit `054f36c`.
- After the team's remaining review and acceptance requirements are satisfied, archive the backend and UI changes through the archive workflow. Both deltas target `profile-social-links` and add distinct requirement names, so preserve both sets when syncing the capability.
