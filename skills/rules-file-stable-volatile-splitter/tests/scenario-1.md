# Scenario 1 — Clear-cut split (mid-size repo AGENTS.md)

## Input

```markdown
# AGENTS.md

## Build & Test
- Build: `pnpm build`
- Test: `pnpm test -- --runInBand`
- Lint: `pnpm lint:fix` before every commit
- Never run `pnpm publish` directly — always go through `scripts/release.sh`

## Architecture
- `packages/core` has no dependency on `packages/ui` — never add one
- All API calls go through `lib/http-client.ts`, never raw `fetch`
- Feature flags live in `config/flags.ts` and must default to `false`

## Code Style
- Prefer named exports over default exports
- Error messages must be user-facing-safe — never leak stack traces to the client

## Current Status (as of 2026-10-02)
- TODO: migrate `lib/legacy-auth.ts` off the old session format — ticket PR-884
- WIP: the billing refactor branch `feat/billing-v2` is mid-migration, don't touch `lib/billing/*` until it merges
- As of this week we have 3 failing tests in `tests/checkout.spec.ts`, being tracked in PR-901
- File count snapshot: 212 files, 14 TODOs open in codebase as of last scan

## Review Checklist
- [ ] Check PR-884 migration status before touching auth
- [ ] Confirm PR-901 checkout fixes landed before next release cut
```

## Expected output criteria

- The **Build & Test**, **Architecture**, and **Code Style** sections (8 lines total) land entirely in the STABLE draft, unchanged in substance and in original order.
- The entire **Current Status (as of 2026-10-02)** section (4 lines: migrate legacy-auth TODO, billing WIP, failing-tests note, file-count snapshot) lands in the VOLATILE draft (`STATE.md`), reorganized under headings like `## Open TODOs` / `## Recent Changes` rather than kept as one dumped block.
- The **Review Checklist** section (2 checklist items referencing PR-884/PR-901) is classified VOLATILE, not left in the stable file — these are task-tracking items tied to specific PRs, not durable policy.
- No line is dropped: every one of the ~16 content lines appears in exactly one of stable / volatile / ambiguous.
- The ambiguous table is empty or near-empty ("none" or very few rows) — nothing in this input is genuinely a mixed/unclear case.
- The summary count line correctly reflects roughly 8 stable, ~6 volatile, 0 ambiguous (exact wording may vary, but the stable count must be clearly smaller than the original and the volatile content must be fully accounted for).
- Nothing is invented: no new build commands, no new TODOs, no new rules not present in the input.
