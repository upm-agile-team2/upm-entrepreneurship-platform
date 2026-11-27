## Context

T53–T55 provide saved investor profiles and an interest catalogue. The student directory already demonstrates the filter and empty-state interaction.

## Goals / Non-Goals

Expose a student-facing investor directory and profile detail. Investor ownership and editing continue to use the separate profile editor.

## Decisions

- Show saved profiles of active investor accounts to signed-in students. Reuse the profile preview layout for student-facing details and link from investor names in the directory and visible idea feedback.
- Retrieve only public feedback for the profile, newest first. Links point to the corresponding idea and comment. Idea-level visibility continues to govern private feedback.
- Use a GET form with one validated interest selection and a clear link to the unfiltered directory. Retain catalogue entries that currently have no matching profiles and show a distinct no-match state.
- Fetch profile owners and interest tags in batches. Keep names ordered case-insensitively with the account ID as a stable tie-breaker.

## Risks / Trade-offs

Tags remain available after the last investor removes them. This preserves existing filter URLs and produces an explicit no-match result when appropriate.
