# Proposal

## Why

Invitations can currently be sent and saved, but students have no website entry point to read or act on them. Complete US028 (#99), T64 (#117) and T65 (#118), and make US027 (#98)'s recipient delivery visible in the application.

## What Changes

- Add a student-only Collaborator requests navigation entry and a received-request inbox showing pending invitations, idea information, creator information, and Accept/Decline controls.
- Accept an invitation by atomically recording Accepted and creating the receiver's collaborator membership. Decline records Rejected without creating a membership. Only the addressed student may act, and only Pending requests may transition.
- Add a Sent tab listing the current student's sent invitations and their statuses. This is an explicit addition requested in this conversation; the original GitHub tasks specify the incoming list, not a sent-history screen.
- Add a read-only History tab showing the current receiver's Accepted and Rejected invitations. This is a further explicit user request from manual acceptance testing; handled invitations leave Received but remain visible to their receiver in History.
- Confirm each action and remove handled requests from the pending inbox. Display accepted collaborators on the idea detail page so membership is visible without granting idea-editing rights.
- Add endpoint, privacy, state-transition, rollback, and rendered-form workflow tests for the three US028 acceptance criteria and the session's sent-status requirement.

### Delivery

Continue on `T60-T65-collaborator-requests`, preserving the existing uncommitted T62–T63 implementation. This is the third stage of the planned single PR. Its task closing references are #117 and #118, with story references #98 and #99. Do not declare either story's full Definition of Done complete without the required review and integrated/UX/Product Owner acceptance.

### Out of scope

Email/push notifications, chat, invitation cancellation, resending rejected requests, collaborator removal, and collaborator editing rights are outside this change. Reuse the existing request and membership schema and keep feedback notifications separate.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: Receive and manage collaborator invitations, view received history and sent statuses, and expose accepted project membership.

## Impact

- `ideas/views.py`, `ideas/urls.py`: scoped request queries and authorized transactional decision endpoints.
- `templates/base.html`, new request-list template, and `templates/ideas/idea_detail.html`: discoverable invitation inbox, sent list, and membership display.
- New focused Django tests and this OpenSpec change's artifacts.
- No migrations, external dependencies, or feedback notification schema changes.
