# Design

## Context

See proposal.md for motivation and spec delta for the required record behavior. The `ideas` app currently defines `Idea` and `Category`; `Idea` points to `settings.AUTH_USER_MODEL`, and migrations and model tests live in the existing app. No feedback model or feedback capability exists yet.

## Goals / Non-Goals

**Goals:**
- Store a feedback item's target idea, author, text, and submission time in one model.
- Keep the implementation in the existing `ideas` app and follow its model, migration, admin, and test conventions.

**Non-Goals:**
- Do not add submission endpoints/forms, display templates, investor-only permissions, or user-facing validation messages in this change.
- Do not add privacy settings, replies, notifications, or a one-feedback-per-author rule.

## Decisions

- Define `Feedback` in `ideas/models.py`. Add a `ForeignKey` to `Idea` and a nullable `ForeignKey` to `settings.AUTH_USER_MODEL`; this follows the app's existing relationship conventions and preserves support for the configured custom user model.
- Use `related_name="feedback"` for both foreign keys, `text = TextField()` (required by Django model validation), and a `timestamp = DateTimeField(auto_now_add=True)`. The timestamp name follows issue #54, and automatic creation follows `Idea.published_at`.
- Use `on_delete=models.CASCADE` for the idea relationship because feedback depends on its target idea. For the author relationship, use `null=True` and `on_delete=models.SET_NULL`: feedback survives account deletion and its author reference becomes `NULL`. This policy was confirmed by the team for T22.
- Declare the text field with `blank=False`. This makes empty text fail model validation through `full_clean()`, but `save()` does not call `full_clean()` automatically. The user-facing prompt required by US005 when an investor submits empty feedback belongs to the later submission task, not T22; that task must validate submitted form data before saving.
- Register the model in `ideas/admin.py` with a small list view showing idea, author, and timestamp, consistent with the existing `IdeaAdmin`. Do not add broader moderation or privacy controls.
- Add one migration in the `ideas` app. No data backfill is required because the model is new.

## Risks / Trade-offs

- [Author deletion clears the author reference] → The confirmed `SET_NULL` policy preserves the feedback record while the deleted account can no longer be identified through its foreign key.
- [Direct ORM `save()` can store empty text unless callers validate] → `blank=False` is enforced by `full_clean()`, not automatically by `save()`. The later submission task must validate form data before saving. No database constraint is proposed because existing required idea text follows form/model validation conventions.
- [US005 also requires showing feedback with an idea and prompting on empty submission] → These user-facing behaviors are deliberately deferred to their separate tasks; this change tests only model-level data behavior.

## Migration Plan

Create the `ideas` migration for the new table and foreign keys. Apply it through the repository's normal migration workflow when implementation is approved. There is no existing feedback data to migrate. Rollback is the normal reverse migration, which removes the new table and its records.
