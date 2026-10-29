# Spec Delta

## MODIFIED Requirements

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
