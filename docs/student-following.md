# Student following - US011

Implements T35 (#67) and T36 (#68) for US011 (#49).

## T35: follow and unfollow

Investors open a student profile through the author's link on an idea. Follow adds that student to the signed-in investor's collection; Unfollow removes the relationship. The button reflects the current investor's state, including on profiles with missing information.

Follow links investor and student User accounts, so a StudentProfile record is not required. An additive migration creates the relationship table, timestamp, unique-pair constraint and self-follow constraint. Deleting either account removes its relationships. `Follow.clean()` validates roles, while request handlers enforce the current account roles explicitly; ordinary model `save()` does not automatically run `full_clean()`.

Both actions require POST, an investor session and CSRF protection. The investor comes from the session and the student from a student-only route lookup. Repeated follow/unfollow requests are safe. Submitted account identifiers and arbitrary redirect URLs are not accepted as ownership or navigation instructions.

Routes:

- `accounts:follow_student`: `/accounts/students/<student_id>/follow/`
- `accounts:unfollow_student`: `/accounts/students/<student_id>/unfollow/`
- Existing `accounts:investor_profile`: `/accounts/students/<student_id>/profile/`

Automated checks: `accounts.tests.FollowModelTests`, `accounts.tests.FollowActionTests` and `accounts.tests.FollowProfilePresentationTests`.

## T36: followed profiles

The investor-only Following navigation link opens `/accounts/following/` (`accounts:following`). The page shows only the current investor's students, most recently followed first, with profile links, available bio/skills and Unfollow forms. Missing profile information has a fallback. Removing a student from this page returns to the list, including its empty state after the last removal. The empty state links to idea browsing, where investors can discover authors and open their profiles.

The collection query selects related students/profiles and prefetches skills. Private account details such as student email addresses are not displayed. An investor's collection cannot be selected through a submitted investor identifier.

## Acceptance coverage

All test names below are in `accounts.tests`.

| US011 acceptance criterion | Django coverage |
|---|---|
| Follow a profile | `FollowingAcceptanceTests.test_investor_follows_lists_and_unfollows_from_student_profile`; `FollowActionTests.test_follow_uses_session_investor_and_route_student` |
| Unfollow a profile | `FollowingAcceptanceTests.test_investor_follows_lists_and_unfollows_from_student_profile`; `FollowingAcceptanceTests.test_unfollow_from_list_updates_collection_and_preserves_other_investors` |
| View followed profiles | `FollowingListTests.test_list_shows_only_current_investors_followed_students_and_profile_links`; both acceptance journeys |

Additional model, action and presentation tests cover duplicate/self-follow constraints, validated roles, account deletion, repeated submissions, CSRF rejection and successful protected forms, authentication, student restrictions, invalid targets, fixed redirects, investor isolation, incomplete profiles, stable ordering, empty states and escaped profile content.

## Manual review

1. Apply migrations with `python manage.py migrate` and start the app with `python manage.py runserver`.
2. Sign in as a student, publish an idea, and optionally add profile details through My profile.
3. Sign in as an investor, open the idea and select its author's name.
4. Select Follow. Check the success message and that the profile now offers Unfollow.
5. Open Following from the navigation. Check the student's name, available information and profile link.
6. Unfollow from the profile, then follow again and unfollow from the list. Removing the final student must show the empty state.
7. Repeat with a second investor: each account must see and manage only its own collection.
8. Check an incomplete profile, narrow/mobile widths and keyboard access to the navigation, profile link and follow controls.

Run the focused suite with:

```powershell
python manage.py test accounts.tests.FollowModelTests accounts.tests.FollowActionTests accounts.tests.FollowProfilePresentationTests accounts.tests.FollowingListTests accounts.tests.FollowingAcceptanceTests
```

## Verification and Definition of Done

Verified locally on 12 November 2026:

- Full Django suite: initially 163 tests passed, including 27 following tests; after the related profile-entry correction, 175 tests passed (see docs/profile-entries.md). Integration with the latest main now passes 196 tests, as detailed below.
- `python manage.py check`: no issues.
- `python manage.py makemigrations --check --dry-run`: no changes detected.
- `python manage.py migrate --check`: no pending migrations after applying `accounts.0007_follow`.
- `openspec validate follow-student-profiles --strict`: valid.
- `git diff --check`: clean.
- Local SQLite was backed up before migration and existing user/idea records were preserved. Review fixtures, databases and credentials are excluded from the implementation.
- A separate preview database passed 35 browser assertions plus a check for JavaScript runtime errors. Checked login restrictions, following through an idea author's profile, profile/list unfollow actions, persisted button state, two-investor isolation, student restrictions, empty/incomplete states, keyboard skip/follow controls and visible focus, mobile navigation, long names/skills, widths 360/768/1024/1440, and a 200% zoom-equivalent viewport. Desktop and mobile captures were visually inspected. Browser fixtures and screenshots stay under ignored `.venv/follow-review/`.

Global OpenSpec validation (`openspec validate --all --strict`) now reports 15 passing items and one pre-existing failure: `seed-demo-ideas` has no delta specs. The same failure was reproduced in a separate checkout without this change. Its tracked planning files were left unchanged.

## Integration with main after PRs #85, #87 and #90

Feedback, notifications and profile visit statistics are integrated with following and the readable profile editor. The investor profile records each visit and retains Follow/Unfollow controls; the owner's profile retains readable projects/experience and shows the visit count.

Both `0007_follow` and `0007_profile_visit` remain unchanged. The empty `0008_merge_follow_profile_visit` migration depends on both and reconciles the migration graph without changing either table's schema or rewriting their data.

Verified on 12 November 2026:

- Full Django suite: 196 tests passed, including 28 following tests, nine profile-visit tests and 12 profile-entry regression tests.
- `FollowingAcceptanceTests.test_following_and_profile_visits_work_together` covers visit recording alongside Follow/Unfollow controls, collection navigation, readable entries, private statistics and the owner's final count. Follow actions and collection navigation do not themselves add visits; opening the investor-facing profile does.
- Upgrade from an existing local database with `0007_follow`: backed up SQLite, applied `0007_profile_visit` and the merge migration, and verified that every existing user, idea, profile and follow row was unchanged.
- Upgrade from a main-only database with `0007_profile_visit`: an isolated in-memory database retained its users, profile content and existing visit after adding following and applying the merge migration. Both models could be used together, with no conflicting or pending migrations.
- Fresh-database migration coverage is included in the full Django suite. System checks and migration consistency checks passed.
- Strict validation passed for `follow-student-profiles`, `polish-profile-entries` and `profile-view-statistics`. The global validation result is recorded above.

Peer review, confirmation against the team's agreed wireframes, integration into main and Product Owner acceptance at Sprint Review remain external follow-up steps. T46 (#78), T47 (#79), T48 (#80) and US011 (#49) are not closed by this local implementation.
