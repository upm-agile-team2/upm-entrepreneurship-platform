# Tasks

T62 (#115) and T63 (#116), US0027 (#98). Continue on the existing T60–T65 branch. These tasks cover Select collaborator, request persistence addressed to the receiver, and Prevent duplicate requests. Recipient inbox display and request management remain the following T64–T65 stage.

## 1. Owner-scoped project selection

- [x] 1.1 Add `CollaboratorRequestForm` with a required owner-scoped idea selector and Bootstrap styling; add and pass `ideas.tests.CollaboratorRequestFormTests` for valid selection, only the current owner's projects, missing/malformed/nonexistent/foreign project values, and no-project accounts. Record the form contract and test command/results in this change.

## 2. Student discovery and collaboration-profile access

- [x] 2.1 Extract the reusable display context to `accounts/profile_display.py`, update existing callers, and add collaboration context supporting an optional bound form; verify the existing owner/investor profile tests still pass and profile data is rendered consistently without imports between view modules.
- [x] 2.2 Add the student-only collaboration-profile GET route, extend directory access to students, exclude their own card, and add role-appropriate directory links and Students navigation; add and pass `accounts.tests.CollaboratorProfileAccessTests` and updated `accounts.test_discovery` tests for the complete directory-to-profile path, authentication, active student targets, incomplete profiles, and self-view redirection.
- [x] 2.3 Run the relevant account permission/follow/profile-visit regression tests to verify student browsing records no investor visits, students cannot edit another profile or use investor follow actions, and investor links still work. Record the intentional change from the old directory student-403 expectation and the test results in the design.

## 3. Authorized request creation

- [x] 3.1 Add the POST route and handler using the form, authenticated sender, URL receiver, Pending default, model validation, and constraint-backed `get_or_create`; add and pass `ideas.tests.SendCollaboratorRequestTests` for saved participants, sender success/redirect, receiver queries, unchanged membership/feedback-notification counts, duplicates in every status with original status/timestamp preserved, different pairs, and controlled concurrent-winner result handling.
- [x] 3.2 Extend the endpoint tests for login, student role, owner-only selection, self/non-student/missing/inactive receivers, missing/malformed/nonexistent projects, non-POST methods, missing CSRF tokens, and tampered sender/receiver/status fields; verify invalid attempts create no records and valid tampered-extra-field submissions still use server-controlled identities/status.
- [x] 3.3 Record the implemented endpoint, validation/duplicate feedback, test command/results, and receiver-persistence versus later inbox distinction in the design; verify the recorded behavior agrees with the specs and passing endpoint tests.

## 4. Profile action and browser flow

- [x] 4.1 Add the labelled project selector, CSRF token, Request Collaborator button, publish-first empty state, and inline field/non-field errors to the shared profile template; add and pass `accounts.tests.CollaboratorProfilePresentationTests` and `ideas.tests.CollaboratorRequestWorkflowTests` verifying owner-only choices, hidden self/investor controls, bound error/selection retention, valid browser-style submission, duplicate feedback, and navigation back to the selected profile.
- [x] 4.2 Manually verify student A's directory-to-student-B-profile flow, project selection, success confirmation, duplicate attempt, missing-selection error, no-project state, and a narrow viewport; record observed results separately from automated checks and track receiver-management verification in `manage-collaborator-requests` without declaring external story acceptance complete.

## 5. Integration checks

- [x] 5.1 Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `openspec validate send-collaborator-requests --strict`, `openspec validate --all`, and `git diff --check`; verify no new schema changes or unrelated edits and distinguish any previously recorded OpenSpec baseline failures from regressions.
- [x] 5.2 Run `python manage.py test` and verify all Django tests pass. Review the README Definition of Done, record stage-two coverage and pending recipient-facing/integrated/manual checks, team review, and Product Owner acceptance, without declaring the full story complete.

## Workflow follow-up

- Commit this stage on `T60-T65-collaborator-requests`; continue with T64–T65 after reviewing their full requirements, without an intermediate merge.
- Deliver the three stages in one PR to `main`, with closing references for completed tasks, including #115 and #116, and `Refs #98`.
- Archive this change after its implementation and applicable project review requirements are satisfied.
