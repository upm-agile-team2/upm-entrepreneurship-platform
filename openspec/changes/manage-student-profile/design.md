# Design

## Context

See proposal.md for motivation and the spec delta for required behavior. T31 supplies `StudentProfile` and `Skill` in `accounts/models.py`. The accounts app currently has signup/login/logout views, forms, and routes, but no profile workflow or account templates beyond registration pages. Existing protected idea views use `login_required` and raise `PermissionDenied` for non-students; the idea edit view loads the object and checks the current user's ownership rather than trusting submitted owner data.

The three spec requirements map to US009's create, display-skills-and-projects, and edit-own-profile acceptance criteria. T32 also handles the `experience` field because it exists in T31's model, but experience handling and JSON input validation are implementation scope, not additional US009 acceptance criteria.

## Goals / Non-Goals

**Goals:**
- Persist a student's profile details through Django form and view conventions.
- Retrieve the current student's existing profile for editing and keep create/update scoped to that student.
- Validate JSON list fields while leaving list item structure undefined.

**Non-Goals:**
- Define project or experience item schemas or create related models.
- Let students create arbitrary `Skill` catalog records through this form.
- Provide investor access, a public profile URL, or profile discovery/filtering.
- Implement T33's designed editor screen or profile-view layout.

## Decisions

- Add a `StudentProfileForm` `ModelForm` for `bio`, `skills`, `portfolio_projects`, and `experience`; exclude `user`. Bind the form only to an instance selected from `request.user`, so submitted data cannot choose or transfer profile ownership. `ModelForm.is_valid()` invokes model validation, including `StudentProfile.clean()`; do not rely on `save()` to call `full_clean()`.
- Use a `ModelMultipleChoiceField` backed only by existing `Skill` rows. Students can select existing skills, but cannot enter free-text skills or create catalogue rows in T32. The T31 admin registration is the catalogue-management path. An empty catalogue means there are no selectable skills; T32 must not add seed data.
- Treat every profile POST as a complete form submission, not a partial update. An omitted optional `bio` is cleared to its empty value. Blank or omitted `portfolio_projects` and `experience` are normalized independently to fresh empty lists (`[]`). Empty or omitted `skills` means no selected skills and clears existing associations. The GET form must therefore be populated from the current profile so a normal submission retains values the student has not changed. Tests must cover omitted and explicitly empty skill selections and omitted JSON inputs during an update.
- Treat project and experience form values as JSON lists, without imposing a schema on individual entries. Django's `forms.JSONField.to_python()` returns `None` for raw empty input by default. Use a small field subclass that intercepts raw empty input before calling the parent parser and returns a fresh `[]`; parse non-empty input normally and reject decoded non-list values, including JSON `null`. Keep explicit `[]` as an empty list, accept any valid JSON list items unchanged, and reject malformed JSON.
- Add one current-user profile route (proposed name `accounts:student_profile`) for GET and POST. Require login with the existing accounts login URL and reject non-students using `PermissionDenied`, matching the ideas app. On GET, retrieve `request.user.student_profile` when present; otherwise bind the form to an unsaved `StudentProfile(user=request.user)`. This populates existing values without creating a database row for a new profile. On valid POST, save the same instance and its many-to-many skills, then redirect to the profile route. Do not accept a profile/user id in the URL or posted form.
- The server-rendered route may need a minimal functional template for GET and invalid-POST responses. If a template is needed in T32, keep it unstyled and limited to rendering the form; T32 does not implement the final editor or profile-view layout. T33 owns that layout. Do no wireframe or visual redesign work in T32.
- Do not create or alter migrations. The model schema and migration belong to T31; this change assumes the stacked T31 base is present.

## Risks / Trade-offs

- [There may be no `Skill` rows to select] → The form only selects existing admin-managed rows; an empty catalogue has no choices. Do not add free-text creation or seed data in T32.
- [An optional `forms.JSONField` normally maps blank input to `None`] → Normalize blank input to `[]` before saving, and reject decoded non-list values, so form behavior matches T31's non-nullable list fields.
- [The JSON editor exposes serialized arrays] → Validate only the top-level list and preserve arbitrary entries; T33 may decide how to present inputs without imposing an item schema.
- [T32 depends on T31 and T33 integration] → Apply T32 on the T31 stacked branch. The minimal template scaffold keeps backend views testable; T33 owns its final appearance and profile-view layout.
- [Model role validation runs only during explicit validation] → `ModelForm.is_valid()` invokes model validation in this workflow. Any alternate save path must call `full_clean()` or otherwise enforce the student role.

## Migration Plan

No migration is needed. T32 uses the T31 model and migration and must not duplicate or modify them.

## Review Items Before Implementation

- The issues do not specify an initial Skill catalogue or student-created skill names. This design recommends that students select existing admin-managed skills; an empty catalogue yields no choices.
- Confirm that T32 may include a minimal functional template scaffold if needed for server-rendered view tests, with T33 owning the final editor and profile-view layout.
- The proposed route is current-student-only. Investor-facing profile access remains explicitly out of scope for T32.
