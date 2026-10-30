# Proposal

## Why

Students need to correct or improve ideas after publication. Editing must preserve ownership so that only the student who published an idea can change it.

## What Changes

- Add an edit route and view for a student's published idea.
- Reuse the idea form to update title, description, and optional category, retaining required-field validation and inline errors.
- Return HTTP 403 for users who are not students or do not own the idea.
- Add tests for successful owner edits, denied edits, and invalid required fields.

Out of scope: editing ideas as an investor, editing another student's idea, and changes to idea discovery or detail pages.

Refs #19 #5 (US002).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: specify editing published ideas and owner-only access.

## Impact

- `ideas/views.py`, `ideas/urls.py`, `ideas/forms.py`, `ideas/tests.py`, and the idea form template.
- No model or database changes.
