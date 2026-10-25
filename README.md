# UPM Student Entrepreneurship Platform

Web platform for the UPM Innovation Department where students publish their entrepreneurial ideas, receive feedback and connect with potential investors.

Project for **Agile Methods for Software Development: Agile Techniques and Agile Usability** (UPM, 2026-2027) — **Team 2**.

## Team

- Miguel Ángel Martínez Simón
- Javier Campos Soto
- Jorge Benito Díaz
- Alex Ortega Leonato
- Zijie Liang
- Gabriel Peña Sánchez
- Argenis Ronaldo Andrade Zambrano
- Samuel Pérez Vos

## Way of working

Scrum integrated with Lean UX. Sprints last two weeks: week 1 to build the MVP, week 2 to validate it with users and improve it.

| Hypothesis | Business outcome | Sprint |
|---|---|---|
| H1 | Reach 20 published ideas per month | Sprint 1 |
| H2 | At least 20% of the ideas that receive feedback are edited by their author afterwards | Sprint 2 |
| H3 | At least 15% of investor visits end with a student profile being opened | Sprint 3 |

### Sprint 1 goal

Deliver a working MVP in which students can create an account and publish and edit an entrepreneurial idea, and investors can browse the published ideas, filter them by category and view their details, so that the team can validate hypothesis H1 with real users during the second week of the sprint.

## Task board

The Sprint Backlog lives in the organization's GitHub Project (**Team 2 – Sprint Board**):

- Each **user story** is an issue labelled `user-story` (e.g. `US001 Publish an idea`), with its acceptance criteria as a checklist.
- Each **task** is an issue labelled `task` (e.g. `T10 Implement publishing an idea`) that refers to its user story.
- Columns: **Todo → In Progress → In Review → Done**.

## Development workflow

1. Assign yourself an issue from the board and move it to **In Progress**.
2. Create a branch from `main` named after the task, e.g. `T10-publish-idea`.
3. Open a pull request that includes `Closes #<issue number>` and move the issue to **In Review**.
4. Another team member reviews and merges the pull request; the issue moves to **Done**.

### Definition of Done

1. All acceptance criteria of the user story are met.
2. Each acceptance criterion has been tested and all tests pass.
3. The code is in this repository and has been reviewed by at least one other team member.
4. The story works in the integrated MVP, not only on a developer's machine.
5. The screen follows the wireframes agreed in the UX Design Studio.
6. The story has been demonstrated and accepted by the Product Owner in the Sprint Review.

## Tech stack

| Area | Choice |
|---|---|
| Backend and web | Python + Django |
| Frontend | Django templates + Bootstrap |
| Database | SQLite (development), PostgreSQL (deployment) |
| Board and code | GitHub repository + GitHub Projects + Issues |
| Testing and CI | Django tests + GitHub Actions |
| Deployment | Render (free tier) |

## Getting started

The Django project and the setup instructions are added in task **T01**.
