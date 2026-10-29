# Proposal

## Why

Investors need to discover published student ideas and narrow the list to a category of interest. The existing home page is a placeholder, leaving the discovery and category-filtering behavior in US003 (#6) unavailable. This change covers T14 (#21).

## What Changes

- Display published ideas on the discovery page.
- Let an investor select a category and show only ideas in that category.
- Let an investor clear the category filter to restore the full published list.
- Explain when no published ideas match the selected category.

Out of scope: opening an idea detail page (US004, #7), editing ideas or categories (US002, #5), and search, sorting, or pagination, which are not part of US003's specified behavior.

Refs #21; US003 (#6).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ideas`: specify the published idea discovery list, category filtering, clearing the filter, and the no-match message for US003.

## Impact

- `ideas/views.py` and `ideas/urls.py`: provide the discovery list and category filter.
- `templates/ideas/home.html`: render the published ideas, filter control, and empty/no-match states.
- `ideas/tests.py`: cover each US003 acceptance criterion.
- No model or dependency changes are expected; the existing `Idea` and `Category` models support this behavior.
