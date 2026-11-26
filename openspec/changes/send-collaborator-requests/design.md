# Design

## Context

See `proposal.md` for scope and issue references. T60–T61 already provides `CollaboratorRequest` with Pending/Accepted/Rejected statuses, a unique `(idea, receiver)` constraint, and participant validation. It does not override `save()` to call validation. Every stored `Idea` is published; there is no draft flag to filter.

At the start of this stage, `accounts.student_discovery` admitted only investors, and its template linked to the investor-only profile view. The shared profile template distinguished owner and investor actions. `_profile_display_context` in `accounts/views.py` loaded saved profile data and supported students without a completed profile. Investor views create `ProfileVisit` records; student views must not do so.

The existing `Notification` model requires a feedback record. Reusing it for collaborator invitations would require a separate notification-model change not requested by these tasks.

## Goals / Non-Goals

**Goals:** A browser path from the student directory to project selection and an authorized, duplicate-safe request write, reusing the committed models and existing profile presentation.

**Non-Goals:** No request-management state transitions or recipient inbox in this stage. No schema changes, new user roles, or edit access to other students' profiles.

## Decisions

### 1. Extend discovery and add a distinct student profile route

Let both signed-in students and investors use `accounts:student_discovery`. Retain its existing skill filter, active-student saved-profile query, and invalid-filter handling. For student viewers, exclude their own account from the results and link cards to the collaboration-profile route; investor cards retain their existing links. Show the Students navigation entry to both roles.

Add `GET /accounts/students/<student_id>/collaborate/` as `accounts:collaborator_profile`, restricted to signed-in students. Resolve an active student target, redirect self-visits to `accounts:my_profile`, and reuse the shared profile template and display fields. A target without a saved profile uses the existing incomplete-profile message.

Keep the investor profile URL investor-only so it continues to own Follow/Unfollow and investor-visit tracking. Adding a student-specific view avoids recording student visits as investor activity. This extends the old directory access assumption intentionally: replace its student-403 test with student-access coverage, while retaining the investor-profile and following permission tests.

The existing unarchived discovery/profile specifications describe investor use; this stage adds the student collaboration path without changing those investor scenarios. The `ideas` capability owns the new US0027 invitation requirements, consistent with the model-stage change.

### 2. Scope the selector to the current owner

Add `CollaboratorRequestForm` in `ideas/forms.py` with one required `ModelChoiceField` named `idea`. Initialize its queryset from the authenticated student's `Idea` rows, using an explicit stable ordering and the existing Bootstrap select styling. Use the complete owner-scoped list; an already-invited project stays selectable and receives a clear duplicate error on submission, rather than disappearing from the list.

The target profile fixes the receiver. There are no editable sender, receiver, or status fields. Students without ideas see a publish-first prompt rather than a usable submit button. A role check on the endpoint remains necessary even though the form scopes the queryset.

### 3. Share profile presentation without imports between view modules

Move `_profile_display_context` to `accounts/profile_display.py` as a reusable display-context function and update the existing owner/investor callers. Add a collaboration-context function there that accepts an optional bound request form, marks the profile as another student's, and supplies whether the sender owns any ideas.

Both the student-profile GET and the request POST view use this helper. It imports profile data/presentation helpers and the request form, not either app's views. This avoids circular imports and avoids duplicating portfolio/experience formatting on error responses. Existing owner/investor rendering tests protect the small extraction.

### 4. Use a protected POST with explicit validation and atomic duplicate handling

Add `POST /students/<student_id>/collaborator-requests/` as `ideas:send_collaborator_request`. Require login and a student role, resolve an active student receiver, and reject self-invitations. Retain normal Django CSRF protection and reject non-POST methods without writes.

Bind the form with the current user's project queryset. After it validates, construct a Pending candidate from the cleaned idea, `request.user`, and the URL's receiver; call `full_clean()` before creation. Map validation errors into readable form errors, including an explanatory duplicate error when that pair already exists.

Create through `get_or_create(idea=idea, receiver=receiver, defaults={"sender": request.user, "status": Pending})`. The existing database uniqueness constraint is the final arbiter if another submission wins after validation. Handle `created=False` as an existing request, preserving status and timestamp. Do not use `update_or_create` or reset an existing request to Pending. Do not mask unrelated database errors as duplicates.

On success, show a success message and redirect to the collaboration profile. On validation or duplicate failure, render the same profile with the bound form and its error messages; retain a valid selection. Use standard invalid-form HTTP 200 responses, permission errors for forbidden actors, and not-found responses for unavailable targets. Submitted identity/status fields are ignored.

### 5. Treat receiver persistence separately from management UI

The created row must appear in the receiver's `received_collaborator_requests` relationship with the correct sender and idea. It must not create a membership or a feedback notification. T64–T65 will display and process received rows; until that stage is implemented, this stage's tests establish the recipient-addressed persistence portion of the Send request criterion, not end-to-end inbox acceptance.

## Risks / Trade-offs

- UI visibility alone cannot enforce ownership → Validate the authenticated role, owner-scoped form selection, receiver, and model before writing; cover tampered POSTs.
- A validation-time duplicate check can race → Retain the database constraint and use atomic `get_or_create` lookup fields matching that constraint. Test duplicate endpoint submissions for all statuses and the concurrent-winner outcome; retain the existing direct-database constraint tests.
- Broadening directory access changes a previous test expectation → Document the US0027 reason and add student-directory tests while retaining investor and follow regressions.
- Receiver management is a later stage → Keep the receipt limitation explicit in docs and final acceptance notes; do not claim the whole story complete.
- Two unrelated legacy OpenSpec changes currently fail validation → Report them separately and verify this change strictly; avoid mixing their repairs into this stage.

## Migration Plan

No new migration is expected. Verify `makemigrations --check --dry-run` stays clean. Deploy after applying the existing `0007_add_collaborator_models` migration if it has not already been applied. Rolling back these view/template changes does not require deleting saved invitations.

## Planning Validation

At proposal completion, only planning artifacts had been added and implementation tasks remained unchecked. `openspec validate send-collaborator-requests --strict` passed. Repository-wide validation reported 18 passed and the same 2 pre-existing failures in `prepare-sprint2-experiments` and `seed-demo-ideas`, both missing a no-spec-change declaration. No implementation code was changed or Django tests rerun during proposal creation.

## Implementation Progress

`CollaboratorRequestForm` now accepts a required keyword-only `owner` argument and exposes only the required `idea` field. Its queryset starts empty and includes the saved authenticated student owner's ideas ordered by title and primary key. Anonymous users, investors, and students without projects have no valid selections. Extra submitted ownership fields cannot change this scope. The form validates a selection without saving any invitation or membership.

`.venv/bin/python manage.py test ideas.tests.CollaboratorRequestFormTests ideas.tests.IdeaFormTests` passes all 13 tests: 8 new invitation-form tests and 5 existing idea-form tests. The new tests cover valid selection, owner-scoped choices, required/invalid/nonexistent/foreign IDs, tampered ownership data, and accounts without eligible projects. The user also ran the 8 new form tests successfully.

The shared display helper now lives in `accounts/profile_display.py`, with existing owner/investor callers updated and collaboration context retaining an optional bound form. Students can access the existing directory and its skill filter, with their own card excluded, and follow student-specific links to `accounts:collaborator_profile`. Students navigation is visible to both authenticated roles. The new profile route is read-only, requires a student viewer and an active student target, redirects self-visits to the existing owner view, and supports incomplete profiles. It records no investor visits. Its context supplies the owner-scoped invitation form to the shared template.

The old directory student-403 expectation and investor-only navigation expectation were intentionally replaced for US0027. New directory tests cover self-exclusion, filtered/invalid results, and the project-owner directory-to-profile path. All 9 `accounts.tests.CollaboratorProfileAccessTests` pass, including permissions, read-only behavior, no writes/visits on browsing, and bound-form preservation. The combined relevant test run passes 81 tests across that class, `accounts.test_discovery`, `StudentProfilePresentationTests`, `StudentProfileWorkflowTests`, `FollowActionTests`, `FollowProfilePresentationTests`, `ReadableProfileEntryTests`, and `ProfileVisitStatisticsTests`. Existing investor-only profile/follow permissions and profile data ownership remain covered.

The user also ran the 9 collaboration-profile access tests successfully.

The `ideas:send_collaborator_request` POST endpoint is implemented at `/students/<student_id>/collaborator-requests/`. It requires an authenticated student, resolves an active student receiver from the URL, rejects self-invitations, and validates an owner-scoped project selection and the candidate model. Authenticated non-POST submissions return 405, forbidden participants return 403, and unavailable receivers return 404. Invalid selections and model errors return the profile with the bound form and HTTP 200. The authenticated sender, URL receiver, and Pending status override any extra submitted identity/status fields.

Successful creation uses the database-constrained `get_or_create` pair and redirects with `Your collaborator request has been sent.`. Both validation-time duplicates and an existing-row result at creation add `You have already sent a collaborator request to this student for this project.` to the bound form without changing the original status or creation timestamp. Unrelated database errors are not caught and relabelled as duplicates. The receiver relationship exposes the saved row; memberships and feedback notifications are not created.

`.venv/bin/python manage.py test ideas.tests.SendCollaboratorRequestTests ideas.tests.CollaboratorRequestFormTests accounts.tests.CollaboratorProfileAccessTests` passes all 35 tests, including 18 new endpoint tests. Coverage includes role/ownership restrictions, receiver validation, invalid project input, ignored identity/status overrides, actual missing/valid CSRF-token behavior, persistence and success feedback, duplicate preservation in all three statuses, independent pairs, and model-validation error handling. The concurrent-winner test simulates `get_or_create` returning an existing request after validation; it is a controlled race-outcome regression, not a real simultaneous-request test. Existing model tests separately cover the actual database uniqueness constraint.

The user also ran all 18 endpoint tests successfully.

The profile template now renders the invitation section, an explicitly labelled project selector, help text, CSRF token, and Request Collaborator submit button. Field errors render with the selector's generated error ID/ARIA references, and non-field errors render as alerts. Like the existing profile editor, the form uses `novalidate` so empty-selection submissions receive the consistent server validation message. Students without projects see a publish-first prompt and link without a request submission form. Invitation controls are absent from owner/investor views and remain available on an incomplete target profile.

All 7 `accounts.tests.CollaboratorProfilePresentationTests` and 4 `ideas.tests.CollaboratorRequestWorkflowTests` pass. The latter use a CSRF-enforcing Django client and submit the action/token extracted from the actual rendered invitation form. They cover directory-to-profile submission, receiver-addressed Pending persistence, success redirect, correction of an empty selection, duplicate feedback with selection/status/timestamp preservation, and rejection of a foreign project. These are automated HTTP/template checks, not a manual browser or narrow-viewport check.

The combined test run passes 53 tests across those two new classes, `CollaboratorProfileAccessTests`, `SendCollaboratorRequestTests`, `StudentProfilePresentationTests`, and `FollowProfilePresentationTests`. The user also ran all 11 new presentation/workflow tests successfully. Manual browser verification remains pending; recipient inbox/management remains the following stage.

## Integration Verification and Definition of Done

- `.venv/bin/python manage.py test` passes all 301 tests in 19.392 seconds.
- `.venv/bin/python manage.py check` reports no issues, and `makemigrations --check --dry-run` reports no changes. No model or migration file changed in this stage.
- `openspec validate send-collaborator-requests --strict` passes. Repository-wide validation remains 18 passed and 2 failed, with the same pre-existing `prepare-sprint2-experiments` and `seed-demo-ideas` metadata problems recorded above.
- `git diff --check` passes; changed paths are limited to this stage's forms, views, URL configuration, shared profile rendering, navigation/templates, tests, and planning artifacts.

The README Definition of Done was reviewed. Automated tests cover project-owner selection, authorized request persistence addressed to the chosen receiver, and duplicate prevention. The sending-stage manual browser/narrow-viewport checks have now been completed as documented below. The subsequent `manage-collaborator-requests` change implements and verifies the recipient-facing workflow separately. Integrated MVP verification, applicable wireframe checks, team review, and Product Owner acceptance remain pending. These integration checkmarks do not declare the complete story Definition of Done satisfied.

## Manual Browser Observations

The user's later desktop screenshot confirms the missing-selection check: submitting with the project selector still showing `Select a project` renders the inline error `Please select one of your published projects.` and highlights the selector, while retaining the target student's profile and the send form. This is visual confirmation of server-side required-field feedback; absence of a saved invitation for this invalid submission is established by the automated tests rather than by the screenshot.

The user's desktop screenshots confirm that a signed-in student can open another student's collaboration profile and see its saved profile information. Before owning a project, the invitation section displayed the publish-first prompt and Publish an idea link, with no project selector or request submit button. After publishing a project, the owner saw that project in the selector and the Request Collaborator button. A later screenshot shows the success confirmation `Your collaborator request has been sent.` and the profile displayed after submission. A subsequent duplicate-submission screenshot shows the expected already-sent error while keeping the selected project.

Two subsequent Chrome responsive-mode screenshots at 400×609 confirm the narrow-viewport sending flow. The first shows the project selector opened with the available choices, the required-selection error, a fully visible submit button, and the collapsed navigation. The second shows `Your collaborator request has been sent.` after returning to the selected student's profile, with the form fitting the viewport. Together with the earlier desktop observations and required-selection screenshot, this completes the remaining manual sending-form presentation and submission checks for task 4.2. Browser device emulation is not a physical-phone or deployed-MVP acceptance test.

### Local development database compatibility

Manual creation of another student profile exposed a local `NOT NULL constraint failed: accounts_studentprofile.github_url` error. Inspection confirmed that this shared development database had applied the separate T77 migration `accounts.0009_add_profile_social_urls`, while the current branch's models/migration files did not contain those fields. All four legacy URL columns were non-nullable without database defaults, so new profile inserts from this branch omitted required database values. Fresh migration-based test databases did not have this mismatch.

The development database was backed up to the Git-ignored `local-backups/profile-defaults-20261124T184506064466Z/db.sqlite3`. A compatibility repair was first validated on a copy and then applied locally: preserve all columns, existing URL values, constraints, indexes, triggers, and sequence values while adding empty-string database defaults to the four legacy URL columns. Snapshots of every existing application table and sequence matched before and after. A rollback-only profile creation with the current Django model succeeded on both the copy and the repaired database. Foreign-key and integrity checks passed. No model or migration source files were changed for this local environment repair. The user still needs to retry the profile editor in the browser; this does not complete the remaining manual acceptance checks.
