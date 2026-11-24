# Proposal

## Why

US030 (#101) asks students to state their project's development stage and support needs so other users can understand where help is needed. T69 (#122) adds the data model, and T70 (#123) connects that data to the existing creation/edit forms and project detail page.

## What Changes

- Extend `Idea` with optional `development_stage` and `required_support` values, preserving existing projects.
- Offer a single development-stage selection and multiple support selections on both project creation and editing.
- Save, reload, update, and clear these values through the current owner-only form workflow, with server-side validation of allowed selections.
- Display the selected stage and support needs as readable badges on the existing project detail page. Hide unfilled information.
- Add a schema migration and model, form, request, and presentation tests mapped to the three acceptance criteria.

## Confirmed Product Decisions

The issue names the fields but does not specify option values or whether they are required. The user confirmed the following catalog and rules on 2026-11-24; these are agreed decisions for this proposal, not quotations from #101.

| Field | Options | Selection | Empty value |
| --- | --- | --- | --- |
| Development stage | Idea, Prototype, MVP, Launched, Growth | Single selection | Allowed |
| Required support | Funding, Technical support, Mentoring, Marketing, Team members | Multiple selections | Allowed |

Existing projects begin with no selected stage and no requested support. Both fields can be cleared after previously being filled in.

## Out of Scope

- Editing permission changes, new project routes, new user roles, or profile functionality.
- Automatic stage progression, custom/free-text options, discovery filters, or matching investors to needs.
- Actually sending collaborator requests, funding requests, notifications, or messages when a support type is selected.
- Attachments, image storage, and the pending T77/T78 social-link feature.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: add optional stage and support selections to project creation/editing and show the saved project needs on its detail page.

## Impact

- `ideas/models.py` and `ideas/migrations/`: define the two fields, their agreed choices, model validation, and defaults for existing rows.
- `ideas/forms.py`: expose a stage select and support multi-choice field with appropriate optional behavior and field errors.
- `ideas/views.py` and `templates/ideas/idea_form.html`: reuse the current create/edit endpoints and render the new controls accessibly.
- `templates/ideas/idea_detail.html`: show selected stage and support labels as Bootstrap badges.
- `ideas/tests.py`: cover storage, selection validation, create/edit persistence, permissions, detail badges, and empty/legacy data.
- No dependency on the unmerged T77/T78 branch and no new runtime package.

Refs #101 (US030), #122 (T69), and #123 (T70). Covers both tasks together on `T69-T70-project-stage-support`; the task issue numbers have been confirmed by the user.
