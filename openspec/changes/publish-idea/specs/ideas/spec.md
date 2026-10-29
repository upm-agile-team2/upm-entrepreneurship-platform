## MODIFIED Requirements

### Requirement: Submit an idea
The system SHALL publish an idea submitted by a signed-in student who has entered the required information, making it available to other users. The student MAY choose a category from the list of categories when submitting.

Source: US001 (#4)

#### Scenario: Signed-in student submits an idea
- **WHEN** a signed-in student who has entered the required information submits the idea
- **THEN** the idea is published
- **AND** it is available to other users

#### Scenario: Signed-in student submits an idea with a category
- **WHEN** a signed-in student who has entered the required information selects a category from the list and submits the idea
- **THEN** the idea is published with that category

### Requirement: Require essential information
The system SHALL NOT publish an idea without a title or description, and SHALL ask the student to complete the missing information.

Source: US001 (#4)

#### Scenario: Student publishes without a title or description
- **WHEN** a student creating an idea tries to publish it without a title or description
- **THEN** the platform asks them to complete the missing information

#### Scenario: Student publishes without a title
- **WHEN** a student creating an idea who has entered a description tries to publish it without a title
- **THEN** the platform asks them to enter the title
- **AND** the idea is not published

#### Scenario: Student publishes without a description
- **WHEN** a student creating an idea who has entered a title tries to publish it without a description
- **THEN** the platform asks them to enter the description
- **AND** the idea is not published
