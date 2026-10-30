## ADDED Requirements

### Requirement: Edit an owned idea
The system SHALL allow a signed-in student to edit the title, description, and optional category of an idea they own. The system SHALL reject edit access and submissions from non-students and users who do not own the idea with HTTP 403.

Source: US002 (#5)

#### Scenario: Owner edits an idea
- **WHEN** a signed-in student who owns an idea submits valid updated details
- **THEN** the platform stores the title, description, and selected category on that idea

#### Scenario: Another user attempts to edit an idea
- **WHEN** a user who does not own an idea attempts to access or submit its edit form
- **THEN** the platform responds with HTTP 403

### Requirement: Validate edited idea details
The system SHALL identify missing title or description information and preserve submitted values when a student edits an idea with invalid details.

Source: US002 (#5)

#### Scenario: Student edits an idea with a missing required field
- **WHEN** a student submits an edit with a blank or whitespace-only title or description
- **THEN** the platform displays an inline error for each missing field and does not save the changes
