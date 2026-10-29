# Proposal

## Why

The merged authentication and idea-publishing features now provide a real account-required route, but their tests mostly exercise login, publication, and logout separately. T17 needs evidence that US014 and US015 also hold across the complete session lifecycle, especially when a logged-out user revisits or submits a restricted form.

Refs #24 (T17). Acceptance sources: US014 (#2) and US015 (#3). The results can inform the review of T07 (#14).

## What Changes

- Add Django request/session integration tests that use the real login and logout endpoints and the existing idea-publication endpoint.
- Verify successful login after an anonymous visitor is prompted to sign in, and verify that incorrect credentials keep the protected feature inaccessible.
- Exercise login, a successful publication, logout, and subsequent protected GET and POST requests using the same client; rejected requests must not create another idea.
- Run these checks with anonymous browsing enabled so they verify the publication route's own authentication requirement rather than the optional global login policy.
- Add a concise acceptance-coverage document linking all five criteria of US014 and US015 to existing and new tests, while recording the remaining scope of T17.

Out of scope: implementing or changing registration, login, logout, access policy, publication, editing, discovery, filtering, or detail-page behavior; changing wireframes; deploying the application; archiving `publish-idea`; and automatically closing T17, T07, or the user stories. Later functionality remains the responsibility of its current task owners.

## Capabilities

### New Capabilities

None. This change verifies existing behavior.

### Modified Capabilities

None. `accounts` already defines the five acceptance requirements being checked, and `ideas` already supplies the publication behavior used by the tests. No requirement or acceptance criterion is added or weakened. This test/documentation-only change explicitly declares `skip_specs: true` in `.openspec.yaml`, so no delta specs are required.

## Impact

- Planned implementation files: `accounts/tests.py` and a new `docs/acceptance-coverage.md`.
- Existing routes exercised: `accounts:login`, `accounts:logout`, and `ideas:publish`.
- Existing tests in `accounts/tests.py` and `ideas/tests.py` remain in place; new tests fill session-lifecycle gaps instead of duplicating their assertions as standalone cases.
- No runtime dependencies, database migrations, API changes, or production configuration changes.
- A future pull request should use `Refs #24`, not `Closes #24`: this is the first block of T17, not complete acceptance coverage of all seven sprint stories.
