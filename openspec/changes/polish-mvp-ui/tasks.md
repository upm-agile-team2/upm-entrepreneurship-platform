# Tasks

Refs #39. Preserve the existing accounts/ideas criteria; use their existing Django tests. All commands run from the repository root with the project virtual environment.

## 1. Shared visual foundation

- [x] 1.1 Capture before screenshots of discovery and login using an isolated preview database/profile, and start docs/ui-polish.md with the baseline and review scope. Verify the two images exist and the user's db.sqlite3 is untouched.
- [x] 1.2 Add/register the local stylesheet and polish base.html navigation, typography, surfaces, focus and messages. Verify Django findstatic resolves css/app.css, browser assets load, and existing anonymous/authenticated navigation tests pass; record the shared design in docs/ui-polish.md.

## 2. Discovery

- [x] 2.1 Polish discovery, filter, cards and empty states while preserving GET controls, category selection, clear links and detail destinations. Adapt exact presentation assertions only as needed; run HomePageTests and DiscoveryPageTemplateTests and capture an after discovery image documented in docs/ui-polish.md.

## 3. Forms and detail

- [x] 3.1 Unify authentication and idea forms, including visible field errors, keyboard focus and help associations without changing validation or field order. Run AuthenticationFlowTests, IdeaFormTests, RequireEssentialInformationTests and IdeaFormPageTests; capture login/signup/publication and document actual results.
- [x] 3.2 Polish the detail reading layout and existing actions. Run IdeaDetailPageTests and EditIdeaTests; capture detail/edit and document actual results.

## 4. Integration and review

- [x] 4.1 Exercise the real browser journey and error/empty/role states at 360/768/1440 widths and 200% zoom/reflow, checking overflow, focus, long text, working static assets and reduced motion. Capture representative responsive images and record observations in docs/ui-polish.md.
- [x] 4.2 Check PR #36 compatibility in an isolated copy using its test additions and, only in that copy, its known empty-POST fix; keep our branch independent. Record exact counts/results and confirm no changes to accounts/views.py or T17 artifacts.
- [x] 4.3 Run python manage.py test, makemigrations --check --dry-run, openspec validate --all --strict, and git diff --check. Review the complete diff and Definition of Done, record actual results, and prepare a PR for peer review resolving #39 only.

## Workflow follow-up

- Another team member reviews and merges the visual PR; do not self-merge.
- Leave PR #36, T18/T19 and story issue states unchanged.
- Archive polish-mvp-ui after review and merge; Product Owner acceptance remains the team's Sprint Review activity.
