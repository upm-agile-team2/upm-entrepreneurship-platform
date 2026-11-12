# Student profile discovery - US012

T37 (#69) and T38 (#70) implement the three acceptance criteria of US012 (#50).

## T37: backend filtering

The directory population is saved StudentProfile records belonging to active student accounts. Empty or incomplete saved profiles are included; student accounts without a saved profile and profiles attached to inactive or investor accounts are excluded.

`accounts.discovery.StudentProfileFilterForm` validates one optional skill against the current catalogue. No selection means all skills. Invalid identifiers are field errors. A valid skill without matching eligible profiles produces an empty result.

`accounts.discovery.student_profiles` selects the related user, prefetches skills and sorts by case-insensitive student name, then user ID. Loading names and skills for all results uses two queries. The directory query does not record profile visits and needs no schema or data migration.

Database-backed coverage: `accounts.test_discovery.ProfileDiscoveryBackendTests`.

## T38: directory and filter interface

Investors open Students from the navigation, at `/accounts/students/` (`accounts:student_discovery`). The GET form accepts one catalogue skill, for example `/accounts/students/?skill=3`. Applying the filter preserves its selection; Clear filter opens the directory without parameters. The count reflects the displayed profiles.

Cards show student names, a short bio or incomplete-profile fallback, skill badges and View profile. They link to the existing investor profile route. They do not expose emails, account controls or raw portfolio/experience data. Anonymous users are asked to sign in; students are denied access.

A valid unused skill displays No matching profiles and keeps Clear filter available. An invalid identifier displays a field error and no results. An empty directory has its own message and a link to idea browsing. An empty skill catalogue retains the complete eligible directory and explains why no skills can be selected.

The page uses existing blue branding and Bootstrap filter controls, a responsive one/two/three-column grid, visible keyboard focus and wrapping content. Shared navigation can wrap at tablet widths. No custom JavaScript is needed.

The feedback Notifications navigation link is shown only to students, matching US008 (#46). Investor notification behavior is not added; notification storage and recipient isolation remain unchanged. The role-specific navigation test verifies Students for investors and Notifications for students.

## Acceptance coverage

All tests below are in `accounts.test_discovery`.

| US012 acceptance criterion | Coverage |
|---|---|
| Filter by skill | `ProfileDiscoveryBackendTests.test_skill_filter_matches_profiles_and_preserves_all_their_skills`; `ProfileDiscoveryAcceptanceTests.test_investor_filters_sees_no_matches_and_clears_the_filter` |
| Clear profile filters | `ProfileDiscoveryAcceptanceTests.test_investor_filters_sees_no_matches_and_clears_the_filter` follows the rendered Clear filter link and verifies the full list and cleared selection |
| No matching profiles | `ProfileDiscoveryPresentationTests.test_valid_filter_without_results_has_a_clear_explanation`; the acceptance journey |

The 23 focused tests also cover population boundaries, current skill edits, query count, roles, request methods, empty catalogue/directory, validation, accessible form labels, selected state, result counts, escaped content, card data and navigation visibility. `ProfileDiscoveryAcceptanceTests.test_opening_a_discovered_profile_records_a_visit_for_its_owner` verifies that opening a result records a visit visible to the owner; browsing and filtering do not add visits.

## Manual review

1. Start the app and sign in as an investor. Open Students from the navigation.
2. Check that only active students with saved profiles appear, including profiles with missing fields.
3. Select a skill shared by a subset of students and apply it. Check cards, count and preserved selection.
4. Select an unused catalogue skill, check the no-matches message, then use Clear filter to restore the full list.
5. Open a result, then sign in as its student owner and check the visit count.
6. Check keyboard navigation, long labels and widths around 360, 768 and 1440 pixels. Confirm the filter, cards and navigation stay within the viewport.

## Delivery and Definition of Done

This change starts from main and does not depend on PR #91. That separate PR supplies following and the improved profile editor; they are visible once that PR is integrated. This change adds no database migration and does not seed or rewrite local data.

One PR covers T37 (#69) and T38 (#70), referencing US012 (#50), with the requested navigation follow-up referencing US008 (#46). Peer review, broader device review, agreed-wireframe confirmation, main integration and Product Owner acceptance remain follow-up conditions. Shared Sprint 2 tasks are not closed automatically.

## Verification - 12 November 2026

- Focused discovery suite: 23 tests passed. Full branch suite: 179 tests passed.
- Django system checks passed; migration checks detected no model changes and no pending migrations. No migration is added by this change.
- Isolated integration with PR #91 at `aae0bf3`: merge completed without conflicts and all 219 combined tests passed. Registering the discovery route separately from following avoids overlapping route additions. Navigation, CSS, forms and the profile routes coexist in that rehearsal.
- Strict validation passed for `filter-student-profiles`. Global validation reports 14 passing items and two existing missing-delta failures, `seed-demo-ideas` and `prepare-sprint2-experiments`; neither is changed here.
- Working-tree and staged diff checks passed. Local credentials, databases and integration helpers remain excluded.
- Live HTTP checks confirmed the anonymous directory request reaches sign-in and the server serves the directory styles. All account and idea table rows were unchanged across these read-only checks. Existing local data remains intact.
- Rendered HTML coverage includes labels, error indication, filter selection, current navigation, card data, empty states and responsive grid classes. Local review accepted the discovery layout; the profile-detail JSON presentation remains covered by pending PR #91. Broader keyboard/mobile checks are documented above; no new automated browser review is claimed.
- After the navigation follow-up, all 23 focused tests passed both on this branch and in the combined PR #91 checkout, including visibility of Notifications only to students.
