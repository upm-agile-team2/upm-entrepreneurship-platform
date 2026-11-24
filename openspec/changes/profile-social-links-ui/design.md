# Design

## Context

See `proposal.md` for motivation and retrospective-documentation status. The branch already contains T77's `StudentProfile` URL fields, `StudentProfileForm` fields, migration, and backend tests. The editor uses `accounts:student_profile`, while `accounts:my_profile` and `accounts:investor_profile` share a profile-display context and template. Main specs currently cover authentication and ideas; general profile specs remain in earlier pending changes, so this change introduces the focused `profile-social-links` capability.

## Goals / Non-Goals

**Goals:** connect existing storage to ordinary profile pages, keep the editor's existing behavior, and make available external links recognizable and accessible.

**Non-Goals:** redefine validation rules, expand profile access permissions, or add a separate client application. The investor-facing page remains authenticated and investor-only; "public profile" means the existing viewer-facing profile, not anonymous access.

## Decisions

### Reuse the bound model form and shared field partial

The editor view supplies `social_media_fields` containing the four bound fields. The editor template renders them in a Social media fieldset through `includes/form_fields.html`, which already renders labels, optional markers, values, and inline validation errors. Persistence continues through the existing `form.is_valid()` and `form.save()` path. This avoids a second form or a new endpoint and keeps failed submissions available for correction.

### Prepare available links in the shared profile context

`_profile_display_context()` maps each platform to its stored URL and readable name. It skips blanks and URLs rejected by an HTTP/HTTPS `URLValidator`, then supplies `social_links` to the shared detail template. Preparing the list once avoids duplicating platform and availability checks across owner and investor pages. The extra display validation also handles records written through scripts that bypass model validation.

### Use inline icons with visible platform names

`social_icon.html` selects a bundled Bootstrap Icons SVG by platform. Visible platform names identify the destination, while decorative SVGs are hidden from assistive technology. Existing Bootstrap cards, buttons, spacing, and wrapping provide the layout without a new CSS library or client-side package. Compared with fetching icon fonts or images at runtime, the bundled SVGs remove an additional network dependency. Preserve the MIT notice in `docs/licenses/bootstrap-icons.txt`.

### Open external links without replacing the profile page

Each anchor uses the stored URL, `target="_blank"`, and `rel="noopener noreferrer"`. A visually hidden note announces the new-tab behavior. Normal Django autoescaping remains enabled. This is a presentation decision for the story's external-navigation criterion, rather than a new requirement that the external account exists.

## Risks / Trade-offs

- Platform URLs are optional and are not restricted to platform domains. An HTTP/HTTPS URL entered in the GitHub field receives the GitHub icon. This preserves T77's agreed validation scope; changing it needs a separate validation decision.
- Existing student-only editing and investor-only viewing limit the story to current supported profiles. Investor-owned profile editing and student-to-student browsing remain outside this change.
- Automated tests check generated links, targets, errors, and visibility but do not navigate third-party websites. Actual browser-click verification remains a manual acceptance step.
- The UI depends on T77, whose original PR has not merged. The `T77-T78-profile-social-media` branch contains both tasks for one PR to main; inspect the complete backend, migration, UI, tests, and documentation diff together. The older backend-only PR is superseded rather than merged separately.

## Migration Plan

T78 requires no database migration. Apply T77's `0009_add_profile_social_urls` migration before deploying the editor and profile templates. Deploy the view, templates, and license together. Reverting T78's presentation changes leaves T77's stored URLs intact.

## Verification Evidence

- The current implementation passed all 15 `StudentProfilePresentationTests`.
- The full project passed 239 Django tests, and the migration check reported `No changes detected`, before these documentation-only additions.
- User-provided browser screenshots show the editor's legal/invalid URL states and social icons on both the owner's and investor's views.
- Screenshots alone do not confirm an actual external-page click or Product Owner acceptance; these remain pending in `tasks.md`.
