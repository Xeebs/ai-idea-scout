# AI Review Coverage Honesty Gate

A prompt template for auditing whether an AI code-review tool (Cursor Bugbot, Qodex, a Claude- or GPT-based reviewer, GitHub Copilot review, PR-Agent, or similar) actually saw the entire diff it claims to have reviewed — or whether a large PR got silently truncated or chunked while the tool still reported a clean "reviewed" or "passed" status. Paste this whole document into any AI chat tool, then provide the two inputs it asks for.

## When to use this

Use this before merging any PR where an AI review/eval tool gave a pass, "LGTM," or "no issues found" verdict and the PR is large — a big migration, a generated-code dump, a huge documentation patch, or anything in the range of 1,000+ changed lines or dozens of files. That's exactly the size where review tools are most likely to silently drop coverage while still reporting success, because the diff exceeds the model's context window and the tool doesn't always disclose the cut.

Don't use this on small, routine PRs — the failure mode this catches only shows up when diff size is plausibly near or past a model's context budget.

## What you need to provide

This skill needs two things, pasted or linked:

1. **The diff.** Either a link/number to the PR (if the assistant you're using has a way to fetch it, e.g. via a GitHub CLI or API it has access to) or the full raw diff text, pasted completely — not a summary of it.
2. **The AI review tool's complete output.** Every comment or report it posted on that PR, pasted in full. A partial paste produces an unreliable audit — if you're missing part of the tool's output, say so and get the rest first.

Optionally, if you know it, name the review tool and its documented context-window or chunk-size limit. If you don't know it, the assistant should say so explicitly rather than guessing a number for a proprietary tool's internal limits — those aren't usually public and change without notice.

## What the assistant should do (the procedure)

Give the assistant this exact procedure:

1. Build an inventory of every file changed in the diff, with added/removed line counts, and a rough token estimate for the whole diff (characters divided by roughly 4, stated as an approximation).
2. Establish a coverage budget: use a user-supplied tool limit if given, citing it as user-supplied; otherwise state plainly that no verified limit exists for this tool and use a conservative, clearly-labeled generic assumption (e.g. "~100K tokens, unverified") rather than inventing a specific vendor number.
3. Read through the AI review tool's pasted output and classify its coverage signal:
   - Strongest: explicit disclosure language like "reviewed N of M files," "skipped due to size," "chunk 2 of 4," "truncated" — quote it directly.
   - Medium: specific file names or line numbers actually referenced or quoted in the output — build the set of files it demonstrably touched.
   - Weakest: a blanket "no issues found" / "LGTM" / "passed" with no file-level detail and no disclosure language — this is NOT proof of full coverage.
4. Cross-reference every file in the diff inventory against the files the output actually referenced:
   - Named/quoted in the output as reviewed → CONFIRMED REVIEWED.
   - Explicitly named by the output itself as not-yet-reviewed, pending, or skipped → DISCLOSED NOT REVIEWED. Quote the tool's own words. This is the highest-confidence status — never downgrade it to a mere "likely," since the tool said it outright.
   - Not named anywhere, with no disclosure language covering it → NOT CONFIRMED (never say "skipped" — the tool might have reviewed it silently; the honest label is that there's no evidence either way).
   - Falls past the estimated coverage budget in cumulative diff position, with no disclosure either way → LIKELY TRUNCATED, an inference from size math — stronger than "not confirmed," weaker than "disclosed not reviewed."
5. Decide the overall verdict:
   - **Disclosed, no action needed** — every single file is CONFIRMED REVIEWED.
   - **Likely undisclosed partial coverage — review before merge** — any file is DISCLOSED NOT REVIEWED or LIKELY TRUNCATED, or more than roughly 20% of changed files are NOT CONFIRMED with zero disclosure language anywhere in the output. Use this verdict even when the gap was disclosed honestly by the tool — the point is an unreviewed file still exists and needs a human to look at it, not that the tool lied. Name the disclosed files as disclosed, don't imply concealment where there was none.
   - **Unknown — insufficient evidence** — not enough signal either way; this is still a useful, actionable answer, not a non-answer.
6. Never recommend blocking the merge directly — just report the verdict and the specific files to check by hand. The merge decision stays with the human.

## What the output should look like

A single report, structured like this:

```
## AI Review Coverage Audit — <PR identifier or "pasted diff">

**Diff**: <N files, +A/-D lines, ~T estimated tokens>
**Review tool**: <name, or "unspecified">
**Coverage budget used**: <user-supplied limit, cited> OR <"unverified generic ~100K token assumption">

### Verdict: <one of the three verdicts above>

### Per-file coverage
| File | Status | Note |
|------|--------|------|
| path/to/file.ts | CONFIRMED REVIEWED | quoted in tool output, line 42 |
| path/to/big_migration.sql | LIKELY TRUNCATED | falls past estimated token budget; not named in output |
| path/to/other.md | NOT CONFIRMED | not referenced; output gave no file-level detail |

### What to check by hand before merging
- <specific files/sections, prioritized by risk>

### Confidence caveat
<one line naming the biggest source of uncertainty for this specific case>
```

## Guardrails — what the assistant must never do

- Never state a specific proprietary review-tool context-window or chunk-size limit as fact unless the user supplied it. Those limits are usually undocumented and change without notice; a well-known model's own publicly documented context window (e.g. a named Claude or GPT model's stated window) is fine to cite, a vendor's internal review-tool chunking behavior is not something to guess.
- Never label a file "SKIPPED" or "NOT REVIEWED" based on mere absence from the output — the correct label when there's no reference to it is "NOT CONFIRMED." Reserve "DISCLOSED NOT REVIEWED" strictly for when the tool's own output explicitly says so in quotable words.
- Never treat a blanket "LGTM" or "no issues found" as proof of full coverage by itself — that exact pattern is the failure mode this whole audit exists to catch.
- Never recommend or imply a merge-block decision — produce the report; the human decides whether to merge, wait, or demand a re-review.
- Never proceed to a verdict on an incomplete paste of the tool's output — if the output references more chunks/sections than what was actually pasted, say so and ask for the rest first.
- Never invent file names, line numbers, or diff contents that aren't actually present in what was provided.

## Example trigger phrase

"Here's PR #4821, a 2,400-line auto-generated database migration. Qodex reviewed it and said 'No issues found.' Here's the full diff and here's Qodex's full comment — did it actually see all of it?"
