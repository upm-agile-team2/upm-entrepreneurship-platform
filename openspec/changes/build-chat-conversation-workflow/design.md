# Design

## Context

See proposal.md for motivation and specs/chat/spec.md for the behavior contract. PR #140 (T66, #119) adds the `chat` app with `Conversation.participants` and chronologically ordered `Message` records. The current integrated branch does not yet contain those models, so implementation depends on T66 being merged or otherwise present in the task branch. The site uses authenticated Django views, the existing custom User model, and server-rendered Bootstrap templates.

## Goals / Non-Goals

**Goals:**
- Provide a single server-rendered workflow for starting conversations, listing a user's conversations, viewing history, and sending messages.
- Keep conversation and message access scoped to their participants.
- Use the T66 models without changing their schema.

**Non-Goals:**
- Decide role-based contact eligibility; T66 leaves that policy outside its scope.
- Add real-time delivery, notifications, read status, attachments, or user message editing/deletion.

## Decisions

- **Put chat routes, forms, views, and templates in the `chat` app.** Include its URL configuration from `config/urls.py`, and add a Chat navigation link for signed-in users. This keeps chat behavior beside its models instead of adding it to `ideas` or `accounts`.
- **Offer a start-conversation control in the chat area.** It selects another active account and excludes the current user. No role filter is added, preserving the role-neutral scope established by T66. Creating or selecting a pair resolves to the same conversation.
- **Centralize pair lookup/creation in one service.** Within a transaction, lock the two user rows in stable primary-key order, search for a conversation with exactly those two participants, and create one with both participants only when no match exists. This serializes competing starts on the production database without adding another model migration. Keep the check in one path so views cannot create malformed or duplicate conversations.
- **Scope every list and detail query to `request.user`.** Conversation details are loaded through the participant relation; return 404 for non-participants so the endpoint does not reveal whether another user's conversation exists. Require authentication on all chat endpoints.
- **Use a ModelForm or form with stripped required text for sending.** Invalid or whitespace-only submissions render the thread with a field error and do not create a message. Valid submissions save the message with the current user as sender, then redirect to the thread. T66's model ordering supplies stable chronological history.
- **Use server-rendered pages.** The conversation list and thread extend `base.html`; a selected thread shows sender name, timestamp, text, and a compose form. Use normal escaping for user-provided message text.

## Risks / Trade-offs

- [The T66 many-to-many schema has no database constraint for exactly two participants or unique participant pairs] → All creation goes through the transactional service, uses stable user-row locks on PostgreSQL, and has duplicate-start and participant-count tests. SQLite does not enforce `select_for_update`; its test coverage verifies sequential behavior.
- [A role-neutral recipient selector permits either account role to contact any active account] → This follows T66's stated non-goal of choosing chat eligibility here; a later product decision can add a policy without changing message storage.
- [Older conversations may contain malformed participant sets created outside the service] → Pair matching verifies the full participant count and exact pair before reuse; unrelated or malformed conversations are not returned as a match.

## Migration Plan

No schema migration is planned. Deploy after T66's `chat` migration is present. Rollback removes the chat routes, views, forms, templates, and navigation link while keeping the T66 models and data intact.
