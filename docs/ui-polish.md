# MVP visual polish

Refs #39. Change: `polish-mvp-ui`, based on main `ed85be2`, independently of PR #36.

## Review scope

A shared cobalt/navy/light presentation across discovery, authentication, publication/editing and detail. Existing routes, roles, validation, field order and business requirements remain authoritative. T18 and T19 are separate work.

Browser review uses Microsoft Edge in headless mode, a separate profile and a SQLite database under the ignored `.venv/ui-review/` directory. Review accounts and idea fixtures exist only in that database; the user's development database is not used.

## Baseline

Captured on 2026-10-30 at a 1440px viewport, with the existing Bootstrap 5.3.3 stylesheet loaded.

| Discovery | Login |
|---|---|
| ![Discovery before polish](ui-polish/before-discovery.png) | ![Login before polish](ui-polish/before-login.png) |

## Design and verification

- Shared design: system typography, cobalt actions, navy text, a light blue-gray canvas, white surfaces, consistent controls and visible focus. Navigation preserves the existing role-specific actions; a skip link goes directly to main content.
- Local CSS: Django findstatic resolves `css/app.css`; Edge loads both Bootstrap and the local stylesheet. Anonymous/authenticated navigation checks: 2 tests passed.
- Discovery: responsive 1/2/3-column cards, a dedicated filter surface, descriptive empty states, and the existing category/title/summary/detail links. All 15 HomePageTests/DiscoveryPageTemplateTests passed without changing their assertions.

![Discovery after polish](ui-polish/after-discovery.png)

- Forms: one shared field partial preserves labels, optional fields, help text and Django's error/help associations. Authentication widgets now use the same Bootstrap controls as idea forms. All 25 AuthenticationFlowTests/IdeaFormTests/RequireEssentialInformationTests/IdeaFormPageTests passed, including the existing wireframe field order.

| Login | Registration | Publication |
|---|---|---|
| ![Login after polish](ui-polish/after-login.png) | ![Registration after polish](ui-polish/after-signup.png) | ![Publication after polish](ui-polish/after-publication.png) |

- Detail/editing: a readable content surface with the full multiline description, category and existing permission-controlled actions. All 14 IdeaDetailPageTests/EditIdeaTests passed.

| Detail | Editing |
|---|---|
| ![Detail after polish](ui-polish/after-detail.png) | ![Editing after polish](ui-polish/after-edit.png) |

## Browser integration review

Edge checks passed on 2026-10-30:

- Discovery, detail, publication and editing at 360, 768 and 1440 CSS pixels; login/registration at the same widths. No horizontal document overflow. Mobile navigation expands/collapses.
- 200% zoom-equivalent reflow: a 720 CSS-pixel viewport at device scale factor 2, representing a 1440-pixel display. This verifies layout reflow, not browser toolbar zoom or a full accessibility audit.
- Keyboard Tab exposes the skip link and Enter focuses main content. Field focus has a visible ring; reduced-motion media disables card transitions.
- A missing title displays its field error with aria-invalid and retains entered description. Help references point to actual elements. Registration errors remain visible on mobile.
- Real student login -> publish -> category filter -> clear -> detail -> edit -> logout -> restricted edit prompts for login. An investor sees saved edits without publication/edit actions.
- An empty category shows its no-match message. Long unbroken titles/descriptions wrap without horizontal overflow.
- Bootstrap and the local stylesheet load successfully. The development database hash matches the pre-review baseline.

| Discovery on mobile | Registration on mobile | Validation on mobile |
|---|---|---|
| ![Mobile discovery](ui-polish/after-discovery-mobile.png) | ![Mobile registration](ui-polish/after-signup-mobile.png) | ![Mobile validation](ui-polish/after-errors-mobile.png) |

![Category without matching ideas](ui-polish/after-empty-state.png)

The no-publications state was also captured using the isolated database; its review records were restored afterward.

![No published ideas](ui-polish/after-no-publications.png)

## Independent PR #36 compatibility

In an isolated copy, the two PR #36 test files and its known one-line empty-signup-POST correction were applied over this layout. All **78 tests passed**. The correction exists only in that disposable compatibility copy: this branch does not change accounts/views.py, T17 documentation, or the T17 OpenSpec change. Its own suite remains the 70 tests integrated in main.

## Project checks

| Check | Actual result |
|---|---|
| `python manage.py test` | 70 tests passed; system checks found no issues. |
| `python manage.py makemigrations --check --dry-run` | No changes detected. |
| `openspec validate --all --strict` | 7 items passed, 0 failed; presentation-only skip_specs accepted. |
| `git diff --check` | Passed. |
| Static asset discovery | findstatic resolves css/app.css; the browser serves it successfully. |

No test assertions were weakened or changed; the existing tests pass with the new layout.

## Review and Definition of Done

Peer review and merge, the team's wireframe/UX review, shared deployment and Product Owner acceptance remain separate. This visual PR resolves only #39 after review and merge. It does not resolve PR #36's task, T18/T19 or story issues.

The pre-existing OpenSpec `rules.specs[0]` YAML mapping warning is unrelated to this change; shared workflow configuration remains unchanged.
