# Agent Diff Gate — Pre-Merge Review for Agent-Authored Code

A prompt template for reviewing a single AI-agent-authored (Claude Code, Copilot, Cursor, Codex, or similar) diff or pull request for two specific failure modes before it merges: performance regressions and "LLM-style" UI boilerplate smells. It is deliberately narrow — not a general code review — because these two failure modes recur specifically in agent-authored diffs and get missed by standard CI and standard human review, which aren't tuned to look for them.

## When to use this

Use it right before merging any PR or commit that is agent-authored or suspected to be — tagged via a commit trailer, authored by a bot account, or just "an agent wrote most of this." It works as a one-off manual check even if your team has no CI gate for this at all. Don't use it for routine hand-written PRs (its pattern list is tuned to things agents default to, not general bugs) and don't use it as your only code review step — it's a targeted supplement, not a replacement for normal review.

## What you need to hand over

**Data source: Connected (with a manual fallback).** If you're working in an environment with GitHub CLI (`gh`) access, you can hand over just a PR reference like `owner/repo#123` — the reviewer (you, in a chat tool, or an agent with shell access) runs `gh pr diff owner/repo#123` for the diff and `gh pr view owner/repo#123 --json commits,author,title,body` for authorship metadata. If you don't have CLI/API access to the repo, paste instead:

1. The diff itself — output of `git diff`, `git show <commit>`, or the PR's "Files changed" raw diff.
2. Any commit trailer or bot-account info you can see (e.g., "Co-Authored-By: claude[bot]" or similar) — if you don't have this, say so, don't guess.

Optional but helpful to include:
- The language/stack, if not obvious from file extensions.
- A one-line note on what the change was supposed to accomplish (so a legitimate big refactor doesn't get flagged as smell purely for being large).

## The prompt

Paste this into any AI chat tool along with your diff (and PR reference / commit trailer info if you have it):

> You are reviewing a single AI-agent-authored code diff for pre-merge risk. Do NOT do a general code review (security, correctness, style) — review ONLY for two things: performance-regression risk factors, and "LLM-style" UI boilerplate smells. Follow this procedure exactly:
>
> 1. Determine authorship confidence: look for a commit trailer, bot account, or explicit statement of agent authorship. Label it CONFIRMED (explicit trailer/bot account seen), LIKELY (strong stylistic signal, nothing explicit), or UNCONFIRMED (no signal) — never claim CONFIRMED without literal evidence.
> 2. Scan every changed hunk for performance-regression risk factors: a loop added around a call that used to run once (N+1 pattern), removed/bypassed memoization or caching or an early-return that existed before, new synchronous/blocking I/O in a hot path, new full-object deep copies or string concatenation in a loop where a more efficient pattern existed, new unbounded retry/recursion with no backoff or depth limit, new per-iteration allocation inside a loop over user-scale data. For each hit, cite the exact file, line(s), and snippet, explain the risk in one sentence, and rate severity HIGH/MEDIUM/LOW.
> 3. If the diff touches UI/view-layer files, scan for LLM-style boilerplate smells: a new component that near-duplicates an existing one instead of being parameterized, generic placeholder copy ("Welcome to our app", "Lorem ipsum"), redundant single-child wrapper elements inconsistent with the file's style, reimplementation of a utility/hook that already exists elsewhere in the repo under a new name, naming/structure matching generic training-data conventions rather than this repo's established conventions, or excessive generic try/catch blocks with swallowed/bare-logged errors where the surrounding code doesn't do that. Same citation format and severity scale (HIGH = visibly inconsistent/broken to a user or next reviewer, MEDIUM = maintainability drag, LOW = cosmetic). If the diff has no UI files, state that this section was skipped.
> 4. Don't speculate about runtime impact you can't see in the diff (table size, call frequency, etc.) — say so explicitly rather than asserting false-confidence severity.
> 5. Don't flag a diff as smelly just because it's large — only concrete repeated/generic patterns count.
> 6. Produce a report with these exact sections: a header naming the PR/diff, Authorship confidence line, a Performance Regression Risks table (Severity | File:Line | Snippet | Risk) or "No performance-regression risk factors found", a LLM-Style UI Boilerplate Smells table in the same format (or "No smells found" / "Skipped — no UI files"), one Overall Advisory line (LIKELY SAFE TO MERGE / MERGE WITH FOLLOW-UP / RECOMMEND HOLDING FOR HUMAN REVIEW, tied to the highest severity found, framed as advisory not a decision you're making for the user), and a Notes/Limitations line for anything you couldn't assess from the diff alone.
> 7. Never claim you ran, executed, or benchmarked the code — this is a static, diff-only review. Never approve, merge, or post a comment on the actual PR — you are producing a report for a human to act on.
>
> Here is the diff (and any authorship metadata) to review:
> [paste diff / PR reference / commit trailer info here]

## What you get back

A short structured report: an authorship-confidence line, a table of flagged performance-regression risks (or a clean statement that none were found), a table of flagged UI boilerplate smells (or clean/skipped), one overall advisory line, and any limitations the reviewer hit from only having the diff (not runtime data) to go on. It's meant to be fast — read in under a minute, and specific enough that every flagged line can be checked immediately against the real diff.

## Limits

This is a static review of exactly what's in the diff — it cannot catch a regression whose cause lies outside the changed lines (e.g., a caller elsewhere in the codebase that now calls a changed function in a loop), and it cannot verify real-world severity without an actual before/after benchmark. It is meant to catch the most common, visible agent-default failure patterns fast, not to replace a full performance-regression CI suite or a full human code review.
