# Spec Delta

## MODIFIED Requirements

### Requirement: Filter by category
The system SHALL display only the ideas in the category that an investor selects.

Source: US003 (#6)

#### Scenario: Investor selects a category
- **WHEN** an investor selects a category and the list updates
- **THEN** only ideas in that category are displayed

#### Scenario: Every category can be selected
- **WHEN** an investor opens the discovery page
- **THEN** the category filter offers every stored category

#### Scenario: Selected category stays visible
- **WHEN** an investor has selected a category and the list updates
- **THEN** the category filter shows that category as the selected one

### Requirement: No matching ideas
The system SHALL display a message explaining that no matching ideas were found when no ideas match the selected category.

Source: US003 (#6)

#### Scenario: No ideas in the selected category
- **WHEN** the filtered list loads and no ideas match the selected category
- **THEN** the platform displays a message explaining that no matching ideas were found

#### Scenario: Requested category does not exist
- **WHEN** the discovery page is requested with a category value that does not identify any stored category
- **THEN** no ideas are listed and the platform displays a message explaining that no matching ideas were found
