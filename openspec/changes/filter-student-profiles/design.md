# Design

## Context

See proposal.md for motivation. Main has StudentProfile, its skills relation, investor profile viewing and ProfileVisit. The existing catalogue also represents expertise areas. PR #91 contains following and profile-entry improvements, remains under review, and is not a dependency of this change.

## Goals / Non-Goals

**Goals:** cover the three US012 acceptance criteria with an accessible server-rendered directory, bounded queries and stable navigation.

**Non-Goals:** no directory access for students or anonymous visitors, profile editing from cards, catalogue management or extra visit events.

## Decisions

### Discover saved profiles

Query StudentProfile linked to active student users. Include saved profiles with empty fields, but omit users without a saved profile. This is the user-approved population. Show public showcase fields and name, without email or account metadata.

### Filter by one validated catalogue selection

Use a ModelChoiceField with an optional skill and a GET parameter such as `?skill=3`. Empty selection means all profiles; a valid unused skill means no matches. Malformed, missing or excessively large identifiers show a field error and no results, rather than raising a server error or silently widening the search. Keep the selected option and expose a clear-filter link to the directory URL. Multiple criteria and free-text search would need additional product decisions and are excluded.

### Isolate discovery code

Put the form, eligible-profile query and view in a dedicated accounts discovery module, with focused tests in their own module. This limits overlap with PR #91. Reuse the existing Bootstrap form mixin, branding, filter components and profile-detail route. Add an investor-only Students navigation link independently of the student-only navigation block.

### Read profiles efficiently without recording visits

Select the user with each profile and prefetch skills. Sort by case-insensitive student name with user ID as a stable tie-breaker. Browsing or filtering only reads data. The existing investor profile route records visits when a result is opened; no new visit logic belongs in discovery.

### Use a compact responsive directory

Present a title, introduction, labelled skill selector, Apply filter and Clear filter controls, a result count and a one/two/three-column card grid. Cards show name, a short bio or incomplete-profile fallback, skill badges and View profile. Distinguish an empty directory from a valid filter with no matches and from an invalid selection. Use existing blue tokens, wrapping labels and keyboard-visible focus; accommodate the extra navigation link at tablet widths.

## Risks / Trade-offs

- Shared navigation changes in PR #91: keep edits separate and rehearse integration in an isolated checkout before publication.
- Empty catalogue: render All skills, retain the full eligible directory and explain that no skills are available yet.
- Long names and skill labels: allow wrapping and test rendered semantics; record browser verification limits honestly.
- Live profile edits can change matches between requests: every GET uses current saved skills.

## Migration Plan

No schema or data migration is needed. Existing accounts, profiles, follows and visits remain untouched by directory requests. One branch from main and two task commits will form one PR, closing only #69 and #70 and referencing #50. Peer review, agreed-wireframe confirmation and Product Owner acceptance remain follow-up conditions.
