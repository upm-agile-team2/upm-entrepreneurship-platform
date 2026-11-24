# Spec Delta

## Purpose

Allow students to share social and professional background through editable social account links, and allow authorized profile viewers to open the available external accounts.

## ADDED Requirements

### Requirement: Edit social media links through the profile editor

The system SHALL provide optional Instagram, Twitter, YouTube, and GitHub URL inputs in the student's profile editor and save valid submitted links in that student's profile.

Source: US0034 (#105)
Task: T78 (#131), using the backend supplied by T77 (#130).

#### Scenario: Student saves social media links

- **WHEN** a signed-in student editing their profile submits valid Instagram, Twitter, YouTube, or GitHub URLs
- **THEN** the submitted URLs are saved in that student's profile
- **AND** reopening the editor shows the saved values

#### Scenario: Student removes a social media link

- **WHEN** a signed-in student editing their profile clears a previously saved social URL and saves the profile
- **THEN** that social link is removed from their profile

#### Scenario: Student submits an invalid social URL

- **WHEN** a signed-in student editing their profile submits a malformed URL or a URL using a protocol other than HTTP or HTTPS
- **THEN** the editor displays an error beside that input and preserves the submitted values for correction
- **AND** the invalid submission does not persist profile changes

### Requirement: Display available social media links on a profile

The system SHALL display the available Instagram, Twitter, YouTube, and GitHub links as platform icons with readable names when an authorized viewer opens a student's profile. A platform without a link SHALL be omitted.

Source: US0034 (#105)
Task: T78 (#131).

#### Scenario: Another user views saved social links

- **WHEN** an authenticated investor opens a student's profile containing social media links
- **THEN** each available link is displayed with its corresponding platform icon and name

#### Scenario: Only some social accounts are provided

- **WHEN** an authorized viewer opens a student's profile with only some social URLs filled in
- **THEN** only those platforms are displayed

#### Scenario: No social accounts are provided

- **WHEN** an authorized viewer opens a student's profile with no social URLs
- **THEN** no social icons or empty social-media section are displayed

### Requirement: Open the selected social media page

The system SHALL link each displayed social icon to the saved URL for that platform so a viewer can open the corresponding external page.

Source: US0034 (#105)
Task: T78 (#131).

#### Scenario: Another user selects a social link

- **WHEN** an authenticated investor viewing a student's profile selects an available social link
- **THEN** the browser opens the URL saved for that platform
