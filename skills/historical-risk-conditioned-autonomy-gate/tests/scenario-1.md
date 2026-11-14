# Scenario 1 — Mixed PR with one recently hotfixed path (manual mode)

## Setup
A mid-size SaaS team runs an AI coding agent that opens PRs for small feature work and dependency bumps. They currently auto-merge anything under 50 changed lines. An agent just opened a PR touching three files, and the team pastes this into a chat tool (no live repo access) to sanity-check whether their static 50-line rule is actually safe here, before deciding whether to invest in the full always-on gate.

## Input handed to the skill

```
PR touches these paths:
- package.json (dependency version bump, 2 lines changed)
- src/billing/webhook.ts (added a new field to the Stripe webhook handler, 18 lines changed)
- src/billing/webhook.test.ts (added a test for the new field, 22 lines changed)

History:
- package.json: 40 clean dependency bumps in a row, no reverts, none ever.
- src/billing/webhook.ts: 20 past changes; 1 revert and 1 hotfix in that window, most recent hotfix was 12 days ago (a null-pointer issue in webhook signature verification).
- src/billing/webhook.test.ts: 8 past changes, all clean, no reverts or hotfixes.

Our current static policy: diffs under 50 total changed lines auto-merge. This PR is 42 lines total, so it would auto-merge today.
```

## Expected output (pass/fail criteria)

Pass requires ALL of the following:
- [ ] Per-path risk table lists all three files with distinct risk levels: `package.json` = LOW, `src/billing/webhook.ts` = HIGH (hotfix within 90 days), `src/billing/webhook.test.ts` = LOW or MEDIUM (acceptable either way given only 8 past changes — reviewer should accept LOW since zero reverts, 8≥5 threshold).
- [ ] Aggregate PR verdict is **BLOCK — HUMAN REVIEW REQUIRED** (driven by the weakest-link rule on `webhook.ts`'s HIGH risk) — NOT averaged down to flag or approve.
- [ ] Reasoning explicitly names `src/billing/webhook.ts` and the 12-day-old hotfix as the deciding factor.
- [ ] Static-policy comparison explicitly states this disagrees with the team's 50-line auto-merge rule, and explains why (the rule would have let a recently-hotfixed file through).
- [ ] No revert/hotfix numbers are invented beyond what was given — e.g., the skill does not claim a specific date for the revert on webhook.ts since none was given, only "12 days ago" for the hotfix.
- [ ] Output includes the required Caveat line about this being a one-time check, not a running ledger.

Fail if: the verdict comes out as APPROVE or is averaged/blended across the three files, if any risk level is assigned without citing the specific evidence given, or if the static-policy comparison is omitted despite one being supplied.
