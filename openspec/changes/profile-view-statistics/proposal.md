# Proposal

## Why

H3 says that at least 15% of investor visits will end with a student profile being opened. The platform does not record when an investor opens a profile, so neither students nor the team can see that traction. US019 (#52) asks for students to see how many times investors visited their profile. This change covers T41 (#73) and T42 (#74).

## What Changes

- Add a `ProfileVisit` record (student, visitor, date) and create one each time an investor opens a student's profile.
- Show the total number of investor visits on the student's own profile page, with a clear message when there are none yet.
- Register the visits in the admin so the team can read them during the H3 experiment (US023).

Out of scope: charts or visits per day, unique visitors, notifying students of visits, and showing statistics to investors.

Refs #73, #74; US019 (#52); depends on T34 (#66).

## Capabilities

### Modified Capabilities

- `student-profiles`: record investor visits and show the visit count to the profile owner.

## Impact

- `accounts/models.py` and migration `0007_profile_visit`: new `ProfileVisit` model.
- `accounts/views.py`: record the visit in the investor profile view and pass the count to the own-profile view.
- `templates/accounts/student_profile_detail.html`: visit statistics card for the profile owner.
- `accounts/admin.py`: read-only admin for visits.
- `accounts/tests.py`: tests for each US019 acceptance criterion and for which requests count as a visit.
