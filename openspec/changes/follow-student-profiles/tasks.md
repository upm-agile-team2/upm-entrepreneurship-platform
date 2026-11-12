# Tasks

## 1. T35 - Follow data and actions

- [x] 1.1 Add Follow and its additive migration; verify role validation, duplicate/self-follow constraints and account-deletion behavior with model tests.
- [x] 1.2 Implement investor-only follow/unfollow POST actions and fixed redirects; verify persistence, repeated submissions, target validation, authentication, CSRF and ownership isolation with workflow tests.
- [x] 1.3 Add follow-state context and Follow/Unfollow controls to existing student profiles; verify state changes and incomplete-profile rendering with presentation tests, and document T35 behavior in docs/student-following.md.

## 2. T36 - Followed profiles

- [x] 2.1 Add the current investor's followed-profile query, responsive list, empty state and navigation; verify profile links, ordering, available data and access isolation with presentation tests.
- [x] 2.2 Add an acceptance journey covering follow, list and unfollow, including removal from the list; verify all three US011 acceptance criteria and document their test mapping and manual steps in docs/student-following.md.

## 3. Integration and local review

- [x] 3.1 Back up SQLite, apply the additive migration and verify existing data counts; manually check follow/unfollow, the list, empty/incomplete states and keyboard/mobile layouts in a separate preview database, recording results in docs/student-following.md.
- [x] 3.2 Run Django system and migration checks, OpenSpec strict validation, git diff --check and the full python manage.py test suite; record results and check the Definition of Done, explicitly leaving peer review, agreed-wireframe confirmation and Product Owner acceptance pending.
- [x] 3.3 Integrate main after PRs #85, #87 and #90: preserve following, profile editing and visit statistics; reconcile the two accounts migrations; verify both upgrade paths and the combined acceptance journey; prepare updated validation records for PR #91.

## Workflow follow-up

- Local review is complete; publish one PR for T35 (#67) and T36 (#68) for peer review.
- Reference US011 (#49) without closing the story or shared Sprint 2 tasks automatically.
- Archive this OpenSpec change after the applicable review requirements are satisfied.
