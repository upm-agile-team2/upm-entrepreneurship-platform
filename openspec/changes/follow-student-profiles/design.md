# Design

## Context

See proposal.md for the problem and scope. Main already contains StudentProfile, Skill, the investor-facing `accounts:investor_profile` view, and the shared UPM ideaHub templates. A profile page can represent a student who has not created a StudentProfile record. The durable main specs currently cover accounts and ideas; following is a new capability.

## Goals / Non-Goals

**Goals:** implement the three US011 acceptance criteria as one server-rendered workflow; keep ownership checks in the backend; preserve existing profile editing and display behavior.

**Non-Goals:** no general profile directory, new notification events, JavaScript dependency, or profile-schema changes.

## Decisions

### Store relationships between user accounts

Add Follow in `accounts` with investor and student foreign keys to the custom User, plus a creation timestamp. Use account relationships instead of a StudentProfile foreign key so incomplete or absent profile details do not prevent following. Cascade on account deletion. Enforce a unique investor/student pair and prevent self-following in database constraints. Validate investor/student roles in `clean()`, matching existing profile-model conventions; ordinary `save()` does not invoke `full_clean()`. Request handlers enforce roles explicitly.

### Use explicit idempotent POST actions

Provide separate follow and unfollow routes beneath the student account identifier. Require an authenticated investor, accept only POST, and resolve targets from student accounts only. Derive investor identity from the session, never submitted identifiers. `get_or_create` and the unique constraint handle repeated follows; scoped deletion handles repeated unfollows. Use existing CSRF middleware and fixed internal redirects. The unfollow form can submit `source=following` to return to the list; all other values return to the student's profile, with no arbitrary redirect URL.

### Extend existing profile views and navigation

Add the current investor's follow state to the existing investor-facing profile context. Render Follow/Unfollow forms alongside the profile heading, including for incomplete profiles. Add Following to investor navigation and a list with names, available bio/skills, profile links and Unfollow forms. Empty lists link to existing idea browsing, where author links lead to student profiles. Reuse existing tokens and add only scoped layout styles.

### Fetch only the current investor's follows

Query Follow by the authenticated investor and student role, select the student and optional profile, and prefetch skills. Sort most recently followed first with the primary key as a tie-breaker. This avoids exposing other investors' collections or issuing per-card profile/skill queries. A general discovery list and skill filters remain T37/T38 work.

## Risks / Trade-offs

- Missing or incomplete profile data: render available information and a clear fallback; account-based following remains valid.
- Repeated form submissions: idempotent endpoints and database uniqueness prevent duplicates or accidental toggling.
- Role changes through administration: views restrict both actor and targets to their current roles; model validation protects validated writes. Database constraints cannot check roles in another row.
- Team changes to shared navigation: keep the diff small; review compatibility with newer main changes before publishing.

## Migration Plan

The additive migration creates only the Follow table and constraints. Back up local SQLite before applying it, preserve existing users/ideas, and run the standard Django checks and tests. Removing this feature would require reversing that migration, which discards follow relationships only; no automatic rollback is performed.

## Delivery

One branch and one PR for T35 (#67) and T36 (#68), with commits separated by task after local review. Reference US011 (#49); keep shared tests, experiments and deployment tasks open. Record acceptance coverage and remaining peer-review/Sprint Review conditions without claiming those external approvals are complete.
