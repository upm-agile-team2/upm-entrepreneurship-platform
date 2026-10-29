# Design

## Context

See `proposal.md` for motivation and scope. This first block of T17 (#24) checks the existing US014 (#2) and US015 (#3) requirements in `openspec/specs/accounts/spec.md` against the integrated application at main commit `b1bee12`.

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

- Produce repeatable, cross-app request/session evidence for all five criteria above.
- Make the evidence traceable by criterion, story issue, and concrete test method.
- Preserve the distinction between completing this block and completing T17 for the whole sprint.

**Non-Goals:**

- Browser automation, accessibility assessment, visual wireframe approval, load testing, or a new authentication design.
- Testing an edit, discovery, filtering, or detail route before that route is integrated.
- Claiming Product Owner acceptance, automatically changing story status, or creating substitute business requirements to accommodate the current implementation.

## Decisions

### Use the existing Django test framework and real endpoint calls

Add an `AuthenticatedFeatureJourneyTests` class in `accounts/tests.py`, using `TestCase` and its HTTP client. Create a student account through `User.objects.create_user` in setup, but establish and end the session through `accounts:login` and `accounts:logout` HTTP requests. Do not use `force_login`, `client.login`, or mocks for the actions under test.

Keeping the journey in the existing accounts suite avoids new dependencies and leaves `ideas/tests.py` to the feature work already covered there. A separate browser framework was considered and rejected because the identified gap is session continuity across existing Django endpoints, not browser rendering.

### Prove per-route authentication with anonymous browsing enabled

Apply `override_settings(ALLOW_ANONYMOUS_ACCESS=True)` to the journey tests. Resolve URLs using `reverse`, follow the login URL and its query string returned by the application, and submit the existing form fields (`username` for email and `password`).

Using the restrictive global policy was rejected: it could make the checks pass even if the publication route stopped enforcing authentication itself.

### Cover three distinct journeys

1. Anonymous GET of `ideas:publish` produces a login prompt; valid credentials submitted to that prompt establish a session and make the publication form accessible.
2. An existing account's incorrect password produces the login error, leaves the client unauthenticated, and leaves the publication route behind the login prompt.
3. One client signs in through the login endpoint, publishes one valid idea, logs out through POST, then tries both GET and POST on `ideas:publish`. Assert session termination, login redirects for both requests, and preservation of the previously published idea without creating a second one.

These journeys exercise the stated criteria. Repeating existing standalone form, role, password-hashing, CSRF rejection, or external-redirect tests is not part of this block. Retain those tests as supporting evidence.

### Keep requirements stable and record evidence separately

The current `accounts` requirements already express the expected behavior. Declare `skip_specs: true` and add no delta specs. During implementation, create `docs/acceptance-coverage.md` with the five-criterion matrix, exact existing/new test references, commands used for verification, and an explicit statement that the other sprint stories remain outside this block.

A future PR references #24 using `Refs #24`; it does not close the whole task or T07. This deliberately adapts the normal closing-keyword convention to a partial deliverable.

## Risks / Trade-offs

- A Django client test is not a browser or usability test -> state that limit in the evidence document and retain the team's separate UX and demo checks.
- New work may add or alter restricted routes -> keep this first block scoped to the integrated publication route and extend the coverage matrix as later features arrive.
- A discovered application defect could require production changes -> report the failing criterion and agree on a follow-up implementation scope rather than weakening assertions or editing runtime behavior in this test-only change.
- Existing OpenSpec configuration emits a warning because `rules.specs[0]` is parsed as a YAML mapping -> record the warning separately; correcting shared tooling configuration is outside this block. This change has no spec deltas and still follows the existing source requirements.

## Migration Plan

No application migration or deployment step is needed. Review and merge the future test/documentation PR through the normal workflow, keeping T17 open for its remaining stories. Archive `verify-auth-acceptance` after that block is implemented, verified, reviewed, and merged.
