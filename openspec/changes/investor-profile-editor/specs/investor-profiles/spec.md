# Investor profiles

## Purpose

Investors can describe their interests, experience, and past projects so that students can learn about their background.

## ADDED Requirements

### Requirement: Create an investor profile
The system SHALL create an investor profile when the authenticated investor saves valid profile details.

Source: US024 (#95)

#### Scenario: Investor saves profile details for the first time
- **WHEN** a signed-in investor enters valid profile details and saves them
- **THEN** the investor's profile is created

### Requirement: Display saved investor information
The system SHALL display the investor's saved experience, past projects, and interests when their profile is viewed.

Source: US024 (#95)

#### Scenario: Investor views their saved information
- **WHEN** an investor who has saved their experience, past projects, and interests opens their profile
- **THEN** the saved information is displayed

### Requirement: Edit an investor profile
The system SHALL let an investor update the information on their own profile.

Source: US024 (#95)

#### Scenario: Investor updates their existing profile
- **WHEN** a signed-in investor changes valid details on their own profile and saves them
- **THEN** their profile displays the updated information
