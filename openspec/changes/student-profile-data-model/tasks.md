# Tasks

## 1. Student profile and skill models

- [x] 1.1 Add `Skill` and `StudentProfile` to `accounts/models.py` as specified in design.md, including the case-insensitive skill-name constraint, then create the `accounts` migration and verify it with `python manage.py makemigrations --check --dry-run`.

## 2. Model tests

- [x] 2.1 Add model tests in `accounts/tests.py` for profile-to-user one-to-one behavior, optional bio, independent empty-list defaults for portfolio projects and experience, and many-to-many skill associations; run the focused tests.
- [x] 2.2 Add a case-insensitive skill-name uniqueness test using the existing `IntegrityError` and `transaction.atomic()` convention; run the focused test.
- [x] 2.3 Add model-validation tests showing a student-owned profile passes `full_clean()` and an investor-owned profile fails it; document in the test that `save()` does not call `full_clean()` automatically; run the focused tests.
- [x] 2.4 Add a test for the proposed user-deletion behavior: deleting the profile's user cascades to that profile; run the focused test.

## 3. Integration verification

- [x] 3.1 Run `python manage.py makemigrations --check --dry-run`, `python manage.py check`, and `python manage.py test`; confirm the suite passes and review the README Definition of Done for T31. The view, edit, display, and filtering acceptance criteria remain for their separate tasks.
