# Design

## Context

See `proposal.md` for the problem, scope, and user-confirmed choices. `Idea` currently stores title, description, category, owner, publication time, and a demo key. `IdeaForm` explicitly lists three fields and is shared by `publish_idea` and `edit_idea`. Publishing binds the owner from the request; editing checks ownership before binding the model form. Project details already use Bootstrap category badges and are viewable according to existing access rules.

The ideas migration leaf is currently `0006_notification`. The new branch is based on main and does not contain the pending social-link changes. This plan does not depend on those changes.

## Goals / Non-Goals

**Goals:** add validated, optional project metadata; preserve existing projects and the current permission checks; reuse the shared creation/editing flow; expose saved labels clearly on project details.

**Non-Goals:** build new routes, APIs, user roles, taxonomy administration, matching, discovery filters, or automatic actions associated with selecting support needs.

## Decisions

### Fixed stage and support catalogs

Define two named choice catalogs on `Idea`, using translatable labels and stable stored codes:

| Development stage code | Label |
| --- | --- |
| `idea` | Idea |
| `prototype` | Prototype |
| `mvp` | MVP |
| `launched` | Launched |
| `growth` | Growth |

| Support code | Label |
| --- | --- |
| `funding` | Funding |
| `technical_support` | Technical support |
| `mentoring` | Mentoring |
| `marketing` | Marketing |
| `team_members` | Team members |

These values were confirmed by the user because #101 does not enumerate them. Separate code values from labels so templates do not display internal identifiers and future label changes do not require rewriting stored data.

### Store one stage and a small list of support codes

Use an optional `CharField` with stage choices, `max_length=20`, `blank=True`, and `default=""` for `development_stage`. Use `JSONField(blank=True, default=list)` for `required_support`. The callable default gives each project its own list.

A JSON list fits the fixed five-option support catalog and both supported databases without adding an administrative model and join table. Compared with a comma-separated string, it keeps selections explicit. A separate support model would be appropriate if users could create options or catalog entries needed their own metadata, which is outside scope.

Validate support list shape and contents in model validation: it must be a list of known string codes with no duplicates. Reject scalar values, dictionaries, null, unknown codes, and repeated values. Explicitly check empty invalid shapes in `Idea.clean()` rather than relying only on JSON field validators, because field-level blank handling can skip empty values. Report errors against `required_support`; use stage field choices to reject unknown stages. Scripts that bypass a model form must call `full_clean()` when validation is required; do not change the existing `save()` contract.

### Use a stage select and support checkboxes in the shared form

Expose both fields in `IdeaForm`. Derive the stage select from model choices and provide a blank "Not specified" choice. Declare support as a non-required `MultipleChoiceField` with `CheckboxSelectMultiple`, using the model's support catalog and passing a list of codes to the model.

Keep the existing first three fields in order and append the two metadata fields. Update the existing exact field-order test to reflect the accepted extension while continuing to exclude owner, publication time, and demo keys.

An empty checkbox selection must save `[]`, including when the browser omits the checkbox key. Do not interpret deselecting all support checkboxes as preserving old selections. An explicitly blank stage clears the stage. Existing create/edit submissions remain valid when the new optional fields are absent; no new required-field errors are introduced.

Use the existing generic field partial for ordinary inputs and render the support choices in a labeled fieldset with per-option labels, appropriate checkbox styling, and field errors. The view contexts can provide an ordered list of ordinary bound fields, following the existing profile-editor pattern, while the support field is rendered separately. This avoids treating a checkbox group as a text input or changing the shared partial for unrelated forms. Preserve submitted selections and values when validation fails.

### Retain existing endpoints and permissions

Continue saving through the current `IdeaForm` paths in `publish_idea` and `edit_idea`. The create view still supplies the owner; the edit view still checks that the authenticated student owns the project. Preserve the existing success redirects and messages. Tests must exercise the real endpoints, including invalid metadata and attempts by another student or an investor to edit a project.

### Display labels as independent badge groups

Render the selected stage through its choice label and support selections through a model-level display helper that maps valid stored codes to labels in catalog order. Show a labeled Development stage badge and a labeled Support needed group in the project-detail header using the existing Bootstrap badge system. Let groups wrap on narrow screens.

Render a group only when it has a value, and render neither when both fields are empty. Keep existing category, title, description, author, actions, and feedback behavior. Keep normal template escaping and existing detail-page access rules. No new client-side JavaScript or external icon package is needed.

## Risks / Trade-offs

- JSON storage does not provide relational constraints for support types. Mitigate with model/form validation and tests for invalid shapes, values, and duplicates.
- Optional fields can be missing from old fixtures, demo data, and existing test submissions. Mitigate with empty defaults and regression tests; do not invent a stage for existing projects.
- New checkboxes need clear group labeling and appropriate error styling. Mitigate with fieldsets and tests for checked values, retained invalid submissions, and visible errors; inspect desktop and narrow-screen rendering manually.
- The fixed catalogs may later need team-wide revision. Record the confirmed values in this proposal; changing the catalog is a separate product decision and may require data handling.
- Other branches may introduce new ideas migrations before merge. Generate against the current leaf at implementation time and reconcile migration dependencies when updating from main.

## Migration Plan

Generate an additive ideas migration from the current leaf. Existing rows receive an empty stage and an empty support list; preserve all current project data and ownership. Verify the transition using a migration test that seeds a project before the new migration and reads it afterward. Apply normal deployment migrations before serving code that reads the new fields.

Deployment instruction to include in the PR: run `python manage.py migrate` to apply `ideas.0007_add_project_stage_support` before testing the new controls. The migration has been generated and applied successfully in the developer's local environment; the existing-data transition is verified separately by `ProjectStageSupportMigrationTests`.

Reverting this feature's schema migration drops the two new fields and their contents; retain a backup if their values need preserving. No migration or database mutation is performed while writing this proposal.

## Issue References

- The user confirmed T69 is #122 and T70 is #123. US030 (#101) is the parent story. The PR should close the two task issues and reference the parent story.

## Planning Validation Baseline

The proposal passes `openspec validate project-stage-support --strict`. Repository-wide validation currently reports 17 passing items and two failures: the pre-existing `prepare-sprint2-experiments` and `seed-demo-ideas` changes declare no specification changes but lack the explicit metadata required by OpenSpec 2.1.1. Their compatibility fixes are in the separate pending T77/T78 PR and are not copied into this independent feature branch. Track these baseline failures separately from this proposal's validity and recheck against updated main before the final PR.

## Implementation Verification

- All 248 project tests passed after implementation, including migration preservation, model validation, optional form selections, selection clearing, page rendering, read-only detail access, and unauthorized/invalid submissions.
- The focused request/access/edit check passed all 15 tests. The detail-page group passed all 13 tests.
- `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `git diff --check` passed. No additional migration is required beyond `0007_add_project_stage_support`.
- Desktop screenshots show stage choices, multiple support selections, persisted edit values, and updated detail badges. An investor screenshot shows MVP and Technical support with no edit action. These observations verify desktop display and the visible permission boundary.
- Explicit browser clearing/error checks and a narrow-viewport check remain part of manual acceptance; template and request tests do not establish their visual results. Team review, integrated-environment acceptance, and Product Owner acceptance remain pending.
