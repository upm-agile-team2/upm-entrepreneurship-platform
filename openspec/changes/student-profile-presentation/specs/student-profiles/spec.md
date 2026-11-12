# Spec Delta

## Purpose

Present student profiles to their owners and to authenticated investors.

## ADDED Requirements

### Requirement: Provide a student profile editor and own-profile view

The system SHALL provide a student-facing interface for editing a student's profile information and viewing their saved profile.

Source: US009 (#47)
Task: T33 (#65)

#### Scenario: Student views and edits their own profile

- **WHEN** a signed-in student opens their own profile or chooses to edit it
- **THEN** their saved profile details are shown and can be edited through the student profile editor

## ADDED Requirements

### Requirement: Open a student's profile

The system SHALL display a student's profile when an authenticated investor selects the student's profile from an idea.

Source: US010 (#48)
Task: T34 (#66)

#### Scenario: Investor opens a profile from an idea

- **WHEN** an authenticated investor viewing an idea selects its student author's profile link
- **THEN** that student's profile is displayed

### Requirement: Display available investor-facing profile information

The system SHALL display the student's available skills, portfolio projects, and experience on the investor-facing profile.

Source: US010 (#48)
Task: T34 (#66)

#### Scenario: Investor views profile information

- **WHEN** an authenticated investor opens a student's profile
- **THEN** the available skills, projects, and experience are displayed

### Requirement: Handle incomplete student profiles

The system SHALL display available information without errors when a student's profile or some profile fields have not been completed.

Source: US010 (#48)
Task: T34 (#66)

#### Scenario: Investor views an incomplete profile

- **WHEN** an authenticated investor opens a student's profile with missing profile data or empty fields
- **THEN** any available information is displayed without errors
