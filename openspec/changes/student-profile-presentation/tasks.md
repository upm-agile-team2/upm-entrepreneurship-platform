# Tasks

## 1. Student profile presentation (T33, #65; US009, #47)

- [x] 1.1 Add a student-only read-only own-profile route and page using the current user's profile; include an edit link to the existing T32 endpoint. Test viewing saved bio, skills, projects, and experience, plus the no-profile state.
- [x] 1.2 Upgrade the T32 profile form scaffold into a clear Bootstrap editor using `StudentProfileForm` and the shared form partial. Test the field labels, JSON guidance, visible validation errors, and links to own-profile view.
- [x] 1.3 Add a student-only “My profile” navigation link and test that it appears for students but not investors or anonymous visitors.

## 2. Investor profile presentation (T34, #66; US010, #48)

- [x] 2.1 Add an investor-only read-only profile route. Test that anonymous users are redirected to login, students are forbidden, investors can access student profiles, and non-student/nonexistent IDs return 404.
- [x] 2.2 Link the student author's name on an idea detail page to the investor profile route for authenticated investors. Test link target and verify no investor-specific link is exposed to anonymous users or students.
- [x] 2.3 Display the student's available name, bio, skills, portfolio projects, and experience without exposing email or edit actions. Test each rendered value and privacy boundary.
- [x] 2.4 Test incomplete profiles: no StudentProfile row, empty bio, no skills, and empty project/experience lists render without errors and show clear empty states.

## 3. Verification

- [x] 3.1 Run focused account/idea profile tests, `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `python manage.py test`; validate this OpenSpec change and check the README Definition of Done. Do not change the T31 model or add a migration.
