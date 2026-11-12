# Feedback experiments (Sprint 2, H2)

Experiment stories for H2, prepared in T47 (#79).

**H2:** we believe that at least 20% of the ideas that receive feedback will be edited by their author afterwards if John gets valuable feedback from investors and collaborators through an interactive feedback and commenting system.

Both experiments use the feedback features of US005, US006, US007, US018 and US020. Run them only after those stories are merged into `main`.

| | US021 Investor feedback experiment | US022 Student feedback experiment |
|---|---|---|
| **Method** | Moderated usability test (think aloud) + short questionnaire | Moderated usability test + short interview |
| **Participants** | 3–5 potential investors | 5–8 UPM students |
| **Question** | Do investors leave useful feedback, and does private feedback make them more willing to give detailed critiques? | Do students read the feedback and act on it (reply or edit their idea)? |
| **Success criterion** | At least 80% submit feedback without help, and at least 80% answer 4 or 5 to "the private option made me more willing to give detailed suggestions". | At least 20% of the students reply to the feedback or edit their idea after reading it (the H2 threshold). |
| **Stories under test** | US005 (#43), US020 (#53) | US006 (#44), US007 (#45), US018 (#51), US002 (#5) |
| **Owner** | To be assigned | To be assigned |
| **Estimate** | 3 SP, 4 h | 3 SP, 5 h |

## US021 Investor feedback experiment

**As the** product team, **we want** 3–5 potential investors to leave public and private feedback on sample ideas **in order to** know whether the feedback system makes them comfortable giving detailed suggestions (H2).

| Number | Name | Acceptance criterion |
|---|---|---|
| 1 | Participants | Given the experiment is run, then at least 3 people matching the investor profile have completed the session. |
| 2 | Method stated | Given the results are reported, then they state that the method was a moderated usability test with a questionnaire. |
| 3 | Same conditions | Given a session starts, then the participant uses the MVP loaded with the sample ideas, signed in with an investor account, and receives the same instructions from this script. |
| 4 | Results recorded | Given a session ends, then its row of the observation sheet and its questionnaire are complete. |
| 5 | Decision | Given all sessions are done, then the results state whether the success criterion was met and which changes are added to the Product Backlog, with the user story they belong to. |

| Activity | Hours |
|---|---|
| Recruit and schedule participants | 1 |
| Run the sessions (about 20 minutes each) | 2 |
| Analyse the results and present them | 1 |
| **Total** | **4** |

### Script (about 20 minutes)

1. Introduction: "We are testing the platform, not you. Please think aloud. We will not record your name or any personal data."
2. **Task 1.** "Find an idea that interests you and leave a public comment with one suggestion for the student."
3. **Task 2.** "Now leave a private comment with a question or criticism you would not want to post publicly."
4. **Questionnaire** (1 = strongly disagree, 5 = strongly agree):
   - Q1. Leaving feedback was easy.
   - Q2. The private option made me more willing to give detailed suggestions.
   - Q3. I would use this to contact students about their ideas.
   - Q4 (open). What would make you give more feedback?

### Observation sheet

| Participant | Task 1 done / time | Task 2 done / time | Help needed | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|
| P1 | | | | | | | |
| P2 | | | | | | | |
| P3 | | | | | | | |
| P4 | | | | | | | |
| P5 | | | | | | | |

## US022 Student feedback experiment

**As the** product team, **we want** 5–8 UPM students to read feedback on an idea they published **in order to** know whether they reply to it or improve their idea (H2).

| Number | Name | Acceptance criterion |
|---|---|---|
| 1 | Participants | Given the experiment is run, then at least 5 UPM students have completed the session. |
| 2 | Method stated | Given the results are reported, then they state that the method was a moderated usability test with a short interview. |
| 3 | Same conditions | Given a session starts, then the participant's idea already has the same two pieces of feedback (one public and one private) and the participant receives the same instructions from this script. |
| 4 | Results recorded | Given a session ends, then its row of the observation sheet is complete, including whether the student replied, edited the idea or marked feedback as helpful. |
| 5 | Decision | Given all sessions are done, then the results state the percentage of students who replied or edited their idea, whether it reaches 20%, and which changes are added to the Product Backlog. |

| Activity | Hours |
|---|---|
| Recruit and schedule participants | 1 |
| Prepare each participant's idea and feedback | 1 |
| Run the sessions (about 15 minutes each) | 2 |
| Analyse the results and present them | 1 |
| **Total** | **5** |

### Preparation

For each participant: create a student account, publish a short sample idea with it, and leave the same two comments from an investor account:

- Public: "Interesting idea. Who would pay for it, and how much?"
- Private: "The description does not explain what makes this different from existing solutions."

### Script (about 15 minutes)

1. Introduction (same as US021).
2. **Task.** "You published this idea last week. Have a look at it." Do not mention the feedback; observe whether the participant finds it, replies, marks it as helpful or edits the idea.
3. **Interview:**
   - Did you notice the feedback? Was it useful?
   - Would you change your idea because of it? Why (not)?
   - What would make you answer an investor's comment?

### Observation sheet

| Participant | Found the feedback | Replied | Marked helpful | Edited the idea | Time | Interview notes |
|---|---|---|---|---|---|---|
| P1 | | | | | | |
| P2 | | | | | | |
| P3 | | | | | | |
| P4 | | | | | | |
| P5 | | | | | | |
| P6 | | | | | | |
| P7 | | | | | | |
| P8 | | | | | | |

## Results

| Measure | US021 | US022 |
|---|---|---|
| Participants | | |
| Main result | _ of _ submitted feedback without help; _ of _ answered 4–5 to Q2 | _ of _ replied or edited (_%) |
| Success criterion met? | | |
| Changes proposed (and user story) | | |
