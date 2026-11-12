# Design

## Context

See proposal.md. Portfolio and experience are existing JSON list fields accepting arbitrary list items. The view currently serializes each item again and the template prints it in a preformatted block. The StudentProfileForm's original JSON-list validation and ownership rules have regression coverage that must remain valid.

## Goals / Non-Goals

**Goals:** readable profile details and conventional editor controls; preserve saved values and metadata; require no schema conversion.

**Non-Goals:** redefining the stored schema, restricting historical arrays to new object shapes, changing roles or adding new profile features.

## Decisions

- Add shared entry adapters for display and editor initialization. Recognize existing title/name and role/position aliases, render available descriptions and supporting fields, and format other values as escaped readable text. Only valid HTTP/HTTPS project URLs become links. Do not mark stored content as safe HTML.
- Use Django formsets for ordinary project and experience fields. Projects expose title, description and optional link; experience exposes role, organization, period and description. Require a heading for new or edited normal entries. Keep one blank optional row for use without JavaScript. When JavaScript is available, hide unused blank rows until Add is selected, reuse a blank row before cloning another, and focus its first field. Saved rows display their entry headings so repeated field labels are not mistaken for duplicate data.
- Bind each initial form to its corresponding entry from the current student's profile, not an object identifier from POST. Preserve untouched originals exactly. For modified dictionaries, update only changed supported keys while retaining aliases and unknown metadata. Legacy non-text scalar/list entries remain readable, preservable and removable. Explicit DELETE controls remove entries.
- Use a hidden editor-mode marker to distinguish new formset submissions from the existing JSON POST contract. Validate both formsets and the parent profile form before saving any data. Serialize the validated list back into the existing form, keeping its JSON field contract and tests. Validate initial/total form counts to reject malformed or stale row submissions instead of silently truncating entries.
- Keep existing profile presentation and Following intact. Use shared, scoped entry-card styles and accessible labels/errors. Record this extra local-review correction separately from T35/T36.
- Use explicitly labelled block groups in place of nested native fieldsets/legends, constrain collections/rows/controls to their parent's width, and refresh the CSS/editor-script asset URLs. This removes dependence on native legend intrinsic sizing; local review in VS Code's embedded browser confirmed that the reported overflow is resolved.

## Risks / Trade-offs

- Historical arbitrary values or metadata: preserve originals unless the corresponding entry/field is explicitly changed or removed; regression-test mixed arrays and aliases.
- Invalid entry or management data: re-render both editor sections with field/non-form errors and keep the database unchanged.
- Long or untrusted content: wrap text, escape values, and validate outbound URL schemes.
- Multiple editors changing list length: reject an initial-form-count mismatch and ask the user to reload. Same-length concurrent edits follow the existing profile form's last-save behavior.

## Migration Plan

No migration or automatic data rewrite. Existing JSON fields remain unchanged. Reverting the interface also leaves stored arrays intact.
