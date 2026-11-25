# Tasks

## 1. Chat app setup

- [x] 1.1 Create the `chat` app (`chat/__init__.py`, `chat/apps.py` with `ChatConfig` using `BigAutoField`, empty `chat/migrations/__init__.py`) and add `"chat"` to `INSTALLED_APPS` in `config/settings.py`; verify with `python manage.py check`.

## 2. Conversation and Message models and admin

- [x] 2.1 Add `Conversation` to `chat/models.py` with a `participants` many-to-many field to `settings.AUTH_USER_MODEL` (`related_name="conversations"`), an automatically populated `created_at`, ordering `["-created_at"]`, and a readable `__str__`, following the design.
- [x] 2.2 Add `Message` to `chat/models.py` with a `conversation` foreign key (`CASCADE`, `related_name="messages"`), a nullable `sender` foreign key to `settings.AUTH_USER_MODEL` (`SET_NULL`, `related_name="sent_messages"`), required `text` (`blank=False`), an automatically populated `timestamp`, ordering `["timestamp", "id"]`, and a readable `__str__`.
- [x] 2.3 Generate `chat/migrations/0001_initial.py` with `python manage.py makemigrations chat` and verify that `python manage.py makemigrations --check --dry-run` reports no changes.
- [x] 2.4 Register `Conversation` and `Message` in `chat/admin.py` as described in the design and verify with `python manage.py check`.

## 3. Model tests

- [x] 3.1 In `chat/tests.py`, add a test that creates a conversation between a student and an investor, creates a non-empty message from one of them, refreshes it from the database, and verifies its conversation, sender, text, and a timestamp set at creation; run `python manage.py test chat`. This covers the persistence part of US029 (#100) "Send message"; showing the message in the conversation is tested in T68.
- [x] 3.2 Add a test that deletes the sender's account and verifies the message is still in the conversation with `sender` set to `None`; run the focused test.
- [x] 3.3 Add a model-validation test showing that a `Message` with empty text fails `full_clean()` with an error on `text`; run the focused test. This is the model base for US029 "Validate message"; the user-facing prompt is tested in T68.
- [x] 3.4 Add a test that creates several messages in a conversation, sets distinct timestamps explicitly with `Message.objects.filter(pk=...).update(timestamp=...)`, and verifies that `conversation.messages.all()` returns them oldest first with their senders; run the focused test. This covers the ordering part of US029 "Display messages".

## 4. Integration verification

- [x] 4.1 Run `python manage.py makemigrations --check --dry-run` and `python manage.py test`; confirm the new chat tests and the existing suite pass. Review the README Definition of Done for T66 and keep US029 (#100) open until T67 and T68 are complete.

## Workflow follow-up

- Push the work to branch `T66-conversation-message-model` and mark draft PR #140 (which closes #119) as ready for review by another team member.
- Archive the change with `/opsx:archive` after the PR is reviewed and merged.
