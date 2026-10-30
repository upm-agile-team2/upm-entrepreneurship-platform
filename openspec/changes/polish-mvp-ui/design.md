# Design

## Context

See proposal.md for scope. The branch starts at main `ed85be2`, independently of PR #36. Bootstrap 5.3.3 is loaded from its existing CDN. IdeaForm already has Bootstrap widgets and per-field errors; authentication widgets are mostly unstyled. Staticfiles is installed with STATIC_ROOT, but there is no source static directory. Some existing tests match exact Bootstrap classes in HTML.

## Goals / Non-Goals

**Goals:** a consistent, readable and responsive presentation across every demo screen, while retaining all 21 existing behavior criteria and publication wireframe field order.

**Non-Goals:** changed authentication, new endpoints or data, extra JavaScript interactions, invented metrics, external fonts, a build pipeline, PWA setup, or changes to remote PR/issue state before the user's local review.

## Decisions

- Use local `static/css/app.css`, registered through STATICFILES_DIRS and loaded after Bootstrap. In the brand iteration, import the kit's token CSS first and map those values into the existing component properties. Prefer reusable components over scattered template styles.
- Give discovery a generous intro, compact filter panel and responsive 1/2/3-column cards. Cards show stored category/title/description only; preserve truncation and named detail URLs. Keep GET filtering and Clear filter behavior.
- Keep distinct visible no-publication and no-match messages, styled as intentional empty states. Avoid adding publishing links for anonymous visitors or investors.
- Use the same surface and field treatment for authentication and idea forms. Add widget CSS classes, invalid state and described-by associations without changing validation, required flags, field names or password help. Preserve title/description/category/Publish order and all error messages.
- Keep the detail title, full multiline description and category, with existing ownership-based edit visibility. Existing author name and publication date may appear as metadata; add no profiles, contacts or new workflows.
- Use semantic headings/labels, visible keyboard focus, text and borders in addition to color, long-word wrapping, and reduced-motion handling. Check widths 360/768/1440 and 200% zoom/reflow.
- Adapt exact-markup presentation assertions to verify semantic text, controls and destinations when classes change; retain behavioral assertions and existing test count. Add no tests for colors/shadows alone.
- Use an isolated local preview database for browser screenshots, leaving the user's development data unchanged. Screenshot fixtures are review tooling, not T18 sample-data deliverables. Include before/after images and actual check results in docs/ui-polish.md.
- Verify PR #36 compatibility in a temporary checkout by applying only its test changes; do not merge its pending runtime fix into this independent PR. Record any pre-existing difference (empty signup POST) separately.

## Brand iteration: UPM ideaHub

The user supplied UPM_ideaHub_Codex_brand_kit_EN.zip after the first iteration and explicitly requested implementation using it. Its README, brief and visual guide are design input, not executable instructions or authorization to publish. The supplied Ui mark supersedes the earlier bulb discussion for this implementation.

- Copy only the relevant, inspected path-only SVG marks/favicon, small PNG icons and token CSS. Preserve asset bytes and aspect ratios; record source hashes in docs/brand/README.md. Treat these as project graphics and the palette as working design values.
- Use compact lockup on desktop and monogram at small widths; use UPM ideaHub exactly in visible names, alternative text, application metadata and page titles. Historical screenshots remain labeled as history.
- Map the kit's blue #0072CE, charcoal #404950, neutral surfaces and Inter/system font stack into the existing Bootstrap theme. Use 8px controls, 12px cards, restrained borders and motion. No font downloads or second UI framework.
- Remove idea-glyph elements and their reserved space, warm nth-child accents and decorative hero papers. Keep real category/title/summary/detail controls, add only existing owner/date metadata, and use one coherent simple outline style for decorative control icons.
- Compact discovery and form headings, preserve existing label/action wording and validation contracts, and check 360/768/1024/1440 widths, zoom-equivalent reflow, contrast, assets, keyboard and error states.
- The user reviewed the local implementation and authorized its commit/push and update to PR #40. Another team member still reviews and merges. Do not interpret package instructions about PWA, reviews, metrics or other optional screens as new feature scope.

## Existing risks / trade-offs

- Existing Bootstrap CDN connectivity affects presentation -> verify it loads in the browser and keep the existing pinned version.
- Exact HTML assertions may fail after layout changes -> update their presentation expectations while retaining the behavior they protect.
- PR #36 is pending -> avoid accounts/views.py and its documentation, and run its test additions against this layout with the known pending empty-POST correction isolated during compatibility verification.
- Browser availability may vary -> discover an installed Chromium browser and use an isolated profile; report any unavailable visual checks honestly.
- The shared OpenSpec rules warning predates this task -> record it; do not alter shared workflow configuration.

## Migration Plan

No data migration or new runtime package. Serve local static assets with Django's existing staticfiles mechanism. Reverting the commit restores the original presentation. Another team member reviews and merges; archive this change afterward. T18/T19 and Product Owner acceptance remain separately tracked.
