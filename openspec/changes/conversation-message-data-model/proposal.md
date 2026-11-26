# Proposal

## Why

T66 (#119) asks for the `Conversation` and `Message` data models (id, conversation_id, sender_id, text, timestamp). US029 Chat (#100) needs saved messages tied to a conversation and a sender and shown in chronological order. The backend logic (T67) and the chat interface (T68) can only be built once these records exist.

## What Changes

- Add a new Django app `chat` to the existing project and register it in `INSTALLED_APPS`. It is a module of the same Django site (same server, database, authentication and base template), not a separate service.
- Add a `Conversation` model that records the users taking part in it and when it was created.
- Add a `Message` model that belongs to a conversation and stores its sender, its required text and an automatically recorded timestamp. By default, messages are returned in chronological order.
- Add the initial `chat` migration, register both models in Django admin, and add focused model tests.

Out of scope:
- Creating conversations, sending messages, retrieving message history, and preventing duplicate conversations between the same two users. These belong to T67 (#120).
- The chat interface (conversation list and message thread) and the user-facing "please enter text" prompt for empty messages. These belong to T68 (#121).
- Who may chat with whom, read receipts, notifications, attachments, and real-time delivery.

Refs #119; associated user story US029 (#100).

## Capabilities

### New Capabilities

- `chat`: conversations between users and the messages exchanged in them. This change adds only the stored-record requirements; T67 and T68 will extend the same capability with sending, history, and display behavior.

### Modified Capabilities

None.

## Impact

- New `chat/` app: `apps.py`, `models.py`, `admin.py`, `tests.py`, `migrations/0001_initial.py`.
- `config/settings.py`: add `"chat"` to `INSTALLED_APPS`.
- New database tables for conversations, their participants, and messages. There is no existing data to migrate.
- No new route, template, view, or runtime dependency.
