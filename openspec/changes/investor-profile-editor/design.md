## Context

Student profiles already have separate views for editing and viewing. Investor accounts currently have no saved profile information.

## Goals / Non-Goals

An investor can manage their own profile using the existing account navigation and form styles. US025 and US026 cover discovery and access by students.

## Decisions

- Store an optional biography, experience, past projects, and support offered in a one-to-one profile. Use plain text for the narrative fields so the editor can use ordinary text areas.
- Store interests as related tags with a unique case-folded key. Investors enter a comma-separated list and can use the editor on a fresh installation without a seeded catalogue. The same tags can support exact filtering across SQLite and PostgreSQL.
- Derive the owner from the authenticated session. Save profile fields and interests together. Keep incomplete profiles displayable for gradual completion.

## Risks / Trade-offs

Interest names are user-entered. Normalize whitespace and casing for matching, retain a display label, and limit the number and length of entries.

## Migration Plan

Apply the new accounts migration before opening the editor. Existing accounts and student profiles require no data migration.
