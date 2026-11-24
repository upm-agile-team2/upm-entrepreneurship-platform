# Spec Delta

## ADDED Requirements

### Requirement: Store project collaborators
The system SHALL persist each project collaborator with a unique record identifier, the project, the student collaborator, and the creation timestamp. Each student SHALL have at most one membership in the same project.

Source: US0027 (#98), T60 (#113).

#### Scenario: Store a collaborator relationship
- **WHEN** a valid collaborator membership is saved for a published idea and another student
- **THEN** its identifier, project, student, and creation timestamp can be retrieved
- **AND** the student can be retrieved among the project's collaborators

#### Scenario: Reject a duplicate membership
- **WHEN** a student is already recorded as a collaborator on an idea and another membership is saved for the same pair
- **THEN** the duplicate membership is rejected
- **AND** the existing membership is preserved

### Requirement: Store collaborator requests separately from memberships
The system SHALL persist collaborator requests with a unique identifier, project, sender, receiver, status, and creation timestamp. New requests SHALL default to Pending. Storing a request SHALL NOT itself create a collaborator membership.

Source: US0027 (#98), T61 (#114).

#### Scenario: Persist a pending request for its receiver
- **WHEN** a request from an idea's student owner to another student is saved without an explicit status
- **THEN** its identifier, project, sender, receiver, Pending status, and creation timestamp can be retrieved
- **AND** it can be retrieved among the receiver's received requests and the sender's sent requests
- **AND** the receiver is not automatically added to the project's collaborators

### Requirement: Validate student collaboration participants
The system SHALL validate that a request sender is the project's student owner and its receiver is a different student. It SHALL validate that a collaborator membership identifies a student other than the project owner.

Source: US0027 (#98), T60 (#113), T61 (#114).

#### Scenario: Validate the owner and another student
- **WHEN** a request from a published idea's student owner to another student is validated
- **THEN** its participants satisfy collaboration validation

#### Scenario: Reject a sender who is not the owner
- **WHEN** a request whose sender does not own the idea is validated
- **THEN** validation rejects the sender

#### Scenario: Reject self-invitations and non-student participants
- **WHEN** a request to the sender themselves or a request involving a non-student sender or receiver is validated
- **THEN** validation rejects the invalid participants

#### Scenario: Reject an invalid collaborator membership
- **WHEN** a membership identifying the project owner or a non-student as the collaborator is validated
- **THEN** validation rejects the collaborator

### Requirement: Prevent repeated requests for the same project and student
The system SHALL allow at most one request for a given project and receiver, including when the existing request is Pending, Accepted, or Rejected. This rule SHALL NOT prevent a separate request for a different project or receiver.

Source: US0027 (#98), T61 (#114). The user clarified that rejection does not permit resending.

#### Scenario: Reject a repeated request regardless of its status
- **WHEN** a request already exists for a project and student with Pending, Accepted, or Rejected status and another request is saved for that same pair
- **THEN** the duplicate is rejected
- **AND** the original request is preserved

#### Scenario: Permit a request for a different pair
- **WHEN** an existing request concerns a different project or receiver and a valid request is saved
- **THEN** the new request is stored independently
