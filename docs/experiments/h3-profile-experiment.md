# Profile experiment (Sprint 2, H3)

Experiment story for H3, prepared in T47 (#79).

**H3:** we believe that at least 15% of investor visits end with a student profile being opened if John gets greater opportunities to connect with potential investors through user profiles that showcase students' skills, projects and interests.

| | |
|---|---|
| **Method** | Moderated usability test (think aloud) + short questionnaire, plus the profile visit counter of US019 |
| **Participants** | 3–5 potential investors (same profile as the H1 investor experiment) |
| **Question** | When investors look at an idea, do they open the student's profile on their own, and is the profile useful to them? |
| **Success criterion** | At least 15% of the participants open a student profile without being asked (the H3 threshold), and at least 75% of those who open one rate it 4 or 5 as "useful to decide whether to contact the student". |
| **Stories under test** | US009 (#47), US010 (#48), US011 (#49), US012 (#50), US019 (#52) |
| **Owner** | To be assigned |
| **Estimate** | US023, 3 SP, 4 h |

## US023 Profile experiment

**As the** product team, **we want** 3–5 potential investors to explore ideas and student profiles **in order to** know whether profiles lead them to the students behind the ideas (H3).

| Number | Name | Acceptance criterion |
|---|---|---|
| 1 | Participants | Given the experiment is run, then at least 3 people matching the investor profile have completed the session. |
| 2 | Method stated | Given the results are reported, then they state that the method was a moderated usability test with a questionnaire and the profile visit counter. |
| 3 | Same conditions | Given a session starts, then the participant is signed in with an investor account, the MVP has the sample ideas, and at least three sample students have a complete profile. |
| 4 | Unprompted first | Given a session starts, then the first task does not mention profiles, so that opening a profile on their own can be measured. |
| 5 | Results recorded | Given a session ends, then its row of the observation sheet is complete and the visit counter of the opened profiles has been noted. |
| 6 | Decision | Given all sessions are done, then the results state whether the success criterion was met and which changes are added to the Product Backlog, with the user story they belong to. |

| Activity | Hours |
|---|---|
| Recruit and schedule participants | 1 |
| Run the sessions (about 20 minutes each) | 2 |
| Analyse the results and present them | 1 |
| **Total** | **4** |

## Preparation

1. Load the sample ideas: `python manage.py seed_demo_ideas`.
2. Create three student accounts, each with a complete profile (bio, skills, a project and some experience), and publish one idea with each of them.
3. Create one investor account per participant (or let them sign up as investors at the start of the session).
4. Note the visit counter of each sample profile before the first session.

## Script (about 20 minutes)

1. Introduction: "We are testing the platform, not you. Please think aloud. We will not record your name or any personal data."
2. **Task 1 (unprompted).** "Look for an idea you would consider supporting and decide whether you would like to contact its author." Do not mention profiles. Observe whether the participant opens the student's profile.
3. **Task 2.** "Find a student who knows [a skill shown in the sample profiles] and follow them." (Covers US011 and US012 if they are merged.)
4. **Questionnaire** (1 = strongly disagree, 5 = strongly agree):
   - Q1. The student's profile was useful to decide whether to contact them.
   - Q2. I could easily find students with the skills I was looking for.
   - Q3 (open). What information about the student was missing?

## Observation sheet

| Participant | Opened a profile in Task 1 (unprompted) | Task 2 done / time | Help needed | Q1 | Q2 | Q3 |
|---|---|---|---|---|---|---|
| P1 | | | | | | |
| P2 | | | | | | |
| P3 | | | | | | |
| P4 | | | | | | |
| P5 | | | | | | |

## Results

| Measure | Result |
|---|---|
| Participants | |
| Opened a profile without being asked | _ of _ (_%) |
| Rated the profile 4–5 as useful | _ of _ (_%) |
| Profile visits recorded by the counter (before → after) | |
| Success criterion met? | |
| Changes proposed (and user story) | |
