# accounts Specification

## Purpose
User accounts for the platform: visitors create an account, registered users sign in to access the features available to them, and authenticated users log out securely.

## Requirements

### Requirement: Create account
The system SHALL create an account when a visitor submits the registration form with the required valid information.

Source: US013 (#1)

#### Scenario: Visitor registers with valid information
- **WHEN** a visitor who has entered the required valid information submits the registration form
- **THEN** an account is created

### Requirement: Validate registration
The system SHALL display an explanatory error message when the registration form is submitted with required information missing or invalid.

Source: US013 (#1)

#### Scenario: Registration with missing or invalid information
- **WHEN** a visitor submits the registration form with required information missing or invalid
- **THEN** an explanatory error message is displayed

### Requirement: Prevent duplicate accounts
The system SHALL NOT create a second account for an email address that is already registered, and SHALL ask the visitor to sign in or use another address.

Source: US013 (#1)

#### Scenario: Registration with an already registered email address
- **WHEN** a visitor tries to register with an email address that is already registered
- **THEN** the platform asks them to sign in or use another address

### Requirement: Valid sign-in
The system SHALL sign in a user who submits the sign-in form with valid credentials.

Source: US014 (#2)

#### Scenario: User signs in with valid credentials
- **WHEN** a user who has entered valid credentials submits the sign-in form
- **THEN** they are signed in

### Requirement: Invalid sign-in
The system SHALL deny access and display an error message when a user submits the sign-in form with incorrect credentials.

Source: US014 (#2)

#### Scenario: User signs in with incorrect credentials
- **WHEN** a user who has entered incorrect credentials submits the sign-in form
- **THEN** access is denied
- **AND** an error message is displayed

### Requirement: Restrict account features
The system SHALL ask a user who is not signed in to sign in when they try to access a feature that requires an account.

Source: US014 (#2)

#### Scenario: Anonymous user opens a feature that requires an account
- **WHEN** a user who is not signed in tries to access a feature requiring an account
- **THEN** the platform asks them to sign in

### Requirement: End session
The system SHALL end the session of a signed-in user who selects log out.

Source: US015 (#3)

#### Scenario: Signed-in user logs out
- **WHEN** a signed-in user selects log out
- **THEN** their session ends

### Requirement: Prevent access after logout
The system SHALL ask a user who has logged out to sign in again when they try to open a restricted page.

Source: US015 (#3)

#### Scenario: Logged-out user opens a restricted page
- **WHEN** a user who has logged out tries to open a restricted page
- **THEN** the platform asks them to sign in again
