# Tasks

## 1. Data model (T09, #16)

- [x] 1.1 Add `Category` and `Idea` models in `ideas/models.py` as described in design.md, register both in the admin, and verify `python manage.py makemigrations ideas` generates the schema migration
- [x] 1.2 Add a reversible data migration that inserts the initial categories and verify `python manage.py migrate` creates them and `migrate ideas 0001` removes them
- [x] 1.3 Add model tests in `ideas/tests.py`: an idea is stored with its owner, optional category and an automatic publication date; a category in use cannot be deleted; category names are unique ignoring case. Verify they pass

## 2. Publishing with validation (T10, #17)

- [x] 2.1 Add `IdeaForm` (title, description, category, in that order) with required title and description that reject whitespace-only values, and verify with form tests for each missing field
- [x] 2.2 Add the `publish_idea` view and the `ideas:publish` URL: signed-in students create the idea with themselves as owner and are redirected to `ideas:home` with a success message; anonymous visitors are redirected to login; investors get 403. Verify with view tests
- [x] 2.3 Add a test for the criterion *Submit an idea*: a signed-in student submits a valid idea, it is saved with `owner`, appears for another user, and is stored with the chosen category when one is selected
- [x] 2.4 Add tests for the criterion *Require essential information*: submitting without a title, without a description, and without both re-renders the form with a message per missing field and creates no idea

## 3. Submission form screen (T11, #18)

- [x] 3.1 Create `templates/ideas/idea_form.html` following the agreed wireframe (Title, Description, Category dropdown with an empty choice, **Publish** button, in that order) using Bootstrap 5 and showing field errors, and verify the page renders in a view test that checks the field order and the button
- [x] 3.2 Add a "Publish an idea" link to `templates/base.html` for signed-in students only and verify with tests that students see it and anonymous visitors and investors do not
- [x] 3.3 Open the form in the browser with `python manage.py runserver` as a student, publish a valid idea and try an invalid one, and confirm the behaviour matches the wireframe and the acceptance criteria

## 4. Final checks

- [x] 4.1 Run `python manage.py makemigrations --check --dry-run` and verify it reports no changes
- [x] 4.2 Run `python manage.py test` and verify the whole suite passes, including the existing `accounts` tests
- [x] 4.3 Run `openspec validate --all` and verify there are no errors
- [x] 4.4 Check the Definition of Done in the README: every acceptance criterion of US001 is covered by a passing test and the screen follows the wireframe

## Workflow follow-up

- Open a pull request with `Refs #4` and `Closes #16, closes #17, closes #18`, and ask a team member to review it.
- Archive the change with `/opsx:archive` once the pull request is merged.
