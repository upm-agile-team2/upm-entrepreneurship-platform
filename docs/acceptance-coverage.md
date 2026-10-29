# Acceptance test coverage

Refs #24 (T17). OpenSpec change: `verify-auth-acceptance`.

## Scope and configuration

This is the first block of T17, covering all five existing acceptance criteria of US014 (#2, sign in) and US015 (#3, log out) through the currently integrated publication route. The acceptance requirements remain in [the accounts specification](../openspec/specs/accounts/spec.md); this change adds verification rather than new application behavior.

The journey tests in [accounts/tests.py](../accounts/tests.py) use one Django `TestCase` client across real application URLs and the real session middleware. They create a student fixture with `User.objects.create_user`, then authenticate by submitting the login form; they do not use `client.login`, `force_login`, or mocks for the actions under test.

`AuthenticatedFeatureJourneyTests` explicitly sets `ALLOW_ANONYMOUS_ACCESS=True`. This checks the authentication requirement on `/ideas/new/` while ordinary anonymous browsing remains enabled, independently of the optional global login policy.

These are request/session integration tests, not browser automation, wireframe approval, or a usability experiment. The default Django test client bypasses CSRF enforcement; the existing `accounts.tests.AuthenticationFlowTests.test_logout_requires_csrf` separately checks logout with CSRF enforcement enabled.

## US014: Sign in

Source: [US014 (#2)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/2).

| Acceptance criterion | Existing evidence | Added journey evidence |
|---|---|---|
| Valid sign-in | `accounts.tests.AuthenticationFlowTests.test_valid_login_authenticates_and_redirects_home` | `accounts.tests.AuthenticatedFeatureJourneyTests.test_login_prompt_allows_student_to_access_publish_form` follows the login prompt returned by the protected route, submits valid credentials, and reaches the publication form as that student. |
| Invalid sign-in | `accounts.tests.AuthenticationFlowTests.test_invalid_login_is_generic_and_does_not_authenticate` checks an unknown email. | `accounts.tests.AuthenticatedFeatureJourneyTests.test_invalid_credentials_keep_publish_form_restricted` submits an existing account's incorrect password, checks the error and unauthenticated state, and verifies the publication form still prompts for login with no idea created. |
| Restrict account features | `ideas.tests.PublishIdeaAccessTests.test_anonymous_visitor_is_redirected_to_login` and `ideas.tests.PublishIdeaAccessTests.test_anonymous_post_does_not_create_an_idea` | The two sign-in journey tests exercise the protected form after a successful or rejected authentication attempt. `accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post` also checks login prompts for both protected GET and POST requests after logout. |

## US015: Log out

Source: [US015 (#3)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/3).

| Acceptance criterion | Existing evidence | Added journey evidence |
|---|---|---|
| End session | `accounts.tests.AuthenticationFlowTests.test_authenticated_navigation_and_post_logout` checks logout and the public navigation. | `accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post` signs in through the login endpoint, publishes an idea in the same session, posts logout, and asserts the user is no longer authenticated. |
| Prevent access after logout | Existing tests cover logout and anonymous access separately, without revisiting the publication route in the same session after logout. | `accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post` requests and submits `/ideas/new/` after logout, verifies login redirects and the unauthenticated state, and compares all stored idea values to their pre-logout snapshot. |

## Verification

Verified locally on 2026-10-29 with the project virtual environment (Python 3.12 and Django 5.2.18). These results describe this first T17 block, not completion of the full sprint backlog.

| Command from the repository root | Result |
|---|---|
| `.\.venv\Scripts\python.exe manage.py test accounts.tests.AuthenticatedFeatureJourneyTests` | 3 tests passed. Each new test was also run individually when added. |
| `.\.venv\Scripts\python.exe manage.py test accounts ideas` | 45 tests passed; Django system checks reported no issues. |
| `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run` | No changes detected. |
| `openspec.cmd validate --all --strict` | 4 items passed, 0 failed; the no-delta change is accepted with `skip_specs: true`. |
| `git diff --check` | Passed; changed/untracked paths were also checked against this block's six planned files. |
| `.\.venv\Scripts\python.exe manage.py test` | 45 tests passed with default project discovery; Django system checks reported no issues. |

The coverage document's nine fully qualified test references were checked against the actual test classes and methods in `accounts/tests.py` and `ideas/tests.py`.

### Existing tooling warning

`openspec instructions apply` reports that `rules.specs[0]` in `openspec/config.yaml` is a YAML mapping rather than a string, because its unquoted text includes `Source: ...`. OpenSpec ignores that invalid rules list when loading artifact instructions. This warning predates this work and remains a separate configuration follow-up; no shared configuration is changed here.

This change deliberately declares `skip_specs: true`: its existing business requirements stay unchanged and no delta specs are needed. The validation result is recorded separately above.

## Definition of Done review

| README item | Evidence or remaining work |
|---|---|
| All story acceptance criteria are met | Automated evidence covers the five criteria above against the current publication route. New account-required features must be checked as they are integrated. |
| Every criterion has passing tests | The matrix identifies existing and added tests; actual execution results are recorded in Verification. |
| Code reviewed by another team member | Review and merge of this branch are still pending. |
| Story works in the integrated MVP | These checks exercise the locally integrated code through Django requests and sessions. Shared deployment and demo validation remain separate work. |
| Screen follows the agreed wireframes | This block changes no screens and does not provide visual approval. |
| Product Owner acceptance in Sprint Review | Still pending the team's Sprint Review. |

## Remaining T17 scope

US013 (#1) and US001-US004 (#4-#7) remain outside this first verification block. Existing tests for those stories are retained, but this document does not claim that all of their acceptance criteria have been reviewed or satisfied.

Use `Refs #24` in the future PR. T17 remains open for its other stories and later integration work.
