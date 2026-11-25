# Tasks

These records were added after implementation. Checked items are supported by the current code, test results, or supplied screenshots, not by an earlier proposal approval. T77 (#130) provides the schema, validation, and persistence; this checklist records T78 (#131), US0034 (#105).

## 1. Profile editor and saved links

- [x] 1.1 Expose the four bound social fields and render them through the shared field partial. Verify `test_editor_uses_styled_project_and_experience_fields` checks all four labels and input names; retain T77's passing `test_editor_post_creates_updates_and_clears_social_media_urls` for the save criterion.
- [x] 1.2 Show field-level URL errors without discarding entered values. Verify `test_editor_displays_social_url_errors_and_preserves_entered_values` passes; browser screenshots also show the invalid GitHub input and its inline message.

## 2. Profile icons and external navigation

- [x] 2.1 Prepare available links in the shared owner/investor context and hide unfilled platforms and the empty section. Verify `test_owner_and_investor_see_clickable_social_icons`, `test_profile_only_displays_filled_social_icons_and_hides_empty_section`, and `test_profile_does_not_render_invalid_urls_stored_outside_the_form` pass for the display criterion.
- [x] 2.2 Render platform SVGs with visible names, using existing Bootstrap layout, and retain icon attribution. Verify `social_icon.html` contains the four icons, `docs/licenses/bootstrap-icons.txt` contains the license, and supplied screenshots show the owner and investor layouts.
- [x] 2.3 Link each icon to its saved URL with new-tab attributes and accessible new-tab text. Verify `test_owner_and_investor_see_clickable_social_icons` checks the four destinations and external-link attributes for the open-link criterion.
- [ ] 2.4 Complete browser-click acceptance as an investor viewing another student's profile. Click each available icon and confirm a new tab opens its saved destination. The supplied screenshots establish visibility but do not independently establish actual navigation.

## 3. Integration verification and review

- [x] 3.1 Deliver the issue-linked proposal, three acceptance requirements, design, and this evidence-based checklist. Verify the artifacts describe the existing implementation and explicitly identify their retrospective status.
- [x] 3.2 Run `openspec validate profile-social-links-ui --strict`, `openspec validate --all`, and `git diff --check`. For OpenSpec 2.1.1 compatibility, explicitly mark the existing experiment and demo-seeding changes `skip_specs: true`, consistent with their original proposals. Strict validation passed for this change, and repository-wide validation passed all 20 items after adding the companion T77 documentation.
- [x] 3.3 Run `python manage.py test` and `python manage.py makemigrations --check --dry-run`. The unchanged implementation passed all 239 tests and reported `No changes detected` before these documentation-only additions.
- [ ] 3.4 Check the README Definition of Done with the team: obtain teammate review and merge, confirm behavior in the integrated MVP and alignment with agreed wireframes, and obtain Product Owner acceptance in Sprint Review. Verify through the PR, integrated environment, and Sprint Review record rather than local test results alone.

## Workflow follow-up

- Submit `T77-T78-profile-social-media` to `main` as one combined PR, using `Closes #130`, `Closes #131`, and `Supersedes #135`. Include both tasks' code and documents; close the old backend-only PR without merging it. Inspect the complete diff against main before merging.
- After team review and acceptance, archive this change and synchronize its delta through the archive workflow.
