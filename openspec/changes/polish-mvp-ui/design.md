# Design

## Context

See proposal.md for scope. The branch starts at main `ed85be2`, independently of PR #36. Bootstrap 5.3.3 is loaded from its existing CDN. IdeaForm already has Bootstrap widgets and per-field errors; authentication widgets are mostly unstyled. Staticfiles is installed with STATIC_ROOT, but there is no source static directory. Some existing tests match exact Bootstrap classes in HTML.

## Goals / Non-Goals

**Goals:** a consistent, readable and responsive presentation across every demo screen, while retaining all 21 existing behavior criteria and publication wireframe field order.

**Non-Goals:** changed authentication, new endpoints or data, extra JavaScript interactions, invented metrics, external fonts, or a build pipeline.

## Decisions

- Use a single local `static/css/app.css`, registered through STATICFILES_DIRS and loaded after Bootstrap. CSS custom properties define navy text, cobalt actions, a pale blue-gray canvas, white surfaces, spacing and focus. System fonts avoid a new network dependency. Prefer reusable components over scattered template styles.
- Give discovery a generous intro, compact filter panel and responsive 1/2/3-column cards. Cards show stored category/title/description only; preserve truncation and named detail URLs. Keep GET filtering and Clear filter behavior.
- Keep distinct visible no-publication and no-match messages, styled as intentional empty states. Avoid adding publishing links for anonymous visitors or investors.
- Use the same surface and field treatment for authentication and idea forms. Add widget CSS classes, invalid state and described-by associations without changing validation, required flags, field names or password help. Preserve title/description/category/Publish order and all error messages.
- Keep the detail title, full multiline description and category, with existing ownership-based edit visibility. No author/profile expansion is needed.
- Use semantic headings/labels, visible keyboard focus, text and borders in addition to color, long-word wrapping, and reduced-motion handling. Check widths 360/768/1440 and 200% zoom/reflow.
- Adapt exact-markup presentation assertions to verify semantic text, controls and destinations when classes change; retain behavioral assertions and existing test count. Add no tests for colors/shadows alone.
- Use an isolated local preview database for browser screenshots, leaving the user's development data unchanged. Screenshot fixtures are review tooling, not T18 sample-data deliverables. Include before/after images and actual check results in docs/ui-polish.md.
- Verify PR #36 compatibility in a temporary checkout by applying only its test changes; do not merge its pending runtime fix into this independent PR. Record any pre-existing difference (empty signup POST) separately.

## Risks / Trade-offs

- Existing Bootstrap CDN connectivity affects presentation -> verify it loads in the browser and keep the existing pinned version.
- Exact HTML assertions may fail after layout changes -> update their presentation expectations while retaining the behavior they protect.
- PR #36 is pending -> avoid accounts/views.py and its documentation, and run its test additions against this layout with the known pending empty-POST correction isolated during compatibility verification.
- Browser availability may vary -> discover an installed Chromium browser and use an isolated profile; report any unavailable visual checks honestly.
- The shared OpenSpec rules warning predates this task -> record it; do not alter shared workflow configuration.

## Migration Plan

No data migration or new runtime package. Serve local static assets with Django's existing staticfiles mechanism. Reverting the commit restores the original presentation. Another team member reviews and merges; archive this change afterward. T18/T19 and Product Owner acceptance remain separately tracked.
