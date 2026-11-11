# Spec Delta

## Purpose

Student profiles store information students use to showcase their skills and projects to potential investors.

## ADDED Requirements

### Requirement: Store a student's profile information
The system SHALL retain a student's profile information about their bio, skills, portfolio projects, and experience so it can support a profile showcasing that information.

Source: US009 (#47)
Task: T31 (#63) identifies the profile data fields as user, bio, skills, portfolio projects, and experience.

#### Scenario: Student profile data is stored
- **WHEN** a student profile is saved with bio, skills, portfolio projects, and experience
- **THEN** the profile information is retained for that student's profile

Design decisions for T31 (#63)—the one-to-one relationship, student-only model validation, optional bio, empty-list JSON defaults, normalized skills, and case-insensitive skill uniqueness—are documented in `design.md`. They are agreed model-design choices, not additional acceptance criteria stated explicitly in US009 (#47).
