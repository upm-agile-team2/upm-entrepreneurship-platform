# Tasks

Source: US030 (#101). T69 (#122) covers model/storage work and T70 (#123) covers the shared editor and detail-page badges. The option catalog, multiple support selection, and optional fields were confirmed by the user before implementation. Checkboxes record verified progress.

## 1. T69: Data model and existing projects

- [x] 1.1 Add the agreed stage/support choice catalogs and optional `development_stage` field. Add model tests for each valid stage, empty stage, and rejection of unknown stage values; confirm existing title, description, owner, and category behavior remains intact.
- [x] 1.2 Add `required_support` as an optional JSON list with independent defaults and model validation. Add tests for valid subsets, no support selections, independent empty lists, and rejection of unknown codes, duplicates, non-string entries, scalar values, dictionaries, and null.
- [x] 1.3 Generate an additive migration from the current ideas leaf. Add a migration test that creates a project before the migration and confirms its original data survives afterward with an empty stage and empty support list. Document the deployment migration command in the PR instructions.

## 2. T70: Creation and editing

- [x] 2.1 Extend `IdeaForm` with the optional stage select and support checkbox multi-choice field. Update the existing field-order expectation and add form tests for valid selections, invalid stage/support values, and empty inputs while continuing to exclude owner and system-managed fields.
- [x] 2.2 Render the controls on both creation and editing pages using existing styles and an accessible support fieldset. Add page tests for labels, option names, selected/checked saved values, inline errors, and preservation of submitted choices when the form is invalid.
- [x] 2.3 Add request tests for selecting a stage on creation and changing it on edit, saving multiple support needs, and explicitly clearing both fields. Reopen the editor and reload the database record to verify persistence for the select-stage and add-support acceptance criteria. Verify omitted support checkboxes clear the support list.
- [x] 2.4 Preserve the existing owner-only editing and student-only publishing rules. Run current access tests and add metadata submission checks showing another student or investor cannot change a project's values. Verify invalid metadata does not create a project or alter an existing one.

## 3. T70: Project needs on detail pages

- [x] 3.1 Add readable stage/support labels and Bootstrap badges to the detail template. Add tests where another user views a project and sees the saved stage plus all selected support labels; test stage-only, support-only, cleared, and legacy-empty records without empty badges or raw internal codes.
- [ ] 3.2 Manually check the create/edit/detail journey on desktop and a narrow viewport: stage single selection, multiple support checks, save/reload, invalid submission, changing and clearing selections, wrapped badges, and another user's read-only view. Record observations without claiming manual results from template tests alone.

## 4. Integration verification and completion

- [x] 4.1 Run `openspec validate project-stage-support --strict`, `openspec validate --all`, and `git diff --check`. This change's strict validation and diff check passed. Repository-wide validation was executed and reports 17 passing items and two pre-existing failures (`prepare-sprint2-experiments`, `seed-demo-ideas`), as documented in the design; the full-repository check is not passing.
- [x] 4.2 Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `python manage.py test`. System checks passed, no model drift was detected, and all 248 project tests passed.
- [ ] 4.3 Check the README Definition of Done: arrange teammate review, verify integrated-MVP behavior and agreement with the team's wireframes, and obtain Product Owner acceptance during Sprint Review. Record any pending items explicitly.

## Workflow follow-up

- Prepare one PR from `T69-T70-project-stage-support` to `main`, using `Closes #122`, `Closes #123`, and `Refs #101` for the user-confirmed task and parent-story references.
- Request review and move the task issues to In Review according to the README workflow.
- Archive this change after implementation, verification, and the team's required acceptance steps are complete.
