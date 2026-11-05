# Investor experiment (Sprint 1, H1)

Experiment story from the Sprint 1 Backlog, prepared in T18 (#25).

| | |
|---|---|
| **Hypothesis** | H1: an intuitive submission platform with categories and filters helps investors discover relevant business opportunities. |
| **Validation method** | Ask 3–5 potential investors to browse sample ideas and use the category filter; ask whether they can find an idea relevant to their interests. |
| **Success criterion** | At least 75% of the participants find an idea relevant to their interests using the category filter. |
| **Owner** | Argenis Ronaldo Andrade Zambrano |
| **Stories under test** | US003 Browse and filter ideas by category (#6), US004 View project details (#7) |

## Experiment story (for the Sprint Backlog and the burndown)

**As a** team, **we want to** observe 3–5 potential investors using the discovery page **in order to** know whether the category filter helps them find ideas that interest them (H1).

| Number | Name | Acceptance criterion |
|---|---|---|
| 1 | Participants | Given the experiment is run, then at least 3 people matching the participant profile below have completed the session. |
| 2 | Same conditions | Given a session starts, then the participant uses the MVP loaded with the sample ideas (`seed_demo_ideas`) and receives the same instructions from this script. |
| 3 | Results recorded | Given a session ends, then its row of the observation sheet is complete (tasks completed, time, help needed, answers). |
| 4 | Decision | Given all sessions are done, then the results table states whether the success criterion was met and what changes are proposed for the Product Backlog. |

| Activity | Estimated hours |
|---|---|
| Prepare sample ideas and this script (T18) | 2 |
| Recruit and schedule participants | 1 |
| Run the sessions (about 20 minutes each, up to 5) | 2 |
| Analyse the results and present them in the Sprint Review | 1 |
| **Total** | **6** |

## Participants

3–5 people who could realistically invest in, mentor or support a student start-up, for example:

- Students of business, management or industrial organisation who are interested in start-ups.
- Lecturers or staff related to entrepreneurship (for example, people from UPM's innovation and entrepreneurship programmes).
- People working in finance, consulting or a company that funds innovation projects.

Team members do not take part as participants.

## Preparation

1. Run the MVP on a laptop with the sample ideas:

   ```bash
   python manage.py migrate
   python manage.py seed_demo_ideas
   python manage.py runserver
   ```

2. Open http://127.0.0.1:8000/ in a private window, signed out. Browsing does not require an account as long as `DJANGO_ALLOW_ANONYMOUS_ACCESS` keeps its default value (`True`).
3. Print or open the observation sheet below and have a timer ready.
4. After the last session, remove the sample ideas if they are not needed for the demo:

   ```bash
   python manage.py seed_demo_ideas --remove
   ```

## Session script (about 20 minutes)

**Introduction (2 minutes).** Read aloud:

> "Thank you for helping us. We are testing a platform where UPM students publish entrepreneurial ideas so that investors can find them. We are testing the platform, not you: there are no wrong answers. Please think aloud while you use it. We will not record your name or any personal data."

**Before the tasks.** Show the categories available in the discovery filter (Technology, Health, Education, Sustainability, Finance, Social impact and Other). Ask: *"Which of these areas would you be most interested in investing in or supporting?"* Write the selected category down. This keeps the task aligned with the sample ideas available in the MVP.

**Tasks.** Read each task, start the timer and do not help unless the participant is stuck for more than one minute (then write down that help was needed).

| Task | Instruction to read | Completed when |
|---|---|---|
| T1 | "Find the ideas in [the selected category]." | The list shows only ideas from the selected category. |
| T2 | "Open the idea that interests you most and read its details." | The idea detail page is open. |
| T3 | "Now go back to all the ideas and look for one in a different sector." | The full list is shown again and another category is selected. |

**After the tasks.** Ask:

1. "Did you find an idea relevant to your interests?" (yes / no)
2. "How easy was it to find it, from 1 (very hard) to 5 (very easy)?"
3. "What information would you need to decide whether to contact the student?"
4. "What would you change or add to the platform?"

## Observation sheet

| Participant | Profile | Sector of interest | T1 done / time | T2 done / time | T3 done / time | Help needed | Relevant idea found? | Ease (1–5) | Missing information / suggestions |
|---|---|---|---|---|---|---|---|---|---|
| P1 | | | | | | | | | |
| P2 | | | | | | | | | |
| P3 | | | | | | | | | |
| P4 | | | | | | | | | |
| P5 | | | | | | | | | |

## Results

| Measure | Result |
|---|---|
| Participants | |
| Found a relevant idea with the filter | _ of _ (_%) |
| Success criterion (≥ 75%) | Met / Not met |
| Average ease (1–5) | |
| Tasks that needed help | |

**Conclusion and proposed changes.** Summarise what the results say about H1 and list the changes proposed for the Product Backlog (for example, missing information on the idea detail page or a need for search). Bring them to the Sprint Review and to the next hypothesis review.
