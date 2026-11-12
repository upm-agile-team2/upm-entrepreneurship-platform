# Proposal

## Why

Sprint 2 validates H2 (feedback) and H3 (student profiles), but the Sprint 2 Backlog only describes two H2 experiments in one line each and leaves the H3 experiment empty. The professor asked that every experiment be a user story with acceptance criteria and hours, and that the method (usability test, interview or questionnaire) is stated explicitly. This change covers T47 (#79).

## What Changes

- Add `docs/experiments/h2-feedback-experiments.md` with two experiment stories: US021 (investors leave public and private feedback) and US022 (students read and act on feedback).
- Add `docs/experiments/h3-profile-experiment.md` with experiment story US023 (investors open student profiles without being asked).
- Each story states its method, participants, success criterion, acceptance criteria, estimated hours, script, observation sheet and results table.
- Add `docs/experiments/README.md` as an index of all experiment guides.

Out of scope: running the experiments, sample feedback data (it depends on the feedback stories in PR #85 and PR #87) and any code change.

Refs #79; US021–US023 (experiment stories for H2 and H3).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The guides describe validation activities, not behaviour required by a user story, so there is no spec delta.

## Impact

- `docs/experiments/`: two new guides and an index.
- No code, model, migration or dependency changes.
