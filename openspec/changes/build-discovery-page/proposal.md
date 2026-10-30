# Proposal

## Why

The discovery page was built in two halves: a presentation-only template with mock data (#29) and a database-backed list with category filtering (T14, #21). The template still carries the mock-data branches, and some states of the US003 criteria are only partly covered. This change covers T15 (#22) and finishes the discovery page on top of the `Idea` and `Category` models.

## What Changes

- Render the category filter from the stored categories only and keep the selected category marked in the filter after the list updates.
- Show the no-match message whenever the requested category matches no ideas, including a category value that does not identify any stored category.
- Show one visible message per empty state (no published ideas, no matching ideas) instead of a visible message plus a different hidden one.
- Shorten long descriptions on the idea cards; the full description stays on the idea detail page.
- Replace the tests that render the template with mock tuples by tests that use stored ideas and categories.

Out of scope: the idea detail page itself (US004, #7, T16 #23), search, sorting, pagination, multi-category filters, and any change to how ideas are published or edited.

Refs #22; US003 (#6).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: the US003 requirements "Filter by category" and "No matching ideas" gain scenarios for showing the selected category and for a category value that matches no stored category.

## Impact

- `templates/ideas/home.html`: remove mock-data branches, mark the selected category, unify empty-state messages, shorten card descriptions.
- `ideas/tests.py`: replace mock-context template tests with model-based response tests.
- No model, migration, URL or dependency changes.
