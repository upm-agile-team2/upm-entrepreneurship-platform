# Tasks

## 1. Feedback model and admin

- [x] 1.1 Add `Feedback` to `ideas/models.py` with an `Idea` foreign key using `CASCADE`, a nullable foreign key to `settings.AUTH_USER_MODEL` using `SET_NULL`, required text, and an automatically populated `timestamp`; create the `ideas` migration and verify it with `python manage.py makemigrations --check --dry-run`.
- [x] 1.2 Register `Feedback` in `ideas/admin.py` with the minimal fields described in the design and verify the Django configuration with `python manage.py check`.

## 2. Feedback model tests

- [x] 2.1 Add a model test that creates non-empty feedback for an idea by an investor, refreshes it from the database, and verifies the idea, author, text, and submitted timestamp are retained; run the focused test. This covers persistence and author association for US005 (#43). The later display task must test that the interface actually identifies the feedback author; this model test does not cover display.
- [x] 2.2 Add a model-validation test showing empty text fails `full_clean()` for a `Feedback` instance; run the focused test. The user-facing prompt required by US005's empty-submission criterion remains for the later submission task.

## 3. Integration verification

- [x] 3.1 Run `python manage.py makemigrations --check --dry-run` and `python manage.py test`; confirm all model tests and the existing suite pass, and review the README Definition of Done for T22. Keep the broader US005 story open until its separate submission and display tasks are complete.
