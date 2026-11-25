# Design

## Context

See proposal.md for motivation and the spec delta for the required record behavior. The project has two apps, `accounts` (custom `User` with email login and a Student/Investor role) and `ideas`. `ideas.Feedback` and `ideas.Reply` already store authored text with a nullable `SET_NULL` author, `blank=False` text, an `auto_now_add` timestamp, and ascending timestamp ordering. Apps use `BigAutoField` primary keys. No chat model exists yet.

## Goals / Non-Goals

**Goals:**
- Store conversations, their participants, and their messages in a new `chat` app that follows the conventions of `ideas.Feedback`.
- Give T67 and T68 a stable model to build on without changing it again.

**Non-Goals:**
- No views, URLs, forms, templates, or services. These come in T67 and T68.
- No rule that a conversation has exactly two participants, and no rule against duplicate conversations for the same pair. T67 enforces both when it creates conversations.
- No read status, editing, deletion by users, or notifications.

## Decisions

- **A new `chat` app instead of adding models to `ideas`.** Chat is between users and does not depend on ideas, so it gets its own capability and app. This is a Django app inside the same project, served by the same server. Alternative: put the models in `ideas` next to `Feedback`. Rejected because it would mix an unrelated feature into the ideas app and spec.
- **`Conversation.participants` is a `ManyToManyField` to `settings.AUTH_USER_MODEL`** with `related_name="conversations"`, plus `created_at = DateTimeField(auto_now_add=True)`. The issue lists only an id for conversations, but a conversation must know who takes part in it. Alternative: two foreign keys, `user_a` and `user_b`. Rejected because every query would have to check both columns and the pair ordering. A many-to-many relation keeps "conversations of this user" as a single lookup. The trade-off is that the database cannot enforce two participants or unique pairs (see Risks).
- **`Message` fields match the issue:** `conversation` foreign key (`CASCADE`, `related_name="messages"`), `sender` foreign key to the user model (`null=True`, `SET_NULL`, `related_name="sent_messages"`), `text = TextField(blank=False)`, and `timestamp = DateTimeField(auto_now_add=True)`. `CASCADE` is used because messages have no meaning without their conversation. `SET_NULL` keeps the history readable after an account is deleted, matching the confirmed `Feedback.author` policy. The `id` fields come from the default `BigAutoField`.
- **`Message.Meta.ordering = ["timestamp", "id"]`.** `conversation.messages.all()` then returns messages oldest first without each caller adding `order_by`. `id` breaks ties when two messages share a timestamp. `Conversation` is ordered by `-created_at`, so the newest conversation comes first.
- **Empty text is a model-validation rule.** `blank=False` makes `full_clean()` reject empty text, as for `Feedback`. `save()` does not call `full_clean()`, so T67 must validate before saving, and T68 must show the "please enter text" prompt.
- **Admin:** register `Conversation` (list shows id and `created_at`; `filter_horizontal` for participants) and `Message` (list shows conversation, sender, and timestamp; search on text and sender email), in the style of `ideas/admin.py`.
- **`__str__`**: `Conversation` returns something like "Conversation 3"; `Message` returns something like "Message from <sender> in <conversation>", so admin lists are readable.

## Risks / Trade-offs

- [The many-to-many relation cannot enforce two participants or unique pairs at database level] → T67 creates conversations through a single code path that checks for an existing conversation between the two users and adds exactly two participants. This is recorded as a T67 requirement.
- [Direct ORM `save()` can store empty text] → T67 validates messages with a form or `full_clean()` before saving. No database check constraint is added, which matches the existing `Feedback` and `Reply` models.
- [Messages created in the same instant would have no defined order] → The `id` tie-breaker in the ordering makes the order deterministic. Tests set distinct timestamps explicitly instead of relying on clock resolution.

## Migration Plan

Add `chat` to `INSTALLED_APPS` and generate `chat/migrations/0001_initial.py` (conversation, participants join table, message). It depends only on the user model's migration. Apply it with the usual `python manage.py migrate`, including on Render's PostgreSQL during deployment. Rollback is `python manage.py migrate chat zero`, which drops the new tables. No data exists yet.
