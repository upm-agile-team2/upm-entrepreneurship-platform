# UPM ideaHub visual review

Refs #39. Change: `polish-mvp-ui`, based on main `ed85be2`, independently of PR #36.

## UPM ideaHub brand iteration

The user supplied the UPM ideaHub brand kit v1.1, reviewed its local implementation and authorized committing and updating PR #40. The sections below labeled first iteration preserve the earlier visual baseline.

- Exact UPM ideaHub naming in application metadata, page titles, logo alternative text and footer.
- Original compact SVG on desktop, Ui monogram on mobile, and the kit's SVG/PNG favicon. [Asset provenance and checksums](brand/README.md).
- Supplied token CSS mapped into the existing theme: blue #0072CE, charcoal, neutral surfaces, restrained 8px controls and 12px cards. The Inter/system font stack is used without downloading fonts.
- Idea-initial squares, their reserved space, warm accent squares and decorative hero papers removed. Cards prioritize category/title/summary and existing author/date metadata. The reading and form layouts use the same visual system.
- Existing features only. The kit's optional PWA, reviews, insights, loading workflows and other example screens were not interpreted as feature requests.
- The wireframe-order test now examines main content, so the document's description metadata cannot be mistaken for the description form field. All order assertions remain in place; 27 discovery/detail/form tests passed.

### Reviewed screenshots

| Desktop | Tablet | Mobile |
|---|---|---|
| ![UPM ideaHub discovery on desktop](ui-polish/ideahub-discovery-desktop.png) | ![UPM ideaHub discovery on tablet](ui-polish/ideahub-discovery-tablet.png) | ![UPM ideaHub discovery on mobile](ui-polish/ideahub-discovery-mobile.png) |

| Login | Registration | Publication |
|---|---|---|
| ![UPM ideaHub login](ui-polish/ideahub-login.png) | ![UPM ideaHub registration](ui-polish/ideahub-signup.png) | ![UPM ideaHub publication](ui-polish/ideahub-publication.png) |

| Detail | Editing | Mobile validation |
|---|---|---|
| ![UPM ideaHub detail](ui-polish/ideahub-detail.png) | ![UPM ideaHub editing](ui-polish/ideahub-edit.png) | ![UPM ideaHub validation](ui-polish/ideahub-errors-mobile.png) |

| Empty category | No publications |
|---|---|
| ![UPM ideaHub no matching ideas](ui-polish/ideahub-empty-state.png) | ![UPM ideaHub without publications](ui-polish/ideahub-no-publications.png) |

### Current verification (2026-10-30)

- Full branch suite: **70 tests passed**, system checks clean. Isolated PR #36 compatibility: **78 tests passed**, preserving this branch's scoped wireframe assertion and applying the pending signup fix only in the disposable copy.
- Browser journey passed at **360/768/1024/1440 CSS px**, including publication, filtering/clearing, detail, editing, logout, investor restrictions, registration/field errors and empty states. No horizontal overflow; very long unbroken titles, descriptions, author names and categories were checked.
- Compact and mobile SVG variants load at their intended aspect ratios and at least 24px high; exact name checked in titles, application metadata and image alt text. Favicon and styles are local static assets.
- Keyboard skip link/focus and reduced motion pass. 200% zoom-equivalent reflow was checked at 720 CSS px/device scale 2; this is not a browser-toolbar zoom or complete accessibility audit.
- Contrast checks: white on brand blue **4.89:1**, brand blue on canvas **4.66:1**, secondary text on canvas **5.60:1**, control borders on white **3.19:1**. Input/secondary-control borders are deliberately stronger than decorative card borders.
- No migrations needed; strict OpenSpec validation **7 passed, 0 failed**; git diff --check passed. Source assets match the supplied archive byte-for-byte.
- Local review was completed before the user authorized publication in the existing PR #40. Peer review and merge by another team member remain pending; no deployment is included.

## Review scope

A shared blue/charcoal/neutral presentation across discovery, authentication, publication/editing and detail. Existing routes, roles, validation, field order and business requirements remain authoritative. T18 and T19 are separate work.

Browser review uses Microsoft Edge in headless mode, a separate profile and a SQLite database under the ignored `.venv/ui-review/` directory. Review accounts and idea fixtures exist only in that database; the user's development database is not used.

## First-iteration baseline

Captured on 2026-10-30 at a 1440px viewport, with the existing Bootstrap 5.3.3 stylesheet loaded.

| Discovery | Login |
|---|---|
| ![Discovery before polish](ui-polish/before-discovery.png) | ![Login before polish](ui-polish/before-login.png) |

## First-iteration design and verification

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

## First-iteration browser integration review

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

## First-iteration independent PR #36 compatibility

In an isolated copy, the two PR #36 test files and its known one-line empty-signup-POST correction were applied over this layout. All **78 tests passed**. The correction exists only in that disposable compatibility copy: this branch does not change accounts/views.py, T17 documentation, or the T17 OpenSpec change. Its own suite remains the 70 tests integrated in main.

## First-iteration project checks

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
