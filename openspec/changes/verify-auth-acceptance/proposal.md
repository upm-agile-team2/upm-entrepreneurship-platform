# Proposal

## Why

T17 (#24) requires tests for the acceptance criteria of all seven Sprint 1 stories. The initial authentication block is implemented; publication, editing, discovery, and detail are now integrated in main, so the remaining coverage can be verified without waiting for other feature branches.

On 2026-10-30 the task owner requested completion of the whole T17 scope. The historical change name is retained while coverage expands from five authentication criteria to all 21 Sprint 1 criteria.

Refs #24 (T17). Sources: US013-US015 (#1-#3) and US001-US004 (#4-#7).

## What Changes

- Add Django request/session integration tests that use the real login and logout endpoints and the existing idea-publication endpoint.
- Verify successful login after an anonymous visitor is prompted to sign in, and verify that incorrect credentials keep the protected feature inaccessible.
- Exercise login, a successful publication, logout, and subsequent protected GET and POST requests using the same client; rejected requests must not create another idea.
- Run these checks with anonymous browsing enabled so they verify the publication route's own authentication requirement rather than the optional global login policy.
- Extend the logout checks to the integrated edit route as well as publication.
- Add registration regressions for omitted fields, invalid values, and an empty POST; minimally correct a demonstrated failure of the existing validation requirement if necessary.
- Add real student/investor journeys proving publication visibility, filtering/clearing/detail navigation, and visibility of an owner's saved edits.
- Complete the acceptance-coverage document with all 21 criteria, reusing existing tests and recording actual execution results.

Out of scope: new features or changed requirements, redesigning screens or authentication, deployment (T19), usability prototypes/experiments (T18), shared OpenSpec configuration changes, archiving other authors' changes, merging our own PR without peer review, or automatically completing user stories. Minimal corrections of demonstrated existing acceptance failures are within the requested completion scope.

## Capabilities

### New Capabilities

None. This change verifies existing behavior.

### Modified Capabilities

None. `accounts` and `ideas` already define all 21 requirements. No requirement is added or weakened; any minimal regression correction restores the existing contract. This change declares `skip_specs: true` because no spec-level behavior changes and no delta specs are required.

## Impact

- Implementation files: `accounts/tests.py`, `ideas/tests.py`, and `docs/acceptance-coverage.md`; runtime code only for a demonstrated existing acceptance failure.
- Existing routes exercised: signup, login, logout, publication, editing, discovery, and detail.
- Existing tests in `accounts/tests.py` and `ideas/tests.py` remain in place; new tests fill validation and cross-feature session gaps, and existing assertions are strengthened where criterion evidence was incomplete.
- No new dependencies, database migrations, API contracts, or production configuration changes.
- Update PR #36 as the complete T17 deliverable after verification. Its resolving reference targets #24 only, after peer review and merge; story issues #1-#7 remain informational references.
