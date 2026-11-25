# Spec Delta

## ADDED Requirements

### Requirement: Select and save a project's development stage

The system SHALL let the owning student select one optional development stage while creating or editing an idea and save it with that project. Available stages SHALL be Idea, Prototype, MVP, Launched, and Growth.

Source: US030 (#101), select-development-stage acceptance criterion.
Option catalog and optionality: user-confirmed product decisions, 2026-11-24.

#### Scenario: Select a stage during creation

- **WHEN** a signed-in student creating an idea selects an available development stage and submits a valid form
- **THEN** the selected stage is saved with the new project

#### Scenario: Update a project's stage

- **WHEN** the owning student editing an idea selects a different available development stage and saves
- **THEN** the newly selected stage is stored and shown when the editor is reopened

#### Scenario: Leave or clear the development stage

- **WHEN** the owning student saves a valid idea with no stage selected
- **THEN** the idea is saved without a development stage

#### Scenario: Reject an unavailable stage

- **WHEN** a student submits an idea form containing a development stage outside the available options
- **THEN** the form reports an error on the stage selection and does not save the submission

### Requirement: Select and save a project's required support

The system SHALL let the owning student select zero or more support types when creating or editing a project and save the selections with that project. Available support types SHALL be Funding, Technical support, Mentoring, Marketing, and Team members.

Source: US030 (#101), add-required-support acceptance criterion.
Option catalog, creation-form availability, multiple selection, and optionality: user-confirmed product decisions, 2026-11-24.

#### Scenario: Save multiple support needs

- **WHEN** the owning student editing a project selects Funding and Technical support and saves a valid form
- **THEN** both selected support types are stored with the project
- **AND** reopening the editor shows both selections

#### Scenario: Include support needs during creation

- **WHEN** a signed-in student creating a project selects available support types and submits a valid form
- **THEN** those support selections are stored with the new project

#### Scenario: Clear support needs

- **WHEN** the owning student editing a project deselects every support type and saves a valid form
- **THEN** the project's support selections are empty

#### Scenario: Reject unavailable support types

- **WHEN** a student submits a project form containing an unavailable support selection
- **THEN** the form reports an error on required support and does not save the submission

### Requirement: Display project stage and support badges

The system SHALL display a project's saved development stage and requested support types as readable badges on its detail page. Unfilled stage or support information SHALL be omitted without preventing access to otherwise visible project details.

Source: US030 (#101), display-project-needs acceptance criterion; T70 badge presentation.

#### Scenario: Another user views project needs

- **WHEN** another user opens the detail page of a visible project with a development stage and support selections
- **THEN** the current stage and each selected support type are displayed as badges using their readable labels

#### Scenario: A project contains only partial needs information

- **WHEN** another user opens a visible project containing only a stage or only support selections
- **THEN** the available information is displayed without empty badges for missing values

#### Scenario: An existing project has no stage or support needs

- **WHEN** another user opens a visible project with neither field filled in
- **THEN** its existing details remain visible and no empty stage or support badges are shown
