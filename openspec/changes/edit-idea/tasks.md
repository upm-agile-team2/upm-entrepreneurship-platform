# Tasks

## 1. Edit published idea (T12, #19)

- [x] 1.1 Add the owner- and student-restricted `edit_idea` view and `/ideas/<int:idea_id>/edit/` route, reusing `IdeaForm` to update title, description, and category.
- [x] 1.2 Update the shared idea form template to show the appropriate edit heading and save button while rendering inline validation errors.
- [x] 1.3 Add tests for a successful owner edit, 403 for another user and non-student, and missing or whitespace-only title/description without saving changes.

## 2. Final checks

- [x] 2.1 Run `python manage.py test` and verify the whole suite passes.
- [x] 2.2 Run `openspec validate --all` and check the Definition of Done in the README.
