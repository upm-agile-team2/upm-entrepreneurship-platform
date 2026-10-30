# Tasks

Refs #24 (T17). Tasks 1-3 preserve the completed authentication block. On 2026-10-30 the task owner requested full T17 completion; section 4 extends verification to all 21 criteria of US013-US015 (#1-#3) and US001-US004 (#4-#7).

Commands below assume the project virtual environment is active. On Windows, use `.\.venv\Scripts\python.exe` in place of `python` when needed.

## 1. US014: Sign-in and access to an account-required feature

- [x] 1.1 Add `AuthenticatedFeatureJourneyTests` to `accounts/tests.py`, using `TestCase`, a student fixture, and `override_settings(ALLOW_ANONYMOUS_ACCESS=True)`. Add `test_login_prompt_allows_student_to_access_publish_form`: request `ideas:publish` anonymously, follow its actual login prompt URL, submit valid credentials through that URL, and verify the same client is authenticated and can access the publication form. Verify with `python manage.py test accounts.tests.AuthenticatedFeatureJourneyTests.test_login_prompt_allows_student_to_access_publish_form`.
- [x] 1.2 Add `test_invalid_credentials_keep_publish_form_restricted` using an existing account and an incorrect password through the actual login prompt; assert an error is displayed, the client remains unauthenticated, a subsequent protected GET still prompts for login, and no idea is created. Verify with `python manage.py test accounts.tests.AuthenticatedFeatureJourneyTests.test_invalid_credentials_keep_publish_form_restricted`.
- [x] 1.3 Create `docs/acceptance-coverage.md` with the three US014 criteria and exact references to their existing and new tests. Record the active configuration and the request/session scope of the checks; verify each referenced test method exists and the targeted class passes with `python manage.py test accounts.tests.AuthenticatedFeatureJourneyTests`.

## 2. US015: Ending a real session and preventing subsequent access

- [x] 2.1 Add `test_logout_blocks_publish_get_and_post`: use one client to sign in through the login endpoint, publish one valid idea, POST logout, then GET and POST `ideas:publish`. Assert session termination and login redirects for both denied requests, and verify the original idea remains owned by the student with no additional idea created. Verify with `python manage.py test accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post`.
- [x] 2.2 Extend `docs/acceptance-coverage.md` with the two US015 criteria and their existing/new test evidence. Distinguish covered automated behavior from outstanding review, demo, and Product Owner acceptance; explicitly retain US013 and US001-US004 as remaining T17 scope for later verification. Verify all five in-scope criteria map to concrete test methods and run `python manage.py test accounts.tests.AuthenticatedFeatureJourneyTests`.

## 3. Integration checks and completion evidence

- [x] 3.1 Run `python manage.py test accounts ideas` and `python manage.py makemigrations --check --dry-run`; verify the combined existing/new tests pass and no migration is needed. Record the actual commands and results in the acceptance-coverage document.
- [x] 3.2 Run `openspec validate --all --strict` and `git diff --check`; verify this change validates with its deliberate `skip_specs: true`, record any pre-existing configuration warning without hiding it, and confirm the diff contains only this change's planning files, the planned tests, and the coverage document.
- [x] 3.3 Run `python manage.py test` for the complete project and record the actual result. Check the Definition of Done in the README against this first block, document reviewer/demo/Product Owner items that remain pending, and verify the completion note keeps T17 open for its remaining stories rather than claiming the whole sprint is tested.

## 4. Complete Sprint 1 acceptance coverage

- [x] 4.1 Add request-level registration acceptance tests for omitted required fields, invalid values, and an empty POST. Reproduce and minimally correct any demonstrated POST-binding regression required by US013's existing validation criterion; verify with `python manage.py test accounts.tests.RegistrationAcceptanceTests` and retain the existing success/duplicate tests.
- [x] 4.2 Extend the same-session logout journey to reject both GET and POST on publication and editing, preserving stored ideas and prompting for login. Verify with `python manage.py test accounts.tests.AuthenticatedFeatureJourneyTests`.
- [x] 4.3 Add student/investor journeys that verify a real publication appears in browsing/filtering/detail and that an owner's saved edits become visible to the investor. Verify named links, persisted fields, and displayed content with `python manage.py test ideas.tests.IdeaAcceptanceJourneyTests`. Strengthen field-specific edit validation evidence and verify `ideas.tests.EditIdeaTests.test_missing_or_whitespace_required_fields_are_not_saved`.
- [x] 4.4 Complete `docs/acceptance-coverage.md` with all 21 criteria and exact test references. Verify every reference exists, every requirement from the two main specifications appears exactly once, and the document clearly separates automated coverage from peer review, deployment, UX, and Product Owner acceptance.
- [x] 4.5 Run `python manage.py test`, `python manage.py makemigrations --check --dry-run`, `openspec validate --all --strict`, and `git diff --check`. Record actual results, review the complete diff and Definition of Done, and confirm only T17 is proposed for completion after peer review and merge.

## Workflow follow-up

- Update PR #36 from `T17-auth-acceptance-tests` with the complete T17 scope and a resolving reference for #24 only. Make it ready for another team member's review after verification.
- Do not resolve or change story issues #1-#7; their deployment, UX, and Product Owner acceptance remain separately tracked.
- Archive `verify-auth-acceptance` after implementation, verification, peer review, and merge, following the team's OpenSpec workflow.
