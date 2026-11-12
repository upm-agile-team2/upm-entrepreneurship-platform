# Proposal

## Why

US012 (#50) requires investors to find students by skills or expertise, but profiles are currently reachable only through ideas. T37 (#69) and T38 (#70) add a profile directory and its skill filter.

## What Changes

- Provide an investor-only directory of active student accounts with a saved StudentProfile, including incomplete profiles.
- Filter the directory by one selected skill from the existing catalogue, using a shareable GET URL.
- Add an investor navigation link, responsive profile cards, a result count, clear-filter control and distinct empty states.
- Validate unsupported filter values and preserve the boundary between browsing cards and recording a profile visit.
- Cover all three US012 acceptance criteria and access restrictions with database-backed tests.

Out of scope: new models or migrations, multiple simultaneous skill filters, free-text search, new skill catalogue data, following changes, analytics changes and closing shared Sprint 2 tasks. PR #91 remains independent.

## Capabilities

### New Capabilities

- `student-profile-discovery`: Investors browse saved student profiles, filter by skill and clear the filter.

### Modified Capabilities

None.

## Impact

- `accounts`: discovery form/query/view module, route and focused tests.
- Templates and existing styling: directory, filter, cards and investor navigation.
- Documentation and OpenSpec artifacts; no new dependencies or database changes.
- One PR for T37 (#69) and T38 (#70), referencing US012 (#50).
