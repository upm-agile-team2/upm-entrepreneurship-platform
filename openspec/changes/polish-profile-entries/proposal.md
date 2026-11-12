# Proposal

## Why

The profile screen exposes portfolio and experience as formatted JSON, and its editor asks students to enter JSON arrays. Students and investors need readable profile information and ordinary editing controls for the MVP. This correction improves the existing US009 (#47) and US010 (#48) interfaces introduced by T33 (#65), T34 (#66) and PR #86.

## What Changes

- Present projects and experience as readable entries with headings, descriptions and available supporting information.
- Provide ordinary, repeatable project and experience fields in the student editor.
- Preserve saved arrays, aliases, additional metadata and legacy entry types when unchanged.
- Keep validation errors and submitted values visible, and prevent partial saves on invalid entries.
- Retain existing ownership restrictions, JSON storage and compatibility with the original complete-form POST contract.

Out of scope: model/schema changes, following behavior, feedback, profile discovery, analytics, deployment and automatic issue closure.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Existing profile creation, editing and display requirements already cover the workflow. This is a presentation and usability correction with no new durable capability; `skip_specs: true` records that no delta specs are needed.

## Impact

Profile forms, view context, templates and scoped CSS; a small local script for adding form rows; regression tests and review documentation. No new dependencies or migrations. This change is tracked separately from T35/T36 and delivered with the related student-profile work.
