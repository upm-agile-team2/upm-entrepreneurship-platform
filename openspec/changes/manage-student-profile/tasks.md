# Tasks

## 1. Profile form and validation

- [x] 1.1 Add `StudentProfileForm` in `accounts/forms.py` for bio, skills, portfolio projects, and experience; exclude user ownership from submitted fields and use only existing `Skill` records for optional selection. Treat POST as a complete submission: empty or omitted skills clear the selection. Test selecting existing skills, no choices with an empty catalogue, rejection of free-text skill values, and empty and omitted skill values clearing associations during update.
- [x] 1.2 Validate portfolio projects and experience as JSON arrays without constraining individual entries. Test separately that blank or omitted input becomes `[]`, explicit `[]` remains `[]`, and arbitrary valid JSON list items are preserved; for each field, test that malformed JSON and non-list top-level values (including `null`) are rejected without saving a profile.
- [x] 1.3 Verify through `StudentProfileForm.is_valid()` that the `StudentProfile.clean()` student-role rule runs for the view's student-bound form; a student passes and an investor fails, while the test documents that `save()` does not automatically call `full_clean()`.

## 2. Current-student profile workflow

- [x] 2.1 Add a named GET/POST route and view for the current student's profile. Require login, deny non-students, bind only to `request.user.student_profile` or an unsaved profile owned by `request.user`, and do not create a row on GET. Verify that GET retrieves existing field values and that a new GET leaves the profile count unchanged.
- [x] 2.2 On valid complete-form POST, create or update the same student's profile, save its skills relationship and JSON list values, and redirect to the profile route. Omitted JSON fields normalize to fresh empty lists; an omitted bio is cleared, and empty or omitted skills clear associations. Add view tests for create, retrieval of saved skills/projects in response context, update-in-place, omitted optional fields during update, and invalid submissions that do not persist changes.
- [x] 2.3 Add only a minimal unstyled template scaffold if required to render GET and invalid-POST responses; verify that the route renders without introducing T33's visual layout.
- [x] 2.4 Add access-control tests: anonymous users are redirected to login, investors are denied, and a student submitting another user's/profile identifier cannot change that other profile. Verify the user's own profile remains the only profile targeted by the route.

## 3. Integration verification

- [x] 3.1 Run focused accounts profile tests, `python manage.py check`, and `python manage.py test`; confirm the full suite passes and review the README Definition of Done for T32. Keep the T31 stacked dependency and T33 presentation handoff explicit; do not add a migration.
