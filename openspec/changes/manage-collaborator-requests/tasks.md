# Tasks

US028 (#99), T64 (#117), T65 (#118), and the receiving portion of US027 (#98). The Sent and receiver History tabs are additional requirements from this session. Preserve the existing T62–T63 working-tree changes on the shared T60–T65 branch.

## 1. Discoverable, private request lists

- [x] 1.1 Add the student-only Received/Sent list route, navigation, pending request cards with idea/creator details and decision forms, sent statuses, empty states, and a Sent link near the send form. Add and pass list/presentation tests covering user scoping, pending filtering, all sent statuses, navigation, escaping, and auth/role restrictions; record the implemented page contract in design.md.

## 2. Authorized invitation decisions

- [x] 2.1 Add the CSRF-protected POST decision endpoint with receiver-only lookup, validated actions/participants, conditional Pending transition, atomic acceptance/membership creation, decline, confirmation, and terminal-state preservation. Add and pass decision tests covering all three US028 criteria, methods/CSRF/auth/ownership, tampering, repeated/conflicting actions, existing membership, rollback, and a simulated winning competing decision; record the behavior and test results in design.md.

## 3. Visible membership and complete rendered workflow

- [x] 3.1 Display collaborators on idea details while retaining owner-only editing, and add/pass actual-form CSRF-enforcing send → inbox → accept/decline → Sent/membership workflow tests. Verify each US028 acceptance criterion through the rendered UI and document exact automated/browser observations and any external acceptance still pending.

## 4. Integration and Definition of Done

- [x] 4.1 Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`, strict validation for this change, `openspec validate --all`, and `git diff --check`; document results and any unrelated validation baseline failures without generating a migration.
- [x] 4.2 Run `python manage.py test`, verify all Django tests pass, and review the README Definition of Done. Record implemented/tested acceptance criteria and separately retain team review, integrated MVP, agreed wireframe, and Product Owner acceptance as pending where not observed.

## 5. Receiver history requested during manual acceptance

- [x] 5.1 Add a read-only receiver-scoped History tab showing Accepted/Rejected invitations with idea/creator details, active navigation, and an empty state. Verify history excludes Pending and other receivers' records, has no decision forms or mutations, preserves terminal-state protection, and retains accepted/declined outcomes through the rendered workflow. Pass focused tests, the full Django suite, system/migration checks, strict change validation, and whitespace checks; record browser observations and results in design.md.

## Workflow follow-up

- Include #117 and #118 in the shared final T60–T65 PR's completed task references, with story references #98 and #99. Review before closing stories.
- Obtain the README's required team, integrated/UX, and Product Owner review; archive the change only when applicable requirements are satisfied.
