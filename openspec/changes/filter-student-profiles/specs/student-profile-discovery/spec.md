# Spec Delta

## Purpose

Help investors find students whose saved profiles match their technical interests and open those profiles to learn more.

## ADDED Requirements

### Requirement: Filter student profiles by skill

The system SHALL let a signed-in investor select a skill or expertise area and display only matching student profiles.

Source: US012 (#50)
Task: T37 (#69), T38 (#70)

#### Scenario: Investor selects a skill
- **WHEN** a signed-in investor viewing student profiles selects a skill
- **THEN** only profiles containing that skill are displayed
- **AND** the selected skill remains visible

#### Scenario: Investor browses without a filter
- **WHEN** a signed-in investor opens the directory without a skill filter
- **THEN** saved profiles of active student accounts are displayed, including incomplete profiles
- **AND** each result links to its student profile

### Requirement: Clear profile filters

The system SHALL let an investor clear the selected profile filter and return to the full directory.

Source: US012 (#50)
Task: T38 (#70)

#### Scenario: Investor clears a skill filter
- **WHEN** an investor with an applied skill filter chooses Clear filter
- **THEN** the full eligible profile list is displayed
- **AND** no skill remains selected

### Requirement: Explain when no profiles match

The system SHALL explain that no matching profiles were found when no profiles match the selected skill.

Source: US012 (#50)
Task: T38 (#70)

#### Scenario: Selected skill has no matching profiles
- **WHEN** an investor filters by a skill that no eligible profile contains
- **THEN** the directory displays a no-matching-profiles message
- **AND** the investor can clear the filter
