# Proposal

## Why

The initial shared visual polish is implemented in PR #40. The task owner now supplied the UPM ideaHub brand kit v1.1 and requested its application locally, including removal of the idea-initial squares, with a personal review before any PR update.

Refs #39. Existing acceptance sources: US013-US015 (#1-#3), US001-US004 (#4-#7).

## What Changes

- Introduce a local stylesheet with shared blue/light colors, typography, spacing, responsive surfaces, buttons, focus and feedback states.
- Improve the shared navigation and discovery header, filter, idea cards and empty states.
- Give login, signup, publication/editing and idea detail a consistent layout and clear hierarchy.
- Preserve real data, named routes, permissions, field order, validation and navigation behavior.
- Review before/after browser screenshots and responsive/error/role states; adapt existing presentation assertions only when markup changes.
- Adopt the supplied UPM ideaHub spelling, Ui vector marks, favicon and blue/charcoal/neutral tokens; keep reference-document instructions subordinate to the user's local-review and no-push boundary.
- Remove the initial squares and generic decorative artwork, simplify the card hierarchy and show the existing author's name/publication date where available.

Out of scope: new product features, business requirements, model changes, migrations, runtime dependencies, experiment materials (T18), deployment (T19), self-merging, or completing other issues. Keep PR #36 independent and check compatibility with its tests without incorporating its unreviewed application change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The accounts and ideas requirements remain unchanged. Presentation details are recorded in the design; this change declares `skip_specs: true` and creates no delta specs.

## Impact

- Six existing templates, `accounts/forms.py` for widget attributes, `config/settings.py` for local static discovery, and a new `static/css/app.css`.
- Focused presentation assertions in `ideas/tests.py` if required; existing behavioral tests remain authoritative.
- Review evidence in `docs/ui-polish.md` and screenshots.
- Supplied SVG/favicon assets under `static/brand/`, token CSS, shared outline icon partials and provenance in `docs/brand/README.md`.
- No external fonts or icon libraries, database changes, routes or additional runtime packages. Use the supplied Inter/system fallback stack without redistributing font files.
- The user completed local review and authorized committing, pushing and updating PR #40. Another team member's review and merge remain separate; do not change other issue states or deploy.
