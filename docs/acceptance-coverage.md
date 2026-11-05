# Acceptance test coverage

Refs #24 (T17). OpenSpec change: `verify-auth-acceptance`.

## Scope and configuration

This matrix covers all 21 acceptance criteria of the seven Sprint 1 stories, using the unchanged [accounts specification](../openspec/specs/accounts/spec.md) and [ideas specification](../openspec/specs/ideas/spec.md). It extends the initial five-criterion authentication block after publication, editing, discovery, and detail were integrated into main at `ed85be2`.

The added journeys in [accounts/tests.py](../accounts/tests.py) and [ideas/tests.py](../ideas/tests.py) use Django `TestCase` clients, real application URLs, session middleware, and the test database. Accounts are created as fixtures; the journeys authenticate by submitting the actual login form and end sessions through POST logout. They do not use `client.login`, `force_login`, or mocks for those actions.

Both journey classes explicitly set `ALLOW_ANONYMOUS_ACCESS=True`. Publication and editing must enforce their own login requirement while anonymous discovery remains available. Separate student and investor clients verify that published ideas and saved edits are visible to another account.

These are request/session integration tests. Browser rendering, wireframe approval, usability experiments, deployment, and Product Owner acceptance require separate evidence. The default Django client bypasses CSRF enforcement; `accounts.tests.AuthenticationFlowTests.test_logout_requires_csrf` separately checks logout with CSRF enforcement enabled. Existing feature tests remain in place; a journey can support several criteria because it asserts each step.

## US013: Create an account

Source: [US013 (#1)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/1).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| Create account | `accounts.tests.AuthenticationFlowTests.test_valid_signup_hashes_password_authenticates_and_redirects` | Valid registration creates the student account, normalizes its email, hashes the password, and authenticates the visitor. |
| Validate registration | `accounts.tests.RegistrationAcceptanceTests.test_missing_required_registration_fields_show_errors`; `accounts.tests.RegistrationAcceptanceTests.test_invalid_registration_values_show_errors`; `accounts.tests.RegistrationAcceptanceTests.test_empty_registration_submission_shows_required_field_errors`; `accounts.tests.AuthenticationFlowTests.test_signup_rejects_mismatched_passwords_and_invalid_role` | Omitted fields, invalid values, mismatched passwords, an invalid role, and an empty POST display validation errors without creating or authenticating an account. |
| Prevent duplicate accounts | `accounts.tests.AuthenticationFlowTests.test_duplicate_email_is_case_insensitive` | An existing email, including case and whitespace variations, is rejected without a second account; the message explicitly asks the visitor to sign in or use another address. |

The empty-POST regression failed before the correction: `SignUpForm(request.POST or None)` produced an unbound form and no required-field errors. Binding by request method fixes that existing validation requirement without changing GET behavior or the registration contract.

## US014: Sign in

Source: [US014 (#2)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/2).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| Valid sign-in | `accounts.tests.AuthenticationFlowTests.test_valid_login_authenticates_and_redirects_home`; `accounts.tests.AuthenticatedFeatureJourneyTests.test_login_prompt_allows_student_to_access_publish_form` | Valid credentials establish a session; following the protected route's actual login prompt returns the student to the publication form. |
| Invalid sign-in | `accounts.tests.AuthenticationFlowTests.test_invalid_login_is_generic_and_does_not_authenticate`; `accounts.tests.AuthenticatedFeatureJourneyTests.test_invalid_credentials_keep_publish_form_restricted` | An unknown email or an existing account's wrong password displays the generic error, leaves the visitor unauthenticated, and keeps publication restricted. |
| Restrict account features | `ideas.tests.PublishIdeaAccessTests.test_anonymous_visitor_is_redirected_to_login`; `ideas.tests.PublishIdeaAccessTests.test_anonymous_post_does_not_create_an_idea`; `accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post` | Anonymous GET and POST requests prompt for login. After logout, publication and editing are both restricted and stored ideas remain unchanged. |

## US015: Log out

Source: [US015 (#3)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/3).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| End session | `accounts.tests.AuthenticationFlowTests.test_authenticated_navigation_and_post_logout`; `accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post` | A real login/publication session ends through POST logout; the client is unauthenticated and public navigation offers login again. |
| Prevent access after logout | `accounts.tests.AuthenticatedFeatureJourneyTests.test_logout_blocks_publish_get_and_post` | The same client is prompted to sign in on GET and POST to both publication and its existing idea's edit route. All stored idea values match the pre-logout snapshot. |

## US001: Publish an idea

Source: [US001 (#4)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/4).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| Submit an idea | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas` | A signed-in student publishes through HTTP; the stored owner is correct and a separately signed-in investor sees the publication in discovery and detail. |
| Require essential information | `ideas.tests.RequireEssentialInformationTests.test_missing_title_asks_for_the_title`; `ideas.tests.RequireEssentialInformationTests.test_missing_description_asks_for_the_description`; `ideas.tests.RequireEssentialInformationTests.test_missing_both_asks_for_both` | Missing title, description, or both produces the corresponding visible prompts and no idea is published. |

## US002: Edit an idea

Source: [US002 (#5)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/5).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| Select edit option | `ideas.tests.IdeaAcceptanceJourneyTests.test_owner_edits_are_visible_to_another_user`; `ideas.tests.EditIdeaTests.test_owner_sees_edit_form` | The owner's detail page offers the Edit idea link to a populated edit form. |
| Enter idea details | `ideas.tests.IdeaAcceptanceJourneyTests.test_owner_edits_are_visible_to_another_user`; `ideas.tests.EditIdeaTests.test_owner_can_update_title_description_and_category` | Saving changed title and description persists them; the investor sees the new values in discovery and detail. |
| Select a category | `ideas.tests.IdeaAcceptanceJourneyTests.test_owner_edits_are_visible_to_another_user` | Changing and saving the category persists it and displays the new category to the investor on the detail page. |
| Validate required fields | `ideas.tests.EditIdeaTests.test_missing_or_whitespace_required_fields_are_not_saved` | Empty, omitted, and whitespace-only required fields produce the exact field errors and visible prompts; the stored title and description remain unchanged. |

Existing non-owner and investor edit-rejection tests remain in the full suite.

## US003: Browse and filter ideas

Source: [US003 (#6)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/6).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| Browse published ideas | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.HomePageTests.test_home_page_displays_published_ideas` | The investor's discovery page lists the ideas submitted by the student. |
| Filter by category | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.HomePageTests.test_category_filter_shows_only_ideas_in_selected_category` | Selecting one category displays its published idea and excludes the idea from the other category. |
| Clear filters | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.HomePageTests.test_clearing_category_filter_restores_all_ideas` | The Clear filter link targets unfiltered discovery, where both publications are visible again. |
| No matching ideas | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.HomePageTests.test_empty_category_filter_shows_no_match_message` | Selecting a category without ideas displays the no-match explanation and neither publication. |

## US004: View idea details

Source: [US004 (#7)](https://github.com/upm-agile-team2/upm-entrepreneurship-platform/issues/7).

| Acceptance criterion | Test evidence | Verified behavior |
|---|---|---|
| Open project details | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.HomePageTests.test_idea_card_links_to_its_detail_page` | A listed idea links to its own detail route, which the investor can open. |
| Display project information | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.IdeaDetailPageTests.test_detail_page_shows_title_full_description_and_category` | The detail page displays the title, complete description, and category. |
| Return to the project list | `ideas.tests.IdeaAcceptanceJourneyTests.test_investor_can_discover_filter_and_open_published_ideas`; `ideas.tests.IdeaDetailPageTests.test_detail_page_links_back_to_discovery` | Back to ideas targets discovery and the investor can return to see both publications. |

## Verification

Verified locally on 2026-10-30 using the project virtual environment (Python 3.12 and Django 5.2.18). The complete suite passes against the integrated code and the minimal registration correction.

| Command from the repository root | Result |
|---|---|
| `.\.venv\Scripts\python.exe manage.py test accounts.tests.RegistrationAcceptanceTests` | 3 tests passed after reproducing and correcting the empty-POST regression. |
| `.\.venv\Scripts\python.exe manage.py test accounts.tests.AuthenticatedFeatureJourneyTests` | 3 tests passed, including protected publication and editing after logout. |
| `.\.venv\Scripts\python.exe manage.py test ideas.tests.IdeaAcceptanceJourneyTests` | 2 tests passed with distinct student and investor sessions. |
| `.\.venv\Scripts\python.exe manage.py test ideas.tests.EditIdeaTests.test_missing_or_whitespace_required_fields_are_not_saved` | Passed with field-specific validation assertions. |
| `.\.venv\Scripts\python.exe manage.py test` | 78 tests passed; Django system checks reported no issues. |
| `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run` | No changes detected. |
| `openspec.cmd validate --all --strict` | 7 items passed, 0 failed; the no-delta change is accepted with `skip_specs: true`. |
| `git diff --check` | Passed; the complete diff is limited to acceptance tests, this evidence document, this change's planning files, and the one-line registration correction. |

All 30 fully qualified test references were checked against the actual classes and methods in both test files. All 21 requirements in the two main specifications appear exactly once in the criterion rows.

### Existing tooling warning

`openspec instructions apply` reports that `rules.specs[0]` in `openspec/config.yaml` is a YAML mapping rather than a string because its unquoted text includes `Source: ...`. OpenSpec ignores that invalid rules list when loading artifact instructions. This warning predates this work and remains a separate configuration follow-up; no shared configuration is changed here.

This change deliberately declares `skip_specs: true`: the existing business requirements remain unchanged and no delta specs are needed.

## Definition of Done review

| README item | Evidence or remaining work |
|---|---|
| All story acceptance criteria are met | Automated evidence covers all 21 criteria in the integrated code under review; deployment and team acceptance remain separate. |
| Every criterion has passing tests | The matrix identifies concrete tests for every criterion; execution results are recorded above. |
| Code reviewed by another team member | PR #36 still requires another team member's review and merge. |
| Story works in the integrated MVP | Requests, sessions, templates, and persistence are tested together locally. Shared deployment and demo validation remain T19/team work. |
| Screen follows the agreed wireframes | This task provides no visual approval; T18 and the team's UX review remain separate. |
| Product Owner acceptance in Sprint Review | Still pending the team's Sprint Review. |

## T17 completion and workflow

The automated acceptance deliverable now covers all seven Sprint 1 stories. PR #36 should resolve only T17 (#24) after peer review and merge. It does not complete deployment, UX experiments, or Product Owner acceptance, and does not change story issue states.

Keep `verify-auth-acceptance` active for review and merge; archive it afterward following the repository workflow.
