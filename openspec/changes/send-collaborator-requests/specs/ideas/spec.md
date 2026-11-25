# Spec Delta

## ADDED Requirements

### Requirement: Select a collaborator from another student's profile
The system SHALL let a signed-in student view another student's profile and select one of their own published ideas to request that student's collaboration. The profile SHALL offer a project selector and a `Request Collaborator` action for project owners.

Source: US0027 (#98), T63 (#116).

#### Scenario: Project owner selects a potential collaborator
- **WHEN** a signed-in student who owns published ideas opens another student's profile from the student directory
- **THEN** that student's available profile information is displayed
- **AND** a project selector lists only ideas owned by the signed-in student
- **AND** the student can select an idea and choose `Request Collaborator`

#### Scenario: Student has no published ideas
- **WHEN** a signed-in student without published ideas views another student's profile
- **THEN** the profile explains that they need to publish an idea before inviting a collaborator
- **AND** there is no usable request submission control

#### Scenario: Student views their own profile
- **WHEN** a signed-in student views their own profile
- **THEN** the platform does not offer an action to invite themselves

### Requirement: Send a collaborator request to the selected student
The system SHALL save a Pending collaborator request for a valid idea selection, addressed from the signed-in student owner to the student whose profile they selected, and confirm successful submission. The saved request SHALL be available among the receiver's received requests.

Source: US0027 (#98), T62 (#115), T63 (#116).

#### Scenario: Owner sends a valid request
- **WHEN** a signed-in student who owns a published idea selects another student and submits the collaborator request for that idea
- **THEN** exactly one Pending request is saved with that idea, owner, and receiver
- **AND** it can be retrieved among that student's received requests
- **AND** the sender sees a success confirmation
- **AND** submitting the invitation alone does not add a project collaborator

### Requirement: Authorize collaborator request submissions
The system SHALL accept collaborator requests only from signed-in student owners of the selected idea, to a different student. Submitted sender, receiver, or status values SHALL NOT override the authenticated sender, selected profile, or initial Pending status.

Source: US0027 (#98), T62 (#115).

#### Scenario: Anonymous visitor attempts to send
- **WHEN** a visitor who is not signed in attempts to send a collaborator request
- **THEN** the platform asks them to sign in
- **AND** no request is created

#### Scenario: Invalid project or participants
- **WHEN** a submission comes from an investor, selects another owner's or a nonexistent idea, or targets the sender themselves or a non-student
- **THEN** the submission is rejected
- **AND** no request or collaborator membership is created

#### Scenario: Submitted identities or status are tampered with
- **WHEN** a signed-in student submits an otherwise valid request with extra fields claiming a different sender, receiver, or initial status
- **THEN** the saved request still uses the signed-in sender, selected profile's receiver, and Pending status

### Requirement: Explain invalid collaboration project selections
The system SHALL explain missing or invalid project selections without saving a request. A failed submission SHALL retain the profile context and any valid selected project so the student can understand and correct the error.

Source: US0027 (#98), T62 (#115), T63 (#116).

#### Scenario: No valid project is selected
- **WHEN** a student submits the profile's collaborator form without a valid selection from their own ideas
- **THEN** an explanatory validation error is displayed on the profile
- **AND** no collaborator request is saved

### Requirement: Reject repeated collaborator submissions without changing the original
The system SHALL prevent another request for the same project and receiver, explain that a request already exists, and preserve its original status and creation time. This SHALL apply to Pending, Accepted, and Rejected requests, including repeated submissions arriving close together.

Source: US0027 (#98), T62 (#115). The previously agreed no-resend rule also applies after rejection.

#### Scenario: An invitation already exists
- **WHEN** a student submits a request for an idea and receiver that already have a Pending, Accepted, or Rejected request
- **THEN** no second request is saved
- **AND** the original request's status and creation time are preserved
- **AND** the sender sees an explanation that the request already exists

#### Scenario: Another submission creates the pair first
- **WHEN** two valid submissions concern the same idea and receiver and one creates the request before the other's creation attempt
- **THEN** at most one request is stored for that pair
- **AND** the losing submission is handled as an existing request rather than changing it

#### Scenario: Different project or receiver
- **WHEN** a student submits a valid request for a different project or receiver
- **THEN** that request can be saved independently
