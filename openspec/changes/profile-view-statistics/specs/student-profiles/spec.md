# Spec Delta

## Purpose

Let students see how much interest investors show in their profile.

## ADDED Requirements

### Requirement: View profile visit count

The system SHALL display the total number of profile visits received when a student looks at their own profile.

Source: US019 (#52)
Task: T41 (#73), T42 (#74)

#### Scenario: Student checks their profile visits

- **WHEN** a student who has received investor visits opens their own profile
- **THEN** the platform displays the total number of profile visits received

### Requirement: Zero visits state

The system SHALL indicate that no visits have been recorded yet when a student's profile has no visits.

Source: US019 (#52)
Task: T42 (#74)

#### Scenario: New profile without visits

- **WHEN** a student whose profile has no visits yet opens their own profile
- **THEN** the platform indicates that no visits have been recorded yet
