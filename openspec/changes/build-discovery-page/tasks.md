# Tasks

## 1. Category filter (T15, #22)

- [x] 1.1 Render the filter options from stored `Category` instances only (remove the tuple branch); add a Django response test asserting every stored category is offered as an option, verifying it passes
- [x] 1.2 Mark the option matching `selected_category` as selected and remove the string-vs-integer `request.GET.category` comparison; add a Django response test asserting only the chosen category is selected after filtering, verifying it passes
- [x] 1.3 Keep the existing filter and clear-filter tests passing (`test_category_filter_shows_only_ideas_in_selected_category`, `test_clearing_category_filter_restores_all_ideas`)

## 2. Empty states

- [x] 2.1 Show "No ideas were found in this category." for any non-empty category value with no results and drop the hidden `data-empty-message` attributes; add Django response tests for an existing empty category, a non-numeric value and an unknown numeric id, verifying they pass
- [x] 2.2 Keep "No published ideas yet." when no category is requested and nothing is published; update `test_discovery_controls_and_empty_state_render` to assert the visible text, verifying it passes

## 3. Idea cards

- [x] 3.1 Remove the `idea.pk` guard and `category.name` fallback so every card links to its detail page and shows its category badge; add a Django response test asserting the badge, verifying it passes alongside `test_idea_card_links_to_its_detail_page`
- [x] 3.2 Shorten card descriptions with `truncatewords:30` before `linebreaksbr`; add a Django response test with a 40-word description asserting the cut-off, verifying it passes

## 4. Clean-up and integration

- [x] 4.1 Delete the `render_to_string` mock-tuple tests and the imports they alone used (`render_to_string`, `RequestFactory`, `AnonymousUser`), verifying no remaining test references them
- [x] 4.2 Run `python manage.py test` and `openspec validate --all`, and check the Definition of Done in the README, verifying all US003 criteria are covered and the full suite passes

## Workflow follow-up

- Push to the T15 pull request (#38), which closes #22, and get it reviewed by another team member.
- Archive the change after the pull request is merged.
