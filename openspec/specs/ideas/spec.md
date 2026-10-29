# ideas Specification

## Purpose
Entrepreneurial ideas (also called projects): students publish and edit their ideas, and investors browse published ideas, filter them by category and view their details.

## Requirements

### Requirement: Submit an idea
The system SHALL publish an idea submitted by a signed-in student who has entered the required information, making it available to other users.

Source: US001 (#4)

#### Scenario: Signed-in student submits an idea
- **WHEN** a signed-in student who has entered the required information submits the idea
- **THEN** the idea is published
- **AND** it is available to other users

### Requirement: Require essential information
The system SHALL NOT publish an idea without a title or description, and SHALL ask the student to complete the missing information.

Source: US001 (#4)

#### Scenario: Student publishes without a title or description
- **WHEN** a student creating an idea tries to publish it without a title or description
- **THEN** the platform asks them to complete the missing information

### Requirement: Select edit option
The system SHALL take a student to the edit view when they click the edit button while viewing one of their ideas.

Source: US002 (#5)

#### Scenario: Student clicks the edit button on their idea
- **WHEN** a student viewing one of their ideas clicks the edit button
- **THEN** they go to the edit view

### Requirement: Enter idea details
The system SHALL store the title and description that a student enters while editing an idea.

Source: US002 (#5)

#### Scenario: Student changes the title and description
- **WHEN** a student editing an idea enters a title and description
- **THEN** the platform stores those details with the idea

### Requirement: Select a category
The system SHALL display with the idea the category that a student selects and saves while editing it.

Source: US002 (#5)

#### Scenario: Student selects a category and saves
- **WHEN** a student editing an idea selects a category and saves
- **THEN** the category is displayed with the idea

### Requirement: Validate required fields
The system SHALL identify the missing information when a student tries to save an idea with a required field missing.

Source: US002 (#5)

#### Scenario: Student saves an idea with a required field missing
- **WHEN** a student tries to save an idea while a required field is missing
- **THEN** the platform identifies the missing information

### Requirement: Browse published ideas
The system SHALL display a list of the published ideas when an investor opens the discovery page and published ideas are available.

Source: US003 (#6)

#### Scenario: Investor opens the discovery page
- **WHEN** an investor opens the discovery page and published ideas are available
- **THEN** the platform displays a list of them

### Requirement: Filter by category
The system SHALL display only the ideas in the category that an investor selects.

Source: US003 (#6)

#### Scenario: Investor selects a category
- **WHEN** an investor selects a category and the list updates
- **THEN** only ideas in that category are displayed

### Requirement: Clear filters
The system SHALL display the full list of published ideas when an investor clears an applied category filter.

Source: US003 (#6)

#### Scenario: Investor clears the category filter
- **WHEN** an investor who has applied a category filter clears the filter
- **THEN** the full list of published ideas is displayed

### Requirement: No matching ideas
The system SHALL display a message explaining that no matching ideas were found when no ideas match the selected category.

Source: US003 (#6)

#### Scenario: No ideas in the selected category
- **WHEN** the filtered list loads and no ideas match the selected category
- **THEN** the platform displays a message explaining that no matching ideas were found

### Requirement: Open project details
The system SHALL display the detail page of a project when an investor selects it from the project list.

Source: US004 (#7)

#### Scenario: Investor selects a project from the list
- **WHEN** an investor viewing the project list selects a project
- **THEN** the platform displays its detail page

### Requirement: Display project information
The system SHALL display the title, description and category of a project when an investor opens it.

Source: US004 (#7)

#### Scenario: Investor opens a project
- **WHEN** an investor opens a project
- **THEN** its title, description and category are displayed

### Requirement: Return to the project list
The system SHALL return an investor viewing project details to the project list when they select the return-to-list option.

Source: US004 (#7)

#### Scenario: Investor returns to the project list
- **WHEN** an investor viewing project details selects the return-to-list option
- **THEN** the platform returns them to the project list
