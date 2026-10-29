# Design

## Context

`ideas/` is an empty app: `models.py` is a comment, `views.py` only has the placeholder `home` view and `ideas/tests.py` has one test for it. `accounts.User` already has a `role` (`student` or `investor`) and an `is_student` property. The start page `ideas:home` is public by default, and `AnonymousAccessMiddleware` only protects pages when `DJANGO_ALLOW_ANONYMOUS_ACCESS=False`, so the publishing view cannot rely on it. `LOGIN_URL` is not set; Django's default `/accounts/login/` happens to match `accounts:login`. See proposal.md for scope.

The UX Design Studio chose option A, "one page": Title, Description, Category (dropdown) and a **Publish** button, in that order.

## Goals / Non-Goals

**Goals:**
- A student can publish an idea from one page, and the idea is stored with its owner and publication date.
- The list of categories is data, shown as a dropdown, and can be changed without a code change.
- US002 (edit), US003 (list and filter) and US004 (detail) can reuse the same models.

**Non-Goals:**
- Draft or unpublished states, moderation, or deleting ideas.
- Free-text categories or categories created by students.
- Any listing or detail view of ideas.

## Decisions

### `Category` is a model, with its initial list loaded by a data migration
`Category(name)` with a unique, case-insensitive name. A data migration inserts the initial list, so every environment (development, CI, Render) starts with the same dropdown. It is registered in the admin so the list can be maintained without deploying.

Alternatives: a `TextChoices` enum on `Idea` is simpler but fixes the list in code and needs a deploy to change it; a free-text field was rejected by the wireframes ("fixed list").

The initial list is a proposal to confirm with the Product Owner. Proposed: Technology, Health, Education, Sustainability, Finance, Social impact, Other. Changing it later only touches the data migration or the admin.

### `Idea` fields and the meaning of "published"
`Idea` has `title` (max 200), `description` (text), `category` (optional foreign key to `Category`, `on_delete=PROTECT`, so a category in use cannot be deleted by accident), `owner` (foreign key to the user model, `on_delete=CASCADE`) and `published_at` (`auto_now_add`). There is no `status` field: US001 says a submitted idea is published and available, and no story asks for drafts. If drafts appear later, a field can be added then with a migration.

Category is optional because no US001 criterion requires it. The dropdown shows an empty choice.

### Validation lives in a `ModelForm`
`IdeaForm` exposes `title`, `description` and `category`, in the wireframe order. Title and description are required, and the form strips whitespace so a title made only of spaces counts as missing. The template shows the error under each field with Bootstrap's `is-invalid` and `invalid-feedback`, which is how the platform "asks them to complete the missing information". The owner is set in the view, never taken from the form, so it cannot be forged.

Alternative: validating in the view or the model's `clean()`. A form is the idiomatic place for request validation and also drives the rendered fields.

### One view for GET and POST, restricted to signed-in students
`publish_idea` (URL name `ideas:publish`, path `ideas/new/`) shows the form on GET and, on a valid POST, creates the idea with `owner=request.user`, adds a success message and redirects to `ideas:home` (post/redirect/get). On an invalid POST it re-renders the form with a 200 status and does not create anything.

Access rules, enforced in the view itself:

| Visitor | Result |
|---|---|
| Not signed in | Redirect to the login page, keeping `next` |
| Signed in as investor | 403 |
| Signed in as student | Form / publish |

Implemented with `login_required` plus a role check. The role check raises `PermissionDenied` for non-students. The redirect target is set explicitly through `reverse_lazy("accounts:login")` instead of depending on Django's default `LOGIN_URL`.

### Where the student lands after publishing
The home page, with a success message, because the detail page does not exist until US004. When US004 lands, the redirect can point to the new idea without changing the form or the model.

### Navigation
`base.html` gets a "Publish an idea" link, shown only to signed-in students. Hiding the link is cosmetic; the view enforces the rule.

## Risks / Trade-offs

- [The initial category list may not match what the Product Owner expects] → It is data: change it in the admin or in the data migration before the Sprint Review.
- [A data migration for categories makes tests depend on seeded rows] → Tests that need categories create their own rows, and tests that need none do not assume the seeded ones.
- [`on_delete=PROTECT` blocks deleting a category that has ideas] → Intended; the admin shows the protection message. Renaming a category is always possible.
- [No status field means unpublishing needs a later change] → Accepted; no story requires it in Sprint 1.
- [Multiple "required information" checks only on title and description] → Matches the acceptance criteria; category stays optional.

## Migration Plan

1. `makemigrations ideas` creates the schema migration for `Category` and `Idea`.
2. A second, data migration inserts the initial categories (reversible: deletes only those names).
3. `migrate` runs on deploy. Rollback is `migrate ideas zero`, which drops both tables; there is no production data yet.

CI runs `makemigrations --check --dry-run`, so the migration files must be committed with the models.
