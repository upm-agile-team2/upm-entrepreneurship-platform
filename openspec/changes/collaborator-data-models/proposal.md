# Proposal

## Why

US0027 (#98) requires students to invite other students to help develop their published ideas. T60 (#113) and T61 (#114) provide the persistent membership and request records needed before the sending and management workflows can be built.

Refs #113, #114, #98.

### Delivery plan

Develop T60–T65 on the shared branch `T60-T65-collaborator-requests` and deliver them in one pull request to `main`. Keep three implementation stages with separate commits and verification: T60–T61 models, T62–T63 sending, then T64–T65 management. This OpenSpec change covers the first stage; plan the remaining stages against their complete task and user-story requirements before implementing them. No intermediate merge is required.

## What Changes

- Add a `Collaborator` model containing an ID, idea, collaborator user, and creation timestamp.
- Add a `CollaboratorRequest` model containing an ID, idea, sender, receiver, status, and creation timestamp. Statuses are Pending, Accepted, and Rejected, with Pending as the default.
- Expose the project-to-collaborator relationship through the membership model, with one membership per idea and student.
- Validate that the sender is the idea's student owner and the receiver is another student. A membership identifies another student collaborating on the idea.
- Prevent duplicate requests for the same idea and receiver using a database constraint. As agreed with the user, this applies regardless of status, including rejected requests; a different idea can have a separate request.
- Add an additive database migration and Django tests for persistence, relationships, validation, and duplicate prevention.

### Out of scope

Later stages on the same branch will implement selecting a student and sending a request (T62–T63), followed by request management and its UI (T64–T65). This model-stage change adds no views, forms, profile permissions, notifications, acceptance/rejection actions, automatic membership creation, or chat functionality. It does not complete all acceptance criteria or the Definition of Done of US0027 by itself.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: Add project membership and collaborator-request persistence contracts supporting US0027, including duplicate prevention.

## Impact

- `ideas/models.py`: two models and the explicit project-to-student membership relationship; existing `accounts.User` accounts are reused.
- `ideas/migrations/0007_add_collaborator_models.py`: an additive migration from `0006_notification`.
- `ideas/tests.py`: model-level tests; `ideas/test_collaborator_models_migration.py`: an upgrade check preserving existing users and ideas.
- No new dependencies, endpoints, or visible interface changes.
- The separate T69–T70 branch also adds an `ideas` migration. Its eventual integration may require a migration merge; this change does not depend on that unmerged branch.
- The final T60–T65 PR should include closing references for the completed tasks. This model stage contributes `Closes #113`, `Closes #114`, and `Refs #98`; confirm the remaining issue references when planning the later stages, and do not close the parent story before all its acceptance criteria are verified.
