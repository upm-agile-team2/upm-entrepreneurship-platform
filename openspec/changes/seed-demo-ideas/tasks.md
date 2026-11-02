# Tasks

## 1. Sample ideas (T18, #25)

- [x] 1.1 Add the `seed_demo_ideas` command with 20 sample ideas covering every initial category; add a Django test proving the ideas are created and every main category is used, verifying the test passes
- [x] 1.2 Create the demo authors as students with an unusable password; add a Django test proving they cannot sign in, verifying the test passes
- [x] 1.3 Make the command idempotent; add a Django test proving a second run creates no duplicates, verifying the test passes
- [x] 1.4 Add `--remove` to delete only the sample ideas and their authors; add a Django test proving ideas from real students are kept, verifying the test passes
- [x] 1.5 Stop with a clear error when a required category is missing; add a Django test proving no ideas are created in that case, verifying the test passes
- [x] 1.6 Add a Django test proving the sample ideas appear on the discovery page

## 2. Investor experiment

- [x] 2.1 Write `docs/experiments/investor-experiment.md` with the experiment story, acceptance criteria, estimated hours, participant profile, script, observation sheet and results table
- [x] 2.2 Document the command in the README
- [x] 2.3 Run `python manage.py test` and check the Definition of Done in the README
