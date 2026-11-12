# Spec Delta

## Purpose

Let investors keep and revisit a personal collection of student profiles that interest them.

## ADDED Requirements

### Requirement: Follow a student profile

The system SHALL let a signed-in investor follow a student from the student's profile and add that student to the investor's followed list.

Source: US011 (#49)

#### Scenario: Investor follows a student
- **WHEN** a signed-in investor viewing a student's profile chooses Follow
- **THEN** that student is added to the investor's followed list
- **AND** the profile offers Unfollow instead of Follow

#### Scenario: Repeated follow does not duplicate a student
- **WHEN** an investor repeats a follow action for a student they already follow
- **THEN** the student appears only once in their followed list

#### Scenario: Investor follows an incomplete profile
- **WHEN** a signed-in investor chooses Follow on a student's profile with missing profile information
- **THEN** that student is added to their followed list without requiring the student to complete their profile

#### Scenario: Following requires an investor account
- **WHEN** a visitor who is not signed in attempts to follow a student
- **THEN** the platform asks them to sign in

#### Scenario: Student accounts cannot follow other students
- **WHEN** a signed-in student attempts to follow another student
- **THEN** the platform denies the investor-only action

### Requirement: Unfollow a student profile

The system SHALL let a signed-in investor remove a student from their own followed list.

Source: US011 (#49)

#### Scenario: Investor unfollows a student
- **WHEN** a signed-in investor following a student chooses Unfollow
- **THEN** the student is removed from that investor's followed list
- **AND** the student's profile offers Follow again

#### Scenario: Unfollowing is isolated between investors
- **WHEN** one investor unfollows a student who is also followed by another investor
- **THEN** only the first investor's follow relationship is removed

### Requirement: View followed student profiles

The system SHALL display the signed-in investor's followed student profiles and let that investor open each profile.

Source: US011 (#49)

#### Scenario: Investor opens their followed list
- **WHEN** a signed-in investor opens Following
- **THEN** their followed students are displayed with links to their profiles
- **AND** students followed only by other investors are not included

#### Scenario: Investor has no followed profiles
- **WHEN** a signed-in investor with no followed students opens Following
- **THEN** the platform explains that they are not following any students yet

#### Scenario: Investor removes a student from the list
- **WHEN** a signed-in investor chooses Unfollow from their followed list
- **THEN** the list is displayed again without that student
