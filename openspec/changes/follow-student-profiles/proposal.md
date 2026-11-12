# Proposal

## Why

Investors can now open student profiles, but cannot keep a personal list of students they want to revisit. US011 (#49) requires following, unfollowing, and viewing followed profiles; T35 (#67) and T36 (#68) implement this complete workflow.

## What Changes

- Add a persistent investor-to-student follow relationship with duplicate prevention.
- Add authenticated, investor-only follow and unfollow actions.
- Show the appropriate Follow or Unfollow button on investor-facing student profiles.
- Add an investor-only Following page and navigation link, including an empty state and links back to profiles.
- Cover the three acceptance criteria and their authorization and persistence boundaries with Django tests.

Out of scope: profile discovery and skill filtering (T37/T38), visit analytics, publication notifications, feedback, deployment, and closing the shared Sprint 2 acceptance-testing task. Existing branding and profile content remain the basis of the interface.

## Capabilities

### New Capabilities

- `student-following`: Investors maintain and revisit their own list of followed students.

### Modified Capabilities

None. Existing account and profile-view requirements remain unchanged.

## Impact

- `accounts`: Follow model, additive migration, URLs, views, and tests.
- Templates: follow controls on student profiles, a followed-profiles page, and investor navigation.
- Styling: small responsive additions using the existing UPM ideaHub tokens and components.
- No new runtime dependencies. One PR will reference US011 (#49) and close T35 (#67) and T36 (#68) after review.
