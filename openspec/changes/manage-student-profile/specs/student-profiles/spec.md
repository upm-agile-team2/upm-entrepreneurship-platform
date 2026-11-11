# Spec Delta

## Purpose

Student profiles let students maintain and present information about their skills and projects.

## ADDED Requirements

### Requirement: Create a student profile
The system SHALL create a profile when a signed-in student enters profile details and saves them.

Source: US009 (#47)
Task: T32 (#64)

#### Scenario: Student saves profile details
- **WHEN** a signed-in student enters profile details and saves them
- **THEN** a profile is created for that student

### Requirement: Display saved skills and projects
The system SHALL display a student's saved skills and projects when the student's profile is viewed.

Source: US009 (#47)
Task: T32 (#64)

#### Scenario: Student profile is viewed
- **WHEN** a profile with saved skills and projects is viewed
- **THEN** those skills and projects are displayed

### Requirement: Edit one's own profile
The system SHALL save updated profile information when a student updates their own profile.

Source: US009 (#47)
Task: T32 (#64)

#### Scenario: Student updates their profile
- **WHEN** a student who owns a profile updates and saves its information
- **THEN** the profile shows the updated details
