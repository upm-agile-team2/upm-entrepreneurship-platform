# Tasks

## 1. Readable entries

- [x] 1.1 Add shared entry presentation and readable profile templates/styles; verify project/role titles, metadata, mixed historical values, empty states, escaping and safe links with regression tests.

## 2. Conventional editor

- [x] 2.1 Add project/experience formsets, dynamic row addition and atomic form validation; verify create/edit/remove, exact preservation of untouched legacy entries, alias/metadata preservation, invalid/stale submission handling and the existing JSON POST contract with tests. Document the correction in docs/profile-entries.md.
- [x] 2.2 Clarify saved-entry headings and hide/reuse unused blank rows when JavaScript is enabled; verify editor rendering, invalid-input preservation, existing formset behavior and JavaScript syntax, and record local review results.
- [x] 2.3 Replace nested native fieldset/legend wrappers with labelled, width-bounded groups and refresh editor asset URLs; verify rendered form semantics, preserved entry controls, focused regression tests and JavaScript syntax, and obtain local confirmation that VS Code overflow is resolved before updating the PR.

## 3. Verification

- [x] 3.1 Restart the isolated preview and verify the reported project/experience example, editor add/edit/remove, validation, keyboard access and desktop/mobile layouts in a real browser; record results and confirm the normal database remains unchanged.
- [x] 3.2 Run system/migration checks, strict validation for both local changes, git diff --check and the full Django suite; record outcomes and complete local review before publication.

## Review follow-up

- Local review in VS Code confirmed that the reported horizontal overflow is resolved.
- Publish the reviewed adjustments in PR #91; peer review and main integration remain pending.
