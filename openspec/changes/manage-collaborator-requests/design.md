# Design

## Context

See proposal.md for motivation. The existing models provide status/participant validation, unique idea/receiver requests, and unique idea/collaborator memberships. `ideas/views.py` only sends requests. The existing uncommitted T62–T63 changes provide student directory/profile access; preserve them. Feedback `Notification` rows require a feedback record and are not a suitable invitation inbox.

Original issues reviewed on 2026-11-24: US027 (#98), US028 (#99), T64 (#117), and T65 (#118). T64–T65 belong to US028, unlike the previous stage's shorthand association with US027. US028's three criteria are View pending requests, Accept request, and Decline request. The Sent tab is authorized by this conversation and is not attributed to an explicit GitHub acceptance criterion.

## Goals / Non-Goals

**Goals:** Complete the rendered student-to-student workflow using the existing schema, make both receipt and outcomes discoverable, and preserve authorization, terminal states, and atomic membership creation.

**Non-Goals:** No signals, generic notification-model changes, collaborator editing permission, or new schema. No invitation resend/cancel/removal. Do not alter other students' profile permissions or investor statistics.

## Decisions

### One scoped list view, three server-rendered tabs

Use GET `/collaborator-requests/` (`ideas:collaborator_requests`), defaulting to received Pending invitations. `?tab=sent` shows all invitations sent by the current student. Use explicit filters on the authenticated user and `select_related` for idea, sender, and receiver; order newest first with the primary key as tie-breaker. Unsupported tab values fall back to Received. A dedicated page keeps feedback notification semantics intact. Reuse Bootstrap and the existing detail-surface styles, with labelled navigation, semantic cards, dates, visible statuses, and responsive action groups. A student-only main-nav link exposes the page; link to Sent from the successful sending confirmation/profile section for immediate discovery.

Following the user's manual-test feedback, add `?tab=history` between Received and Sent. Filter it by the authenticated receiver and explicitly by Accepted/Rejected statuses. Reuse the received cards' creator/project/status information, render a history-specific introduction and empty state, and omit decision forms. Keep history read-only and retain the existing terminal-state protection on the POST endpoint. The user's explicit request extends the original pending-only inbox requirement; no schema change is needed, and existing handled rows immediately appear.

### One POST decision endpoint

Use POST `/collaborator-requests/<request_id>/respond/` (`ideas:respond_collaborator_request`) with an `action` value of `accept` or `decline`. Derive the receiver from the session and scope the lookup to that receiver. Anonymous visitors sign in; investors receive 403; missing/other-recipient IDs receive 404; non-POST requests receive 405; unsupported actions receive 400. Keep Django CSRF protection. Submitted sender, receiver, idea, or status fields do not control the operation.

### Conditional transition and atomic membership creation

Read/validate the invitation before starting the write transaction. Validate current model participants before processing a Pending request so changed ownership/roles cannot create an invalid membership. Inside `transaction.atomic`, update only a row still Pending and addressed to the current user. A successful accept uses membership `get_or_create` in the same transaction. A zero-row update means another action already handled the request; show informational feedback without changing membership. This conditional write preserves the first outcome without depending on `select_for_update`, which does not lock rows on SQLite. Unrelated database failures propagate and roll back both changes. Existing memberships are preserved; accepting does not duplicate them. Rejection never deletes a pre-existing membership.

### Visible membership, unchanged editing permissions

Display accepted collaborators by name on the idea detail page through the existing many-to-many relationship, with profile links only for signed-in student viewers. Reuse the relation in all detail render paths. Keep owner-only `can_edit` behavior unchanged.

### Focused acceptance and integrity tests

Add `ideas/test_collaborator_requests.py`. Test each US028 criterion plus privacy, sent statuses, empty states, auth/role/method/CSRF checks, invalid IDs/actions, participant tampering, stale eligibility, terminal replay, existing memberships, and rollback. Exercise the actual rendered forms using CSRF-enforcing clients through send → receiver inbox → accept/decline → sender Sent and idea membership. Simulate a competing decision that wins before the conditional update; do not describe that as a real parallel database test. Run the focused tests, the full Django suite, migration checks, OpenSpec validation, and whitespace checks. Use a local browser preview if available and record exactly what was observed.

## Risks / Trade-offs

- Concurrent decisions → A conditional Pending update and one transaction make only the winning action create membership; SQLite may reject contended writes with a database-lock error, but cannot commit a partial acceptance.
- Prior invalid/stale participant rows → Validate the pending record and show an error without changing it.
- Navigation is already wide → Let the existing navbar wrapping/mobile collapse handle the added link and verify a narrow viewport if browser tooling is available.
- Existing unrelated OpenSpec baseline failures → Record them separately from this change's strict validation; do not fix unrelated requirements silently.
- Wireframe/team/PO acceptance are external → Keep these Definition of Done items pending rather than treating automated tests as their replacement.

## Migration Plan

Run `python manage.py migrate` when deploying with the T62–T63 changes. The existing `0007_add_collaborator_models` migration supplies the collaboration schema. After synchronizing current main, `0008_merge_collaborators_and_project_stage` joins that migration with main's existing `0007_add_project_stage_support` through an empty operation list. It adds no fields or data transformations of its own. Main's accounts social-link migration is retained. Application rollback does not require deleting saved invitations or memberships.

## Implementation and Verification

### Request lists

`GET /collaborator-requests/` now renders the current student's Pending received invitations; `?tab=history` renders their Accepted/Rejected incoming invitations, and `?tab=sent` renders their sent invitations in every status. Query-string participant IDs cannot override user scoping. Cards include project descriptions, creator/recipient profile links, dates, and visible status labels; Received has CSRF-protected Accept/Decline forms, while History and Sent are read-only. The student navigation and the profile send section link to the lists. Other roles cannot enter the page.

The request-list tests cover these behaviors, empty states, stable ordering, HTML escaping, and read-only listing. Following the History addition, all 16 tests in `ideas.test_collaborator_requests.CollaboratorRequestListTests` pass. Decision processing is verified separately below.

### Decisions

`POST /collaborator-requests/<request_id>/respond/` now accepts `action=accept` or `action=decline`. Only the saved receiver can process a request; supplied participant/project/status values are ignored. Pending-only conditional updates and atomic membership creation preserve the first recorded outcome and roll back Accepted when membership creation fails. Stale model eligibility produces an explanatory error without changes; handled invitations produce informational feedback. Decline does not create or delete memberships.

`.venv/bin/python manage.py test ideas.test_collaborator_requests.CollaboratorRequestDecisionTests` passes all 17 tests, including authorization, method/CSRF checks, terminal replay, existing memberships, ownership/role changes, rollback, and a simulated competing decline before acceptance. The competition test is a controlled outcome test, not a real parallel database test.

### Membership and rendered workflow

Idea details now render collaborator names from the existing membership relation, prefetched in a stable name/ID order for the normal detail view. Student viewers can follow profile links; other viewers see names without student-only links. Owner-only editing rules remain unchanged.

`.venv/bin/python manage.py test ideas.test_collaborator_requests` passes all 39 focused tests: 16 list tests, 17 decision tests, 2 full rendered-form workflow tests, and 4 membership presentation/permission tests. The workflow tests use separate CSRF-enforcing sender/receiver clients and the actual form action/token from each rendered page. Both acceptance and decline are followed through to the receiver's History, the sender's status view, membership outcomes, and duplicate-send prevention.

A separate headless Chrome preview used a fresh temporary browser profile, temporary SQLite database, and fictional student accounts. Real send forms produced three invitations; the receiver's inbox displayed all three with idea/creator details. Real Accept and Decline buttons processed one each, and the sender's Sent page showed one Pending, one Rejected, and one Accepted. The accepted student's name appeared on idea details without an edit link. Screenshots at 1365×1100 and 390×844 were inspected, including the expanded mobile navigation and long unbroken title/description text; no horizontal page overflow was observed. Preview database, browser profile, and screenshots were kept outside the repository. This local browser verification does not establish production integration, agreed-wireframe review, or Product Owner acceptance.

### Integration checks and Definition of Done

- `.venv/bin/python manage.py check`: passes with no issues.
- `.venv/bin/python manage.py makemigrations --check --dry-run`: passes with no changes.
- `openspec validate manage-collaborator-requests --strict`: passes.
- `openspec validate --all`: all 24 items pass after synchronizing current main. The earlier pre-submission metadata cleanup passed 21 items; the initial baseline failed two items because their no-spec-change metadata was absent.
- `git diff --check`: passes.
- `.venv/bin/python manage.py test`: all 380 Django tests pass after the latest-main integration, including both upstream features and migration-branch preservation tests. The History-stage run previously passed 340 tests.

US028's View pending requests, Accept request, and Decline request criteria have automated HTTP/template coverage and local browser verification. US027's sent request can now be seen and processed by its receiver, and the sender can see its status. The README Definition of Done was reviewed: another team member's review, integrated/deployed MVP verification, comparison with the agreed UX wireframes, and Product Owner Sprint Review acceptance are still external follow-up. The implementation checklist does not claim these reviews or story acceptance have occurred.

### Receiver-history follow-up

The user requested retaining visible accepted/declined history after manually confirming that Decline removes the invitation from Received and shows Rejected in the sender's Sent page. History now shows existing handled records immediately, using only the current receiver and Accepted/Rejected status filters. It includes project/creator information and status badges, a dedicated empty state, and active navigation, with no decision forms. The original Pending-only Received behavior and terminal-state protections are retained.

Three new list tests verify history filtering/privacy/read-only behavior, empty state/active navigation, and discoverability. Existing auth/scoping and CSRF-rendered accept/decline workflow tests now cover History too. All 39 focused tests and all 340 Django tests pass. System checks, no-migration checks, strict change validation, and whitespace checks pass. At the History verification, repository-wide OpenSpec validation was 19 passed with the same two previously recorded unrelated failures; the pre-submission cleanup below resolves those metadata failures.

The isolated headless Chrome preview was reopened using the previous fictional records. The receiver saw the existing Rejected and Accepted invitations in History, with no action forms or pending invitations; the sender's receiver-history view was empty. Navigation between Received and History worked. Desktop (1365×1100) and mobile (390×844) screenshots were inspected, with no horizontal overflow. No production/user records were used for browser checks.

### Pre-submission metadata cleanup

The user's submission-readiness request prompted resolving the two existing OpenSpec validation failures. Both `prepare-sprint2-experiments` and `seed-demo-ideas` explicitly declare no capability/specification changes in their proposals. Added their missing `.openspec.yaml` files with `schema: spec-driven` and `skip_specs: true`, matching that documented scope and the existing metadata convention. No application code or behavior changed in this cleanup. `openspec validate --all` now passes all 21 items, and `git diff --check` passes. The latest application test run remains all 340 tests passing; metadata-only cleanup does not require another Django run.

### Latest-main integration and delivery preparation

Fetched current main (`2554f2f`) over HTTPS after the configured SSH remote failed authentication. Main includes social profile links and project development-stage/support fields, plus the same two OpenSpec metadata fixes. Resolved the profile-context extraction conflict by moving main's HTTP(S)-validated social-link presentation into `accounts/profile_display.py`, shared by owner, investor, collaboration GET, and invalid-send renders. Retained main's profile editor fields, project form/details, and the collaborator model validation imports.

Added `0008_merge_collaborators_and_project_stage` as an empty merge node depending on the two existing `ideas.0007` migrations. Two new migration tests upgrade from each sibling independently and preserve existing project fields, requests, and memberships. Three new HTTP/template regressions verify social links on collaboration GET/invalid POST, unsafe-link filtering, and coexistence of stage/support details with accepted collaborators. All seven focused integration/migration checks pass, and the full Django suite passes all 380 tests. System checks, migration consistency, all 24 OpenSpec items, and whitespace checks pass.

The isolated temporary preview database was upgraded and verified again in Chrome at desktop and mobile widths. Collaboration profiles retained social links and the invitation form; project details retained stage/support and collaborator names without granting edit access; existing History outcomes remained visible and read-only. Screenshots were inspected. The development database was backed up outside the repository, checked with SQLite `quick_check`, and its only pending migration (the empty merge node) was applied successfully; `migrate --check` passes.

Prepared a single T60–T65 PR description with closing references #113–#118 and story references #98/#99. Separate local commits preserve the sending, management, and metadata stages. Remote push and PR creation are not claimed complete: SSH returned `Permission denied (publickey)`, no HTTPS GitHub credential or API token was available, and no existing PR was found for this branch. GitHub authentication requires user action; no credentials were printed or added to the repository. External team/integrated/wireframe/PO acceptance remains pending.
