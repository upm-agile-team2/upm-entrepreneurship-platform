# Design

## Context

See `proposal.md` for motivation and scope. `ideas.Idea` already has an owner and a publication timestamp; it has no draft state. `accounts.User` already distinguishes students and investors. Before this change, the branch had no collaboration models. Existing relationships use `settings.AUTH_USER_MODEL`, and `Follow` provides a nearby example of model validation plus database constraints.

The `ideas` migration leaf before this change was `0006_notification`; this change adds `0007_add_collaborator_models`. SQLite is used locally and PostgreSQL in deployment. The separate project-stage/support branch is not a dependency.

T60–T65 share the branch `T60-T65-collaborator-requests` and one final pull request. This design covers the first, model-only stage. Later stages reuse its models without waiting for an intermediate merge, with separate commits, verification, and planning artifacts based on their complete requirements.

## Goals / Non-Goals

**Goals:** Provide reusable membership and request records, stable ORM relationships, and database protection against duplicate rows, so later workflows can build on the same contract.

**Non-Goals:** No state-transition service or UI. No signals that turn requests into memberships. No automatic changes to existing project ownership or profile-view permissions.

## Decisions

### 1. Keep both models in the ideas app

Collaboration is scoped to an existing idea. Reuse `Idea` and `settings.AUTH_USER_MODEL` rather than creating another app or another type of student account.

| Model | Fields |
| --- | --- |
| `Collaborator` | Default primary key; `idea` foreign key; `collaborator` user foreign key; `timestamp` with `auto_now_add=True` |
| `CollaboratorRequest` | Default primary key; `idea`, `sender`, and `receiver` foreign keys; `status`; `timestamp` with `auto_now_add=True` |

Foreign keys use `CASCADE`, consistent with project-scoped records: deleting the idea or a referenced user removes its dependent rows. This is not an audit-history feature. Timestamps record creation, not last modification.

### 2. Use the membership as the explicit join table

Add `Idea.collaborators` as a `ManyToManyField` to users with `through="Collaborator"`, explicit `through_fields=("idea", "collaborator")`, `blank=True`, and reverse name `collaborating_ideas`. The membership's foreign-key reverse names are `collaborator_memberships` on the idea and `idea_collaborations` on the user.

Add a unique constraint on `(idea, collaborator)`. An implicit many-to-many join table would duplicate the T60 model and lose its timestamp; storing a user list in JSON would weaken referential integrity.

The request's reverse names are `collaborator_requests` on the idea, `sent_collaborator_requests` on the sender, and `received_collaborator_requests` on the receiver. Reading these relationships does not implement website delivery or an inbox.

### 3. Store a small status vocabulary without implementing transitions

Use `TextChoices` with `pending`, `accepted`, and `rejected`, displayed as Pending, Accepted, and Rejected. Store it in a `CharField(max_length=20)` defaulting to Pending. These are design choices for the otherwise unspecified task status field. Validate choices and add a database check restricting stored values to this vocabulary.

This change only stores status values. Later request-management work must decide and enforce authorized transitions and create the membership on acceptance. Saving a request, even with Accepted status, has no membership side effect at this stage.

### 4. Enforce duplicates at the database boundary

Use an unconditional unique constraint on `(idea, receiver)`. The sender is omitted because valid requests must come from that idea's owner. This protects concurrent inserts and ordinary saves even when model validation is bypassed.

The user agreed that rejected invitations cannot be resent for the same project. A pending-only constraint would permit that, so it does not match the chosen rule. Later endpoints must also avoid resetting an old request to Pending as a resend; the current constraint prevents duplicate rows rather than enforcing transitions or preserving history after deletion.

### 5. Separate cross-record validation from database constraints

`CollaboratorRequest.clean()` checks that the sender is a student, owns the idea, and differs from the student receiver. `Collaborator.clean()` checks that the collaborator is a student other than the idea owner. Add a database check against requests with identical sender and receiver IDs.

Callers use `full_clean()` before saving to run field, model, uniqueness, and constraint validation. Do not override `save()` globally. Role and ownership checks span tables and are model-level checks, not database guarantees; future views/services must validate explicitly and enforce authenticated ownership. The many-to-many manager is a query convenience, not an authorization boundary, and its writes must not be treated as validated business operations.

Handle missing or nonexistent foreign keys without raising an uncaught related-object exception during validation. Aggregate errors on relevant fields so later forms/services can report them.

## Risks / Trade-offs

- Role/ownership changes can invalidate existing relationships → Revalidate before later actions; changing account roles or project ownership is outside this scope.
- Permanent duplicate prevention is deliberately strict → A resend policy would need an explicit later requirement change. It provides no general rate limit across projects.
- T69–T70 also adds an `ideas` migration → Inspect the graph after either branch merges and add a migration merge if necessary; do not depend on an unmerged migration here.
- Model tests cannot demonstrate selecting, sending, or receiving invitations in the browser → Record model-level coverage now and leave the remaining US0027 acceptance work to T62–T65.

## Migration Plan

1. Generate an additive migration from `0006_notification` creating both tables, their constraints, and the explicit many-to-many relationship. Use Django's swappable user dependency.
2. Test upgrading a database containing an existing user and idea: their original fields remain unchanged and the new collaboration relations are empty.
3. Apply with `python manage.py migrate`, check for migration drift, and run focused and full Django tests.
4. If rollback is required before later workflows depend on these tables, reverse this migration only after reviewing/backing up any collaboration data. Reversal drops the new tables and their records, while preserving the original idea/user tables.

## Planning Validation

The proposal originally contained planning artifacts only. Repository-wide validation identified two pre-existing changes without specification deltas: `prepare-sprint2-experiments` and `seed-demo-ideas`. Their compatibility metadata is outside this change's scope; report them separately from validation of this change.

## Implementation Progress

The two models, their relationship, and validation/constraint declarations have been added to `ideas/models.py`. `.venv/bin/python manage.py check` reports no issues, and `git diff --check` passes.

The user generated and successfully applied `0007_add_collaborator_models`. Its operations have been inspected: they add the intended tables, through relationship, and constraints, with no changes to existing idea fields. `.venv/bin/python manage.py makemigrations --check --dry-run` reports no changes.

All 9 tests in `ideas.tests.CollaboratorModelTests` pass, covering persistence, relationship queries, duplicate membership rejection at validation/database boundaries, invalid roles/owner membership, missing/nonexistent foreign keys, and independent memberships for different pairs. The user also ran these 9 tests successfully.

All 17 tests in `ideas.tests.CollaboratorRequestModelTests` pass, covering request persistence/defaults and reverse queries; supported/unsupported statuses; participant roles, ownership, and self-invitations; missing/nonexistent foreign keys; duplicate prevention for all three existing statuses at validation/database boundaries; independent project/receiver pairs; and deletion cascades for requests and memberships. The user also ran these 17 tests successfully. Status persistence alone does not create a membership. The combined focused run passes all 26 tests.

The single test in `ideas.test_collaborator_models_migration` passes. It creates a user and a categorized idea under the `0006_notification` schema, upgrades to `0007_add_collaborator_models`, and compares their original fields, including the publication timestamp and category/owner references. The new collaboration relations and tables are empty. Other apps stay at their current schema, and cleanup restores the latest migration targets, including on failure. This uses Django's temporary test database. The user also ran this migration test successfully.

## Integration Verification and Definition of Done

- The user's `python manage.py test` run passed all 253 tests in 17.551 seconds. No production code has changed since that run.
- `python manage.py makemigrations --check --dry-run` reports `No changes detected`.
- `openspec validate collaborator-data-models --strict` passes.
- `openspec validate --all` reports 17 passed and 2 failed. The failures are the same pre-existing `prepare-sprint2-experiments` and `seed-demo-ideas` metadata issues recorded above, not regressions introduced by this change.
- `git diff --check` passes, and the reviewed implementation diff is limited to the collaboration models, their migration, tests, and this change's planning artifacts.

The T60–T61 model implementation and its automated verification are complete. The README Definition of Done was reviewed: US0027's website selection, sending, and receiving criteria still require later stages; code submission and another team member's review, integrated MVP checks, applicable wireframe checks, and Product Owner acceptance remain pending. These task checkmarks do not declare the parent story complete. Continue with T62–T63 on the same branch after reviewing its complete requirements; deliver the three stages together in the final T60–T65 PR.
