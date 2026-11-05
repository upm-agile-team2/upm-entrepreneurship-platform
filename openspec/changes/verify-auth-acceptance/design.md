# Design

## Context

See `proposal.md` for motivation and scope. The initial block below checked US014 (#2) and US015 (#3) against main commit `b1bee12`. On 2026-10-30 the task owner requested full T17 completion; the new section below extends verification to all 21 criteria using integrated main at `ed85be2` and preserves the initial evidence as history.

Observed implementation:

- `AccountLoginView` uses the real email authentication form and Django session login; its default destination is `ideas:home`.
- `publish_idea` requires login independently of `AnonymousAccessMiddleware`, accepts signed-in students, and stores the session user as the idea owner.
- The login form posts to its current URL. A login prompt's `next` query parameter can therefore remain on the URL through form submission; the test should follow that URL instead of constructing a different navigation contract.
- `AccountLogoutView` handles POST logout and returns to `ideas:home`.
- Anonymous browsing is enabled by default. The optional global policy has its own existing tests and is not the mechanism this block is intended to prove.

Existing evidence and remaining gaps:

| Acceptance criterion | Existing test evidence | Addition in this block |
|---|---|---|
| US014: Valid sign-in | `AuthenticationFlowTests.test_valid_login_authenticates_and_redirects_home` | Login through the actual prompt returned by the protected publication route, then access the form as the authenticated student. |
| US014: Invalid sign-in | `AuthenticationFlowTests.test_invalid_login_is_generic_and_does_not_authenticate` | Incorrect password for an existing account through the same prompt; the account-required feature must remain inaccessible. |
| US014: Restrict account features | `PublishIdeaAccessTests.test_anonymous_visitor_is_redirected_to_login` and `test_anonymous_post_does_not_create_an_idea` | Exercise the restriction again after a real authenticated session has been ended, checking both the login prompt and absence of side effects. |
| US015: End session | `AuthenticationFlowTests.test_authenticated_navigation_and_post_logout` | End the actual session used to log in and publish through HTTP endpoints. |
| US015: Prevent access after logout | Existing logout tests revisit the public home page; global-policy tests require an explicit configuration override. | Visit and submit the real restricted publication route after logout; verify a login prompt and no additional idea. |

The existing suite passed 42 tests during the preceding local integration check. This is a historical baseline, not proof that the proposed tests have been implemented or run.

## Goals / Non-Goals

**Goals:**

- Produce repeatable, cross-app request/session evidence for all 21 criteria across the seven Sprint 1 stories.
- Make the evidence traceable by criterion, story issue, and concrete test method.
- Preserve the distinction between completing T17's test deliverable and the separate UX, deployment, and Product Owner work.

**Non-Goals:**

- Browser automation, accessibility assessment, visual wireframe approval, load testing, or a new authentication design.
- New product features, changed business requirements, or testing routes that have not been integrated.
- Claiming Product Owner acceptance, automatically changing story status, or creating substitute business requirements to accommodate the current implementation.

## Decisions

### Use the existing Django test framework and real endpoint calls

Add an `AuthenticatedFeatureJourneyTests` class in `accounts/tests.py`, using `TestCase` and its HTTP client. Create a student account through `User.objects.create_user` in setup, but establish and end the session through `accounts:login` and `accounts:logout` HTTP requests. Do not use `force_login`, `client.login`, or mocks for the actions under test.

Keeping the authentication journeys in the existing accounts suite avoids new dependencies. The expanded publication/edit/discovery journeys belong in `ideas/tests.py` alongside the existing feature tests. A separate browser framework was considered and rejected because the identified gaps concern requests and session continuity across existing Django endpoints.

### Prove per-route authentication with anonymous browsing enabled

Apply `override_settings(ALLOW_ANONYMOUS_ACCESS=True)` to the journey tests. Resolve URLs using `reverse`, follow the login URL and its query string returned by the application, and submit the existing form fields (`username` for email and `password`).

Using the restrictive global policy was rejected: it could make the checks pass even if the publication route stopped enforcing authentication itself.

### Cover three distinct journeys

1. Anonymous GET of `ideas:publish` produces a login prompt; valid credentials submitted to that prompt establish a session and make the publication form accessible.
2. An existing account's incorrect password produces the login error, leaves the client unauthenticated, and leaves the publication route behind the login prompt.
3. One client signs in through the login endpoint, publishes one valid idea, logs out through POST, then tries both GET and POST on `ideas:publish`. Assert session termination, login redirects for both requests, and preservation of the previously published idea without creating a second one.

These journeys exercise the stated criteria. Repeating existing standalone form, role, password-hashing, CSRF rejection, or external-redirect tests is not part of this block. Retain those tests as supporting evidence.

### Keep requirements stable and record evidence separately

The current `accounts` and `ideas` requirements already express the expected behavior. Keep `skip_specs: true` and add no delta specs. Complete `docs/acceptance-coverage.md` with all 21 criteria, exact existing/new test references, actual verification results, and an explicit separation of testing from the remaining deployment, UX, peer review, and Product Owner work.

Once full verification passes, update PR #36 to the complete T17 scope and target #24 only for completion after peer review and merge. Story references remain informational. Do not merge the PR ourselves or change story states.

### Complete coverage after the remaining features are integrated

- Registration: add request-level regressions for each missing required field, invalid email/name/password values, and an empty POST. `signup` currently binds `request.POST or None`, which may render an unbound form without validation messages for an empty POST. Reproduce this before applying any minimal method-based binding correction, as already used by publishing and editing.
- Logout: extend the same authenticated client journey to denied GET/POST requests on both publication and editing, checking the login prompt and an unchanged snapshot of stored ideas.
- Publication/discovery/detail: use distinct student and investor clients, authenticated through the actual login endpoint. Publish two categories through HTTP, verify another user can see the results, filter and observe an empty category, clear the filter, open full details, and return to discovery.
- Editing: follow the owner's Edit link, verify the populated form, save changed title/description/category, and verify those persisted changes are displayed to the investor. Strengthen the existing missing-field test to check the exact erroneous fields and their visible messages while preserving stored data; retain the non-owner rejection tests.
- Coverage matrix: map all 21 main-spec requirements exactly once to actual test methods. Use named URLs and semantic link labels/targets; direct ORM reads may verify persistence but cannot substitute for another account's ability to see the result.
- These additions remain Django request/session tests, without new browser automation dependencies. Minimal fixes of reproduced acceptance failures restore existing requirements rather than changing their contract.

## Risks / Trade-offs

- A Django client test is not a browser or usability test -> state that limit in the evidence document and retain the team's separate UX and demo checks.
- New work may add or alter restricted routes -> verify both currently integrated write routes and keep the coverage matrix tied to the version under review.
- A discovered application defect may violate an existing criterion -> reproduce it with a regression and keep the correction minimal and directly tied to that requirement; do not weaken assertions or introduce new product behavior.
- Existing OpenSpec configuration emits a warning because `rules.specs[0]` is parsed as a YAML mapping -> record the warning separately; correcting shared tooling configuration is outside this block. This change has no spec deltas and still follows the existing source requirements.

## Migration Plan

No dependency or database migration is expected. Incorporate main into the T17 branch with a merge, finish all acceptance coverage and verification, and update PR #36 for peer review. T17 remains open until that reviewed PR is merged. Archive this change afterward, independently of the other authors' changes.
