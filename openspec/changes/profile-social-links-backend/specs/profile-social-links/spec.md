# Spec Delta

## Purpose

Preserve optional social account URLs as part of student profiles so users can share additional social and professional background with authorized profile viewers.

## ADDED Requirements

### Requirement: Persist optional social account URLs

The system SHALL store optional Instagram, Twitter, YouTube, and GitHub URLs in the student's profile when valid profile edits are saved.

Source: US0034 (#105)
Task: T77 (#130), supporting the add-social-media-links acceptance criterion.

#### Scenario: Save and retrieve social account URLs

- **WHEN** a signed-in student editing their profile submits valid social account URLs
- **THEN** those URLs are stored in that student's profile and are available when the profile is retrieved

#### Scenario: Leave social account URLs empty

- **WHEN** a signed-in student saves a profile without social account URLs
- **THEN** the profile can be saved with empty social URL values

#### Scenario: Update or remove a saved URL

- **WHEN** a signed-in student editing their profile replaces or clears a saved social account URL and submits the profile
- **THEN** the stored value is updated or cleared accordingly

### Requirement: Validate social account URLs on profile submission

The system SHALL validate submitted social account URLs on the server before saving profile edits and reject malformed URLs or protocols other than HTTP and HTTPS.

Source: US0034 (#105)
Task: T77 (#130), which explicitly includes backend validation.

#### Scenario: Reject an invalid social URL

- **WHEN** a signed-in student editing their profile submits an invalid social URL
- **THEN** validation reports an error on the corresponding field
- **AND** the submission does not persist profile changes

#### Scenario: Accept valid web links

- **WHEN** a signed-in student editing their profile submits valid HTTP or HTTPS social account URLs
- **THEN** URL validation permits the profile submission
