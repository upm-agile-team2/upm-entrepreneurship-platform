# Design

The edit endpoint uses the existing `IdeaForm` as a bound `ModelForm` with the selected `Idea` instance. The view requires authentication, checks the student role, then fetches the idea and checks ownership before handling either GET or POST. Both a non-student and a non-owner receive `PermissionDenied` (HTTP 403).

On a valid POST, save the form and redirect to the home page with a success message. Invalid POSTs render the shared idea form, which renders each field's validation errors inline. The form page accepts a heading and submit label in context so publish and edit can use the same layout while presenting the correct action.

No model or migration changes are needed. Django's required `CharField` cleaning strips surrounding whitespace, so whitespace-only titles and descriptions fail required validation.
