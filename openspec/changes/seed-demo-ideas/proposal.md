# Proposal

## Why

The Sprint 1 experiment stories need the MVP to show realistic content: investors must browse and filter published ideas, and the demo needs more than an empty discovery page. Today the database only contains what each developer publishes by hand, so every session starts from a different state. This change covers T18 (#25).

## What Changes

- Add the `seed_demo_ideas` management command, which creates 20 sample ideas across the initial categories, written by four fictional student accounts that cannot sign in.
- Make the command safe to run more than once, and let `--remove` delete only the sample ideas and their demo authors.
- Add the investor experiment guide in `docs/experiments/investor-experiment.md`: experiment story with acceptance criteria and estimated hours, participant profile, session script, observation sheet and results table.

Out of scope: the student publishing experiment (its own experiment story), deploying the MVP (T19, #26), and any change to how ideas are published, listed or displayed.

Refs #25.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The command is a development and experiment tool; it adds no behaviour required by a user story, so there is no spec delta.

## Impact

- `ideas/management/commands/seed_demo_ideas.py`: new command.
- `ideas/tests.py`: tests for the command.
- `docs/experiments/investor-experiment.md`: new experiment guide.
- `README.md`: how to load the sample ideas.
- No model, migration or dependency changes.
