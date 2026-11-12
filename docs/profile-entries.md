# Readable profile projects and experience

The profile screen introduced in PR #86 displayed projects and experience as raw JSON. The `polish-profile-entries` change provides readable display and ordinary editor controls for the existing US009 (#47) / US010 (#48) workflows. It is separate from following and does not close additional issues.

Projects and experience now use readable headings, descriptions and available supporting details. Known legacy aliases are understood, other metadata remains visible as labeled text, and only validated HTTP/HTTPS project links become clickable. All saved content remains escaped.

Students edit entries through ordinary fields. Saved rows show the entry's title or role. Add project/Add experience reveals a spare blank row before creating more; unused blank rows are hidden when JavaScript is active so they are not mistaken for duplicates. Remove this entry when saving is an explicit deletion control. One blank row per section also works without JavaScript. Invalid entries keep the entered values and show field errors without saving any part of the profile.

Storage remains in the existing JSON list fields. Untouched entries retain their exact values and types. Editing a supported field on a saved dictionary retains aliases and additional metadata. Historical non-text scalar/list entries remain readable and removable. The original complete-form JSON POST behavior, validation and owner restrictions remain supported. No migration or data rewrite is needed.

Regression coverage: `accounts.tests.ReadableProfileEntryTests` and `accounts.tests.ProfileEntryEditorTests` (12 new tests), alongside the existing profile form/workflow/presentation suites. The previous editor presentation test now asserts ordinary fields instead of JSON help text; the original JSON validation and workflow tests remain in place.

## Verification - 12 November 2026

- Full Django suite: 175 tests passed, including all 27 following tests and the 12 new profile-entry regression tests.
- Django system checks passed; no migration changes or pending migrations.
- Strict validation passed for both `polish-profile-entries` and `follow-student-profiles`; this presentation correction deliberately skips delta specs.
- `git diff --check` passed.
- Global strict OpenSpec validation has 14 passing items and the same pre-existing `seed-demo-ideas` missing-delta failure recorded in docs/student-following.md.
- Real Edge browser review passed 27 assertions with no JavaScript runtime errors: the exact reported project/role example, readable headings without raw JSON, ordinary editor fields, keyboard row addition/focus, unique labels, creation/persistence, visible validation and retained input, prevention of partial saves, removal in both sections, supporting metadata, safe project links, following controls, and 360/768/1440 layouts.
- Desktop and mobile screenshots of the corrected profile and the editor were visually inspected. Browser fixtures/captures remain in ignored `.venv/follow-review/`.
- Browser verification used isolated fixtures. This correction performs no schema migration or automatic data rewrite; local review data and credentials are not part of the implementation.

## Manual review

1. Apply migrations with `python manage.py migrate`, then start the app with `python manage.py runserver`.
2. Create a student account through Sign up. Open My profile, then Edit profile, and enter projects and experience using the ordinary fields.
3. Add another entry, save, and verify its readable presentation on My profile. Edit an entry and explicitly remove another one.
4. Enter a project description without a title, or an invalid project link. Confirm that the errors and typed values remain visible and the saved profile is unchanged.
5. Publish an idea as that student. Create an investor account, open the idea, and select its author to check the same readable profile and follow controls.
6. Repeat at mobile widths and use the keyboard to add and navigate entry fields.

Local review is complete. Peer review, integration into main, agreed-wireframe confirmation and Product Owner acceptance remain follow-up conditions. This correction does not close additional issues or archive OpenSpec changes automatically.

## Embedded-editor layout

The editor uses explicitly labelled block groups instead of nested native fieldset/legend wrappers. Collections and controls are bounded to the available width, and refreshed CSS/editor-script URLs prevent stale assets from retaining the previous layout. Local review in VS Code's embedded browser confirmed that the reported horizontal overflow is resolved.

Saved rows now show their project title or role. With JavaScript enabled, blank optional rows stay hidden until Add is selected, and an unused row is reused before another is cloned. The server-rendered blank row remains available without JavaScript; rows containing errors or entered values are not hidden.

Follow-up checks: 23 focused profile tests passed; JavaScript syntax, OpenSpec strict validation and diff checks passed. A live response from port 8000 was checked for labelled groups, unique IDs and refreshed asset URLs. No database entries were deduplicated or deleted.

These adjustments are included in PR #91 after local review. Peer review and integration into main remain pending. There is no schema or data change, and local credentials and databases remain excluded.
