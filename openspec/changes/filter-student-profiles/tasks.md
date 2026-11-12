# Tasks

## 1. T37: profile filtering backend

- [x] 1.1 Add the validated skill form and eligible-profile query, with database tests for filtering, saved/incomplete profiles, active student roles, empty selection, invalid identifiers, ordering and bounded related queries. Document the backend in docs/student-profile-discovery.md.

## 2. T38: discovery interface

- [x] 2.1 Add the investor-only GET view and route; verify authentication, role/method restrictions, validated query behavior and that directory requests do not record visits.
- [x] 2.2 Add the responsive directory, filter controls, count, navigation and profile cards; test selected/clear states, invalid values, empty directory/catalogue, no matches, public fields and escaped content.
- [x] 2.3 Add acceptance journeys for skill filtering, clearing and no matches, including opening a result through the existing profile route; document acceptance coverage and manual review steps.
- [x] 2.4 Show the feedback Notifications navigation link only to students, as requested after local review; verify role-specific navigation and preserve student notification behavior.

## 3. Integration and verification

- [x] 3.1 Run system/migration checks, OpenSpec validation, diff checks and the full Django suite; rehearse integration with PR #91 in an isolated checkout, verify local data is unchanged and record results and remaining Definition of Done conditions.

## Workflow follow-up

- Deliver one PR with the two task commits and the requested navigation follow-up, closing #69 and #70 and referencing #50 and #46.
- Keep shared Sprint 2 tasks and Product Owner acceptance open; archive after the applicable review requirements are met.
