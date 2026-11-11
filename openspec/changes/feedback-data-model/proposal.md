# Proposal

## Why

T22 (#54) requests a `Feedback` data model with an idea, author, text, and submission timestamp. US005 (#43) depends on saved feedback being associated with its idea and identifiable by its author, so the existing `ideas` app needs a persistent model foundation before the later submission and display work.

## What Changes

- Add a `Feedback` model in the existing `ideas` app, related to `Idea` and the configured user model, with required text and an automatically recorded submission timestamp.
- Add the model migration and focused tests for its relationships, stored text, timestamp, and non-empty model validation.
- Register `Feedback` in Django admin consistently with the existing idea models.

This change covers the data-model portion of US005 only. It does not implement a submission form or endpoint, user-facing empty-feedback error handling, display with an idea, or authorization behavior. Private feedback, replies, notifications, and other UI work are also out of scope.

Refs #54; associated user story US005 (#43).

## Capabilities

### New Capabilities

None. Feedback belongs to the existing ideas capability.

### Modified Capabilities

- `ideas`: add the feedback-record data required by US005, without specifying submission or display flows.

## Impact

- `ideas/models.py`: define the `Feedback` relationships and fields.
- `ideas/migrations/`: add the schema migration.
- `ideas/tests.py`: add focused model tests.
- `ideas/admin.py`: register the model for administration.
- No new app, runtime dependency, route, template, or project configuration change.
