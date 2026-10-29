# Tasks

## 1. Discovery query and behavior (T14, #21)

- [x] 1.1 Update the discovery view to provide published ideas and available categories; add a Django test proving the discovery page displays the available published ideas, verifying the test passes
- [x] 1.2 Apply a selected category to the published ideas list; add a Django test proving only ideas in that category are displayed, verifying the test passes
- [x] 1.3 Support clearing the category selection; add a Django test proving the full published list returns after clearing, verifying the test passes
- [x] 1.4 Render an explanatory no-match state for a category with no published ideas; add a Django test asserting the message, verifying the test passes

## 2. Discovery page and integration

- [x] 2.1 Update the home template with the published idea list, category selector, clear-filter option, and empty/no-match messages; add Django response tests for these rendered states, verifying the tests pass
- [x] 2.2 Run `python manage.py test` and check the Definition of Done in the README, verifying all US003 criteria are covered and the full suite passes
