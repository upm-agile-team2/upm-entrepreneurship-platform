# Proposal

## Why

T66 (#119) provides the conversation and message records, but users still need a backend workflow to open conversations and exchange messages, plus a screen to access that workflow. This change covers the follow-up work in T67 (#120) and T68 (#121) for US029 Chat (#100).

## What Changes

- Add backend behavior to find or create a conversation for a participant pair, send validated messages, and retrieve a user's conversations and message history.
- Add an authenticated chat interface that lists conversations, displays a conversation thread, and lets participants send messages with clear validation feedback.
- Restrict conversation and message access to their participants.

Out of scope: changing the T66 data model, defining which user roles may initiate contact, read receipts, notifications, attachments, and real-time delivery.

## Capabilities

### New Capabilities

- `chat`: extend the conversation and message capability introduced by T66 with participant-scoped conversation access, message sending, and the chat interface.

### Modified Capabilities

None.

## Impact

- `chat/`: add conversation and message workflow, forms, views, URLs, and tests on top of the models from T66.
- `config/urls.py` and `templates/`: expose and render the chat experience using the existing authenticated Django site and Bootstrap base template.
- No new models or migration are expected; T67/T68 depend on T66 (#119) being integrated first.
