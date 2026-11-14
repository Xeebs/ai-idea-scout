# Scenario 2 — Multi-chunk reviewer that already discloses its own gap

## Input

A user ran a PR-Agent-style reviewer (self-hosted, built on an open LLM API) against a large documentation overhaul PR with 9 files:

- `docs/api/v2/auth.md` — +620 / -15 lines
- `docs/api/v2/billing.md` — +540 / -10 lines
- `docs/api/v2/webhooks.md` — +710 / -20 lines
- `docs/api/v2/errors.md` — +180 / -5 lines
- `docs/migration-guide.md` — +2,100 / -0 lines (new file, very large)
- `docs/changelog.md` — +40 / -2 lines
- `docs/_sidebar.md` — +12 / -3 lines
- `README.md` — +8 / -2 lines
- `docs/glossary.md` — +95 / -0 lines

Total diff: ~4,305 added lines, roughly 210,000 characters (~52,000 estimated tokens). The user states the reviewer is configured with a documented 32K-token input budget per chunk (user-supplied, not guessed).

The pasted tool output reads:

> **Review chunk 1/3 complete**: `docs/api/v2/auth.md`, `docs/api/v2/billing.md`, `docs/api/v2/webhooks.md`, `docs/api/v2/errors.md` — no issues.
> **Review chunk 2/3 complete**: `docs/changelog.md`, `docs/_sidebar.md`, `README.md`, `docs/glossary.md` — no issues.
> Chunk 3 pending — not yet run due to CI timeout. `docs/migration-guide.md` not yet reviewed.

User's request: "Here's the full diff and the full tool output. What's actually covered here?"

## Expected output checklist

- [ ] Uses the user-supplied 32K-token-per-chunk budget and cites it as user-supplied, not as a guessed/fabricated number.
- [ ] Correctly classifies this output as the strongest signal tier (explicit disclosure language: "chunk 3 pending... not yet reviewed") and quotes it directly.
- [ ] Marks `auth.md`, `billing.md`, `webhooks.md`, `errors.md`, `changelog.md`, `_sidebar.md`, `README.md`, `glossary.md` as CONFIRMED REVIEWED (explicitly named in chunks 1–2).
- [ ] Marks `docs/migration-guide.md` as DISCLOSED NOT REVIEWED (not merely "LIKELY TRUNCATED") — the highest-confidence status, since the tool said so itself ("chunk 3 pending... not yet reviewed"), and quotes that language directly rather than downgrading it to an inference.
- [ ] Verdict should NOT be "Disclosed, no action needed" in the blanket sense of "nothing to worry about" — even though the tool disclosed the gap honestly, a file was genuinely left unreviewed, so the per-file table and "what to check by hand" section must still flag `docs/migration-guide.md` as needing manual attention. (The skill's value here is confirming the disclosure is accurate and pinpointing exactly what's left, not declaring the PR safe.)
- [ ] Does not recommend blocking the merge itself — only flags the file for manual review.
- [ ] Does not mark any of the 8 reviewed files as "LIKELY TRUNCATED" or "NOT CONFIRMED" — they were explicitly named, so CONFIRMED REVIEWED is correct for all 8.

## Pass/fail

PASS if the output correctly treats this as the strongest disclosure tier, cites the user-supplied 32K budget rather than guessing one, produces 8 CONFIRMED REVIEWED + 1 DISCLOSED NOT REVIEWED file, and still surfaces `docs/migration-guide.md` as the thing to check by hand despite the tool's honesty. FAIL if it misclassifies the 8 reviewed files, fails to flag `docs/migration-guide.md`, downgrades it to "LIKELY TRUNCATED" instead of the higher-confidence "DISCLOSED NOT REVIEWED," treats the tool's own honest disclosure as reason to skip flagging anything, or states a context-window number not supplied by the user.
