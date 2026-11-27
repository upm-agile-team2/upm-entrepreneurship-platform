# Tasks

## 1. T67 — Chat backend (#120)

- [x] 1.1 Add a service that creates a conversation with exactly two active participants or returns the existing conversation for that pair; test new creation, participant count, repeat requests, and reversed participant order.
- [x] 1.2 Add authenticated endpoints to start and list conversations, scoped to the current user; test anonymous redirects, role-neutral access, self-conversation rejection, inactive/nonexistent recipients, and that users cannot list another user's conversations.
- [x] 1.3 Add a message form and thread endpoint that save non-empty messages with the current participant as sender; test valid persistence, whitespace and empty validation, and no message creation on invalid input.
- [x] 1.4 Enforce participant-only thread access for both reads and writes; test a non-participant cannot view a thread or submit a message and receives a non-disclosing response.

## 2. T68 — Chat interface (#121)

- [x] 2.1 Add authenticated chat navigation and a conversation list with a start-conversation control; test links, participant-scoped results, target selection, and the empty-list state for students and investors.
- [x] 2.2 Add a conversation thread showing messages oldest first with sender and timestamp, plus a compose form; test rendered history, sender identity, valid submission, and redirect back to the thread.
- [x] 2.3 Render accessible field errors for empty or whitespace-only messages without losing the thread context; test the prompt and verify invalid submissions do not create messages.

## 3. Integration verification

- [x] 3.1 Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `python manage.py test`; verify the complete suite passes and review the README Definition of Done for US029.

## Workflow follow-up

- Open PRs with `Closes #120` and `Closes #121` after T66 (#119) is integrated; have another team member review before merge.
