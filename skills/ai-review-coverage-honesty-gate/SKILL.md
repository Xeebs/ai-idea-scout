---
name: ai-review-coverage-honesty-gate
description: Audits a completed AI code-review's output against the diff it claims to have reviewed, flagging files/sections that were likely truncated or never actually seen by the model when the tool's own output doesn't disclose a gap. Use before merging a large PR that an AI reviewer marked "reviewed" or "passed."
---

# AI Review Coverage Honesty Gate

## When to use this
A PR has already gone through an AI code-review or AI-eval tool (Cursor Bugbot, Qodex, a Claude- or GPT-based reviewer, GitHub Copilot review, PR-Agent, or similar), the tool reported something like "reviewed," "no issues found," or a pass/fail status, and the PR is large enough (big migration, generated code, a huge documentation patch, 1000+ line diff, dozens of files) that you don't fully trust the tool actually saw everything before you merge. Run this skill before merging, not after an incident.

## Inputs
**Data source**: Connected — reads the PR diff directly via the GitHub/GitLab PR API (e.g. `gh pr diff <number>` or the GitLab equivalent) when CLI/API access is available; this part is mature and works today. Falls back to Manual — paste the full diff text — when no API access exists. The AI review tool's own output/comment text is Manual in all cases today: paste the full text of its PR comment(s) or report, since no reviewed-coverage tool currently exposes chunk/coverage metadata through a connector a skill can read.

You need to hand over:
1. The diff — either a PR URL/number (skill fetches it via `gh pr diff`) or the raw diff text pasted in full.
2. The AI review tool's complete output — every comment/report it posted on this PR, pasted in full, not summarized. Partial pastes make this audit unreliable.
3. (Optional, improves accuracy) The name of the review tool and its documented context-window limit or chunk size, if you know it. If omitted, the skill states its assumption explicitly rather than guessing a vendor-specific number it can't verify.

## Procedure
1. **Obtain the diff.** If given a PR link/number and CLI access exists, run `gh pr diff <number>` (or `gh pr view <number> --json files,additions,deletions` for a file list) to get the actual diff. Otherwise use the pasted diff text verbatim — never ask the user to re-describe it from memory.
2. **Inventory the diff.** List every changed file with its added/removed line counts. Estimate total diff size in characters and a rough token estimate (chars ÷ 4 as a standard approximation — state that it's an approximation, not exact).
3. **Determine the coverage budget.** If the user supplied a tool name + known limit, use it and cite it as user-supplied. If not, do not invent a vendor-specific number — state plainly: "No verified context-window/chunk-size limit for <tool> was supplied; using a conservative generic assumption of ~100K tokens of input budget shared across prompt + diff, flagged as unverified." Never present a fabricated vendor limit as fact.
4. **Scan the review tool's output for explicit coverage signals**, in this order of trust:
   a. Explicit disclosure language ("reviewed N of M files," "skipped due to size," "chunk 2 of 4," "truncated") — if present, trust and quote it directly; this is the strongest signal.
   b. Explicit file/line references — build the set of files and line ranges the output actually names or quotes from.
   c. A blanket claim with no file-level detail ("no issues found," "LGTM," "review complete") and no disclosure language — treat as *unconfirmed*, not as proof of full coverage.
5. **Cross-reference every file in the diff inventory (step 2) against the output's referenced set (step 4b/4a):**
   - File named/quoted in the output as reviewed → **CONFIRMED REVIEWED**.
   - File the output *explicitly* names as not yet reviewed, pending, skipped, or cut (step 4a disclosure language) → **DISCLOSED NOT REVIEWED** — quote the tool's own words; this is the highest-confidence status because the tool said it itself, not an inference, and it must never be downgraded to a mere "likely."
   - File not named anywhere in the output, with no disclosure language covering it either → **NOT CONFIRMED** (don't say "skipped" — the tool may have reviewed it without quoting it; say the output gives no evidence either way).
   - File/section whose cumulative position in the diff falls after the estimated coverage budget (step 3) is exceeded, and which the output neither confirms nor explicitly discloses → **LIKELY TRUNCATED** (an inference from size math, stronger than NOT CONFIRMED but weaker than DISCLOSED NOT REVIEWED since the tool didn't say it outright).
6. **Render the verdict** using the rule: if every file is CONFIRMED REVIEWED, verdict is "Disclosed, no action needed." If any file is DISCLOSED NOT REVIEWED or LIKELY TRUNCATED, or more than ~20% of changed files are NOT CONFIRMED with no disclosure language anywhere in the output, verdict is "Likely undisclosed partial coverage — review before merge" (use this verdict even when the gap *was* disclosed by the tool — the point is that an unreviewed file exists and needs human eyes, not that the disclosure itself was dishonest; name explicitly-disclosed files as such in the per-file table rather than implying the tool hid anything). Otherwise "Unknown — insufficient evidence either way," which is itself an actionable finding, not a failure to produce an answer.
7. **Never recommend blocking the merge yourself.** State the verdict and the specific files/sections to check by hand; the decision to merge, wait, or request a fuller re-review is the human's.

## Output format
A single markdown report:

```
## AI Review Coverage Audit — <PR identifier or "pasted diff">

**Diff**: <N files, +A/-D lines, ~T estimated tokens>
**Review tool**: <name, or "unspecified">
**Coverage budget used**: <user-supplied limit, cited> OR <"unverified generic ~100K token assumption">

### Verdict: <Disclosed, no action needed | Likely undisclosed partial coverage — review before merge | Unknown — insufficient evidence>

### Per-file coverage
| File | Status | Note |
|------|--------|------|
| path/to/file.ts | CONFIRMED REVIEWED | quoted in tool output, line 42 |
| path/to/big_migration.sql | LIKELY TRUNCATED | falls past estimated token budget; not named in output |
| path/to/other.md | NOT CONFIRMED | not referenced in output; output gave no file-level detail |

### What to check by hand before merging
- <specific file/section list, prioritized by risk>

### Confidence caveat
<one line stating this is a size/reference-based estimate, not a guarantee, and naming the single biggest source of uncertainty for this specific case — e.g. "no verified context limit for this tool" or "tool may summarize without quoting, which this method can't detect">
```

## Guardrails
- Never state a specific vendor context-window or chunk-size limit unless the user supplied it or it is a model's own publicly documented context window (e.g. a named Claude or GPT model's documented window) — proprietary review-tool limits are often undocumented and change without notice; guessing one and presenting it as fact is worse than flagging it as unverified.
- Never mark a file "SKIPPED" or "NOT REVIEWED" based on mere absence from the output — use "NOT CONFIRMED" instead, since absence of a reference is not proof the model never saw it. Reserve "DISCLOSED NOT REVIEWED" strictly for cases where the tool's own output explicitly says so in quotable words — don't apply it on inference.
- Never treat a blanket "LGTM"/"no issues"/"passed" status as evidence of full coverage on its own — it is exactly the failure mode this skill exists to catch.
- Never recommend or perform a merge-block action — this skill produces a report for a human to act on, not a CI gate decision (the always-on CI version is a separate piece of infrastructure, not this skill).
- Never proceed on a partial paste of the tool's output — if the user's paste looks truncated or is clearly missing sections (e.g. references a chunk count higher than what's pasted), say so and ask for the full output before producing a verdict.
- Never invent file names, line numbers, or diff content not present in the actual diff/output provided.
