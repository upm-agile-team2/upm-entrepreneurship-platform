# Design

## Context

`ideas.views.home` already queries `Idea` with `select_related("category", "owner")`, filters by a numeric `category` query parameter, returns `ideas.none()` for an unknown or non-numeric value, and passes `selected_category` (a `Category` or `None`). `templates/ideas/home.html` predates that view: it accepts categories as `(value, label)` tuples, guards the detail link with `{% if idea.pk %}`, falls back from `category.name` to `category`, and pairs each visible empty message with a different hidden `data-empty-message`. Some tests still render the template with those tuples and assert the hidden text.

## Goals / Non-Goals

**Goals:**
- The template consumes only model instances, so the view is its single contract.
- Tests exercise the page through the view with stored data and assert visible text.

**Non-Goals:**
- No change to the view's query or filtering logic.
- No client-side (JavaScript) filtering or auto-submit.

## Decisions

- **Mark the selected option with `selected_category == category`.** The view already resolves the query parameter to a `Category` or `None`, so comparing instances is exact. The existing `request.GET.category == category.pk` fallback compares a string with an integer and never matches; it is removed rather than fixed, since an unresolvable value must not mark any option.
- **Choose the empty-state message by `request.GET.category`.** Any non-empty category value with no results shows "No ideas were found in this category."; otherwise "No published ideas yet." This covers both an existing empty category and an unknown value without extra view context.
- **Drop the hidden `data-empty-message` attributes.** Two different strings for one state confuse tests and translations; the visible `role="status"` paragraph is the single source.
- **Shorten card descriptions with `truncatewords:30`.** A presentation choice, not a US003 requirement, so it lives here and not in the spec. Truncation runs before `linebreaksbr` so line breaks are preserved in the shortened text. Alternative considered: CSS line clamping — rejected because it still sends the whole description and is harder to assert in Django tests.
- **Replace `render_to_string` mock tests with `self.client` tests on stored models.** They test the real view-template contract and keep working if the template changes its internals.

## Risks / Trade-offs

- [Word-based truncation can still produce long cards for very long single words] → Acceptable for the MVP; titles and descriptions are short in practice and the detail page shows the full text.
- [Removing mock-data branches breaks any caller that passes tuples] → Only the removed tests did; the view always passes model instances.
