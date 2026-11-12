# Tasks

## 1. Readable entries

- [x] 1.1 Add shared entry presentation and readable profile templates/styles; verify project/role titles, metadata, mixed historical values, empty states, escaping and safe links with regression tests.

## 2. Conventional editor

- [x] 2.1 Add project/experience formsets, dynamic row addition and atomic form validation; verify create/edit/remove, exact preservation of untouched legacy entries, alias/metadata preservation, invalid/stale submission handling and the existing JSON POST contract with tests. Document the correction in docs/profile-entries.md.

## 3. Verification

- [x] 3.1 Restart the isolated preview and verify the reported project/experience example, editor add/edit/remove, validation, keyboard access and desktop/mobile layouts in a real browser; record results and confirm the normal database remains unchanged.
- [x] 3.2 Run system/migration checks, strict validation for both local changes, git diff --check and the full Django suite; record outcomes and complete local review before publication.
