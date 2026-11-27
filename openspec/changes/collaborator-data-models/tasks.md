# Tasks

This checklist covers the T60 (#113) and T61 (#114) model stage. All T60–T65 stages share `T60-T65-collaborator-requests` and one final PR, with separate commits and tests per stage. US0027 (#98) acceptance coverage is split: participant validation provides the data foundation for selecting another student; request persistence and receiver queries provide the data foundation for sending/receiving; uniqueness directly covers duplicate prevention. Browser selection, authenticated sending, delivery presentation, and request management require T62–T65 and remain explicitly incomplete.

## 1. Collaboration models and migration

- [x] 1.1 Add `Collaborator`, `CollaboratorRequest`, their foreign keys and timestamps, request status choices/default, and the explicit `Idea.collaborators` through relationship; verify `python manage.py check` reports no issues and reverse relation names match the design.
- [x] 1.2 Add membership/request uniqueness, request status and non-self database checks, and model validation for student roles and idea ownership, including missing/nonexistent foreign keys; verify validation through the focused tests in 1.4 and 1.5.
- [x] 1.3 Generate and apply an additive `ideas` migration from the current leaf; inspect its operations to confirm it creates only the intended tables/relationship/constraints, then verify `python manage.py makemigrations --check --dry-run` reports no changes.
- [x] 1.4 Add `ideas.tests.CollaboratorModelTests` for saved IDs/timestamps, project/student relationship queries, duplicate memberships at validation and database boundaries, invalid roles, and project-owner membership rejection; run that class successfully.
- [x] 1.5 Add `ideas.tests.CollaboratorRequestModelTests` for persistence, Pending default, supported/unsupported statuses, sender/receiver queries, valid owner-to-student participants, invalid roles/ownership/self-invitations, and incomplete foreign keys; verify no automatic membership side effect and run that class successfully.
- [x] 1.6 Extend the focused tests to reject duplicate requests with each existing status, including a direct database insert, and permit different idea/receiver pairs; also test deletion cascades and run both model test classes successfully.
- [x] 1.7 Add `ideas.test_collaborator_models_migration` using the test database to upgrade existing idea/user data from the previous schema and verify original fields are preserved with empty collaboration relations; restore the latest schema after the test and run the migration test successfully.
- [x] 1.8 Reconcile proposal/spec/design with the implemented models and record focused-test and migration results in this change; verify the documented statuses, duplicate rule, and limitations agree with code, and keep later workflows explicitly out of scope.

## 2. Integration and delivery checks

- [x] 2.1 Run `openspec validate collaborator-data-models --strict` and `openspec validate --all`; verify this change passes and distinguish pre-existing repository validation failures from regressions. Run `git diff --check` and inspect the diff for unrelated changes.
- [x] 2.2 Run `python manage.py test` and verify the full Django suite passes. Review the README Definition of Done, record which model-task checks are satisfied, and leave team review, integrated workflow/UI acceptance, and Product Owner acceptance pending rather than claiming US0027 is complete.

## Workflow follow-up

- After all three stages are implemented and verified, open one T60–T65 pull request to `main`. Include `Closes #113`, `Closes #114`, and the confirmed references for the remaining completed tasks, with `Refs #98`; obtain another team member's review according to the README.
- Reconcile migration branches with the latest main before merging if another `ideas` migration has landed.
- Continue on the same branch with T62–T63 and T64–T65 planning and implementation stages, including their Django endpoint/template tests and manual acceptance checks. Review their complete requirements before implementation and student-to-student profile access when planning the selection entry point. No intermediate PR or merge is required.
- Archive this change after its implementation and the applicable project review requirements are satisfied.
