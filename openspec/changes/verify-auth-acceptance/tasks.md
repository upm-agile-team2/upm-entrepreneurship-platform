# Tasks

Refs #24 (T17). This first block checks the three criteria of US014 (#2) and the two criteria of US015 (#3) already specified in `openspec/specs/accounts/spec.md`. Other sprint stories remain in the wider T17 backlog.

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

## Workflow follow-up

- Open a pull request from `T17-auth-acceptance-tests` with `Refs #24`, and ask another team member to review it. Do not use `Closes #24` for this partial block.
- Use the resulting evidence to coordinate the review of T07 (#14), US014 (#2), and US015 (#3); issue state changes require their own completion review.
- Archive `verify-auth-acceptance` after implementation, verification, review, and merge, following the team's OpenSpec workflow.
- Extend T17 coverage as the editing, browsing, filtering, and detail features are integrated.
