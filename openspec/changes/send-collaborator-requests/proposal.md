# Proposal

## Why

US0027 (#98) requires a student who owns a published idea to invite another student from their profile, with duplicate requests prevented. The T60–T61 models are implemented, but there is no sending endpoint or profile action, and the current student directory and other-student profile route admit only investors.

Refs #115 (T62), #116 (T63), #98 (US0027).

## What Changes

- Let signed-in students use the existing student directory and reach another student's read-only collaboration profile through a student-specific route.
- Add a project selector and a `Request Collaborator` submit button on that profile for students who own published ideas. The selector lists only the current user's ideas; students without ideas receive a prompt to publish one first.
- Add an authenticated, CSRF-protected POST action that validates the idea, sender, and receiver and stores a Pending request addressed to the selected student.
- Derive the sender from the session and the receiver from the profile URL; submitted identity or status fields cannot override them.
- Reuse the T61 unique project/receiver constraint. Repeated submissions, including after acceptance or rejection, keep the original request unchanged and return an explanatory message.
- Keep investor profile access, following, and investor-visit statistics on their existing routes. Student visits do not count as investor visits and do not grant profile-editing permissions.
- Add Django form, access, presentation, and workflow tests plus manual acceptance checks.

### Delivery and dependencies

Continue on `T60-T65-collaborator-requests`, using the committed `collaborator-data-models` implementation and `0007_add_collaborator_models`. This is stage two of the same final T60–T65 PR. Add `Closes #115`, `Closes #116`, and `Refs #98` to that PR; do not open an intermediate PR or wait for a model-stage merge.

### Out of scope

Request inboxes, accepting/rejecting requests, and creating memberships on acceptance belong to T64–T65. This stage makes the saved request available through its receiver relationship; the recipient-facing management screen remains unfinished. Email, push notifications, changing the feedback-notification schema, chat, and re-invitation after rejection are outside scope. This stage alone does not satisfy the entire story Definition of Done.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: Allow project owners to select a student from a profile and send a validated, non-duplicate collaborator request for their own published idea.

## Impact

- `ideas/forms.py`, `ideas/views.py`, `ideas/urls.py`: owner-scoped project selection, request creation, validation, and feedback.
- `accounts/discovery.py`, `accounts/views.py`, `accounts/urls.py`: student access to discovery and a separate collaboration-profile route. Extract the existing display-context helper to `accounts/profile_display.py` for use by both profile GET and request POST views.
- `templates/base.html`, `templates/accounts/student_discovery.html`, `templates/accounts/student_profile_detail.html`: navigation, role-appropriate profile links, and the collaboration form.
- Tests in `ideas` and `accounts`: update the directory's former student-denial expectation intentionally; retain investor-only profile, follow, edit, and visit-statistics protections.
- No model changes, database migration, or new external dependencies are expected.
