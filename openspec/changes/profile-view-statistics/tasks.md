# Tasks

## 1. Record visits (T41, #73; US019, #52)

- [x] 1.1 Add the `ProfileVisit` model and migration. Test that an investor opening a profile records a visit with the investor as visitor, also for students without a profile.
- [x] 1.2 Test that students viewing their own profile, other students and anonymous visitors do not record visits.

## 2. Show the statistics (T42, #74; US019, #52)

- [x] 2.1 Show the total number of visits on the student's own profile. Test the plural and singular messages and that only visits to that student are counted.
- [x] 2.2 Show "No visits have been recorded yet." when there are none. Test the zero state.
- [x] 2.3 Keep the statistics private to the owner. Test that investors do not see them.

## 3. Verification

- [x] 3.1 Run `python manage.py check`, `python manage.py makemigrations --check --dry-run` and `python manage.py test`, and check the Definition of Done in the README.
