# Proposal

## Why

Hypothesis H1 (reach 20 published ideas per month) cannot be validated until a student can publish an entrepreneurial idea. US001 (#4) is the first story of Sprint 1 and every other idea story (edit, browse, filter, view details) depends on ideas existing in the database. `ideas/` is still an empty app, so the data model, the publishing logic and the submission screen are all missing.

## What Changes

- Add the `Idea` model (title, description, category, owner, publication date) and a `Category` model with an initial list of categories loaded by a data migration (T09, #16).
- Add publishing of an idea by a signed-in student, with validation that rejects a missing title or description and asks the student to complete them (T10, #17).
- Add the one-page submission form agreed in the UX Design Studio (option A): Title, Description, Category (dropdown) and a **Publish** button, in that order (T11, #18).
- Add a navigation link to the form for signed-in students.
- Publishing an idea creates it as published: there is no draft state in US001.
- After publishing, the student returns to the start page with a success message, because the idea detail page belongs to US004.
- Add Django tests for each acceptance criterion of US001.

Out of scope:
- Editing ideas and changing their category afterwards (US002, #5).
- The discovery list and the category filter (US003, #6).
- The idea detail page (US004, #7).
- Drafts or any publication workflow beyond creating the idea.
- Task T17 (#24, tests for the experiment stories), T18 (#25, prototype and sample ideas) and T19 (#26, deployment).

Source: US001 (#4); tasks T09 (#16), T10 (#17) and T11 (#18).

Refs #4. Closes #16, closes #17, closes #18.

## Capabilities

### New Capabilities

None. The behaviour belongs to the existing `ideas` capability.

### Modified Capabilities

- `ideas`: the two US001 requirements, *Submit an idea* and *Require essential information*, gain scenarios that make the agreed behaviour testable: the category chosen from the list of categories, and a separate scenario for each of the two required fields with nothing being published.

## Impact

- `ideas/`: new `Category` and `Idea` models, an initial migration with the categories, a `ModelForm`, a publish view and URL, and tests.
- `templates/ideas/`: new submission form template following the wireframe; `templates/base.html`: a link to the form for signed-in students.
- `accounts/`: unchanged. The `User.role` field and `is_student` property are reused to restrict publishing to students.
- Database: two new tables (`ideas_category`, `ideas_idea`). CI already runs `makemigrations --check`, so the migration must be committed.
- No new dependencies.
