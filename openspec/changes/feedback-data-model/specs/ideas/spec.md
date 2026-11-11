# Spec Delta

## ADDED Requirements

### Requirement: Associate saved feedback with its idea and author
The system SHALL retain non-empty feedback text with a reference to the idea it concerns, an optional reference to the user who authored it, and the time it was submitted. If the author account is deleted, the feedback remains and its author reference becomes empty.

Source: US005 (#43)

#### Scenario: Non-empty feedback is recorded for an idea
- **WHEN** the later submission flow saves non-empty feedback submitted by an investor viewing a published idea
- **THEN** the feedback record contains the submitted text, identifies the idea and author, and records its submission timestamp
