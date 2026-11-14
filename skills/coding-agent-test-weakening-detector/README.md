# Test-Weakening Detector

A paste-into-any-AI-chat-tool prompt that checks a single pull request diff for one specific failure mode: a coding agent (or anyone) making tests pass by weakening or disabling them instead of fixing the underlying code. This is not a general code review — it does exactly one job, on one PR at a time, on demand.

## When to use this

Use it when:
- A pull request was opened by an autonomous coding agent (Claude Code, Copilot, Cursor, Codex, or similar) and touches test files, and you want a second opinion before approving.
- CI flipped from red to green on a PR, but the production-code change doesn't obviously explain why — the fix might be in the test, not the code.
- You're skimming a diff and something about a test file feels off (an assertion that got shorter, a new `skip`, a mock where a real call used to be) and you want a structured check rather than relying on a gut feeling.

Don't use it for anything else — not style review, not security review, not architecture review. If the diff doesn't touch any test or CI-config files, this prompt has nothing to check and will tell you so.

## What you need to hand over

**Data source**: this works two ways. If you have `gh` (the GitHub CLI) installed and authenticated and you're using it inside a coding assistant that can run shell commands, just give the PR reference (`owner/repo#123`) and the diff can be fetched directly — no copy-pasting required. If you're in a plain chat tool with no shell/API access (the normal case for pasting this README into ChatGPT, Gemini, etc.), you must paste the diff yourself: run `git diff`, `git show <sha>`, or copy the PR's "Files changed" raw diff, and paste the whole thing.

Required, one of:
1. A PR reference, if your tool can run `gh pr diff <owner/repo>#<number>` and `gh pr view <owner/repo>#<number> --json title,body` itself.
2. A pasted unified diff — any size, but say if you think it's a partial/truncated copy.

Optional, helps accuracy:
- The PR description or commit messages, if you didn't already fetch them — this lets the check tell the difference between an unexplained weakened test and one with a stated reason ("removing this test, it was flaky — see #412").
- The languages/frameworks involved, if not obvious from the file extensions.

## The prompt

Paste this whole block into your AI tool of choice, then paste your diff (and PR description, if you have one) right after it:

```
You are reviewing ONE pull request diff for a single, narrow failure mode: the author
(possibly an autonomous coding agent) made the test suite pass by weakening or disabling
tests, rather than by fixing the code the tests check. Do not review anything else about
this diff — no style, no security, no architecture. Follow these steps exactly.

STEP 1 — Scope to test-relevant files only. Look only at files whose path contains "test",
"spec", "__tests__", or "tests/"; filenames like *_test.*, *.test.*, *.spec.*; and CI/coverage
config files (.github/workflows/*.yml, pytest.ini, jest.config.*, .coveragerc, codecov.yml).
If none of the changed files match, stop here and say: "No test or CI-config files touched
in this diff — nothing to check," and do not look for findings elsewhere.

STEP 2 — For every scoped file's changed hunks, check specifically for these patterns and
nothing else:
  a) Deleted or commented-out assertions (assert/expect/assertEqual/etc.) with no equivalent
     assertion added elsewhere in the same test.
  b) Loosened assertions — an exact check replaced by something strictly weaker: a type check
     instead of a value check, a widened numeric tolerance, a looser regex, or a tautology
     like assertTrue(True) / expect(true).toBe(true).
  c) New skip/disable/xfail markers (@pytest.mark.skip, @unittest.skip, it.skip/xit,
     describe.skip, @Disabled, t.Skip(), xfail) or a test commented out / wrapped in "if False".
  d) A real function/API/DB call that used to be invoked directly, now replaced by a mock/stub
     that returns a fixed value — especially if that fixed value matches what the changed
     production code now returns.
  e) An expected value that used to be computed (a calculation, a shared fixture, a call to
     the same logic) now a hardcoded literal that happens to match the new actual output
     introduced in this SAME diff.
  f) A timeout, retry count, or tolerance raised by an order of magnitude or more with no
     justification visible in the diff or PR description.
  g) A test or test file deleted outright with no replacement test for the same behavior.
  h) A CI/coverage config change in the same diff that lowers a coverage threshold, disables
     a lint/type-check step, or removes a required check.

For every hit, record: the file path, the line number(s), the EXACT diff line(s) quoted
verbatim, which pattern (a–h) it matched, and a one-sentence plain-language explanation of
why it's suspicious. Never invent a line that isn't literally in the diff you were given.

STEP 3 — If I gave you a PR description or commit messages, check whether any flagged change
has an explicit stated justification there (e.g., "removing this test, it was flaky and
duplicated by #412"). If so, keep the finding but mark its confidence LOW and quote the
justification — don't delete the finding just because an explanation exists; I still want
to see it.

STEP 4 — Never claim intent. Say what pattern matched and where — never "the agent cheated"
or "this is dishonest." The same literal change can be a legitimate refactor or a gamed test;
your job is to surface it, not to convict anyone.

STEP 5 — If the diff looks partial or truncated (cuts off mid-hunk, or I told you it's
incomplete), say so explicitly and scope your report to only what you actually saw.

STEP 6 — Output in exactly this format:

# Test-Weakening Report — <PR ref or "pasted diff">

**Test/CI files touched**: <count> (list them if 10 or fewer, else count + a few examples)
**Findings**: <count> (broken down by High/Medium/Low confidence)

## Findings
| Confidence | File:Line | Pattern | Quoted diff | Why it's suspicious |
|---|---|---|---|---|
| <High/Medium/Low> | <path:line> | <a–h short name> | `<exact diff line(s)>` | <one sentence> |
(or, if none: "No test-weakening patterns found in the scoped files.")

## Overall Recommendation
<one of: CLEAR — no action needed | REQUEST JUSTIFICATION — ask the author to explain the
flagged change(s) before approving | HOLD FOR HUMAN REVIEW — one or more HIGH-confidence
findings warrant a closer look before merge>

## Coverage Notes
<state whether the full diff was reviewed, or only a partial/truncated copy>

Here is the diff (and PR description, if any):
[PASTE YOUR DIFF HERE]
```

## Guardrails — the AI should never

- Claim the author "cheated" or "lied" — only report pattern, location, and confidence.
- Invent a diff line, file path, or line number not literally present in what you pasted.
- Approve, merge, or comment on the PR itself — this only produces a report for you to act on.
- Treat a stated justification as automatic clearance — it should lower confidence, not delete the finding.
- Flag anything outside test/spec/CI-config files as a "test-weakening" finding.
- Report as if it reviewed the whole PR when you told it the diff was partial.

## Why this is narrow on purpose

This is not a general PR reviewer and not a CI gate you install — it's a single, on-demand second opinion for the one failure mode that's hardest to catch by skimming: a test suite that looks green because it was quietly made easier to pass, not because the underlying bug was fixed. If you want this running automatically on every PR instead of pasted in ad hoc, that's the larger "TestGuard" CI-gate version of this idea — a GitHub Action, not a chat prompt.
