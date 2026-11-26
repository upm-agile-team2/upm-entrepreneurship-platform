# Investor profile discovery

## Purpose

Students can explore investor profiles and find people whose experience and interests match their projects.

## ADDED Requirements

### Requirement: Open an investor profile
The system SHALL let a student open an investor profile from a linked investor name.

Source: US025 (#96)

#### Scenario: Open a linked profile
- **WHEN** a signed-in student selects an investor's linked name
- **THEN** the system displays that investor's profile

### Requirement: Display available investor profile information
The system SHALL display saved experience, past projects, interests, and feedback that is public. It SHALL render the available information when any optional field is missing.

Source: US025 (#96)

#### Scenario: Review a profile with public feedback
- **WHEN** a student opens an investor profile
- **THEN** they can see the available profile information and the investor's public feedback

#### Scenario: Incomplete investor profile
- **WHEN** a student opens a profile with incomplete fields
- **THEN** the system shows the available details without errors

### Requirement: Filter investor profiles by interest
The system SHALL show only matching investor profiles after the student selects an interest.

Source: US026 (#97)

#### Scenario: Student filters by interest
- **WHEN** a signed-in student selects an interest on the investor directory
- **THEN** the directory shows only investor profiles associated with that interest

### Requirement: Clear investor profile filters
The system SHALL restore the full directory after the student clears the interest filter.

Source: US026 (#97)

#### Scenario: Student clears an active interest filter
- **WHEN** a student clears the selected interest
- **THEN** the directory shows the full list of available investor profiles

### Requirement: Show no matching investor profiles
The system SHALL explain that there are no matching investor profiles when an applied interest produces no results.

Source: US026 (#97)

#### Scenario: No profile matches the selected interest
- **WHEN** a student selects an interest with no available investor profiles
- **THEN** the directory displays a no-match explanation
