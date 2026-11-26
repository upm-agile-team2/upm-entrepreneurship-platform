# Spec Delta

## ADDED Requirements

### Requirement: View incoming pending collaborator requests
The system SHALL provide a signed-in student with a requests section listing all their Pending collaborator invitations with the idea's title, description, creator information, and Accept/Decline controls. It SHALL exclude other students' invitations and already-handled requests.

Source: US028 (#99), T64 (#117), T65 (#118); US027 (#98) Send request.

#### Scenario: Student opens received invitations
- **WHEN** a signed-in student with received Pending invitations opens the requests section
- **THEN** all their Pending invitations are displayed with idea and creator information and Accept/Decline controls
- **AND** other recipients' invitations and Accepted/Rejected invitations are absent

#### Scenario: No pending invitations
- **WHEN** a signed-in student without Pending invitations opens the requests section
- **THEN** an explanatory empty state is displayed

### Requirement: Accept an incoming collaborator request
The system SHALL let the addressed student accept a Pending invitation, record it as Accepted, and add that student as a collaborator to the invitation's idea as one indivisible operation. The accepted membership SHALL be visible on the idea detail page without granting owner editing rights.

Source: US028 (#99) Accept request, T64 (#117), T65 (#118).

#### Scenario: Student accepts a pending invitation
- **WHEN** the addressed signed-in student selects Accept for a Pending invitation
- **THEN** the invitation becomes Accepted and the student becomes a collaborator on that idea
- **AND** a confirmation is shown and the invitation leaves the pending inbox
- **AND** the idea detail page displays the student among its collaborators

#### Scenario: Acceptance cannot complete
- **WHEN** adding the collaborator fails while an invitation is being accepted
- **THEN** neither the Accepted state nor a new collaborator membership is retained

### Requirement: Decline an incoming collaborator request
The system SHALL let the addressed student decline a Pending invitation, record it as Rejected, and confirm the action without adding a collaborator.

Source: US028 (#99) Decline request, T64 (#117), T65 (#118).

#### Scenario: Student declines a pending invitation
- **WHEN** the addressed signed-in student selects Decline for a Pending invitation
- **THEN** the invitation becomes Rejected without creating a collaborator membership
- **AND** a confirmation is shown and the invitation leaves the pending inbox

### Requirement: Protect invitation decisions and terminal states
The system SHALL permit invitation decisions only through authenticated student POST submissions with valid CSRF protection, only for the addressed receiver and a Pending invitation. Repeated or conflicting decisions SHALL preserve the recorded terminal state and existing membership. Invalid decision values SHALL NOT change data.

Source: US028 (#99), T64 (#117); preserves US027 (#98)'s duplicate-prevention contract.

#### Scenario: Unauthorized invitation access
- **WHEN** an anonymous visitor, an investor, the sender, or another student attempts to process an invitation they cannot receive
- **THEN** access is denied or authentication is requested without changing invitations or memberships

#### Scenario: Invalid submission
- **WHEN** a decision is submitted with a non-POST method, missing CSRF protection, or an unsupported decision value
- **THEN** the submission is rejected without changing data

#### Scenario: Invitation was already handled
- **WHEN** a receiver repeats a decision or submits a conflicting decision after the invitation has been Accepted or Rejected
- **THEN** the original state and membership are preserved and the receiver is told it was already handled

### Requirement: View sent invitation statuses
The system SHALL let a signed-in student view only their own sent invitations, showing each idea, recipient, and Pending/Accepted/Rejected status.

Source: US027 (#98), US028 (#99); explicit sent-status visibility requested in this session, additional to the GitHub issues' incoming-list criteria.

#### Scenario: Sender checks an invitation's outcome
- **WHEN** a signed-in student opens Sent after sending an invitation or after its receiver handles it
- **THEN** their sent invitation is displayed with its idea, recipient, and current status
- **AND** invitations sent by other students are excluded

#### Scenario: No sent invitations
- **WHEN** a signed-in student who has sent no invitations opens Sent
- **THEN** an explanatory empty state is displayed

### Requirement: View handled incoming invitation history
The system SHALL provide a signed-in student with a read-only History list of their own Accepted and Rejected incoming invitations, including idea information, creator information, and current status. Pending invitations and invitations addressed to other students SHALL be excluded. History SHALL NOT offer Accept/Decline controls.

Source: US028 (#99); explicit receiver-history addition requested by the user during manual acceptance testing, beyond the GitHub pending-list criterion.

#### Scenario: Receiver revisits an accepted or declined invitation
- **WHEN** a signed-in student opens History after accepting or declining an invitation
- **THEN** that invitation is displayed with its project, creator, and Accepted or Rejected status
- **AND** it is absent from Received and cannot be acted on again from History
- **AND** Pending invitations and other receivers' invitations are absent from History

#### Scenario: No handled invitations
- **WHEN** a signed-in student with no Accepted or Rejected incoming invitations opens History
- **THEN** an explanatory empty state is displayed
