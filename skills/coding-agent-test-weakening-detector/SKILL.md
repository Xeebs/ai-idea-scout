---
name: coding-agent-test-weakening-detector
description: Scans a single agent-authored PR diff (or pasted patch) for signs the coding agent weakened, disabled, or gamed its own tests to force CI green — deleted assertions, new skip/xfail decorators, mocks replacing real calls, hardcoded expected values. Use when a human reviewer wants a fast, ad-hoc check on one PR before approving, without wiring up a full CI gate.
---

# Test-Weakening Detector

## When to use this
A reviewer is looking at a single pull request (opened by a coding agent, or suspected to be, or just touching test files in a way that looks off) and wants a targeted check for one specific failure mode: the agent made its own tests pass by weakening them rather than by fixing the underlying code. Use this on demand, PR by PR — it is not a continuously running CI gate, and it is not a general code-quality or security review. Reach for it specifically when:
- A PR is tagged, bot-authored, or known to come from an autonomous coding agent and touches `test`/`spec` files.
- CI went from red to green on a PR with no corresponding change to the production code that would plausibly explain the fix.
- A reviewer has a vague "this test file looks different than I'd expect" feeling and wants a structured second opinion before approving.

Do not use this for a general PR review (style, security, architecture) — it is deliberately narrow to one failure mode. Do not use it on diffs that touch no test, spec, or CI-config files — it will have nothing to check.

## Inputs
**Data source**: Connected — GitHub's REST/Actions API (mature) via the `gh` CLI, when the user gives a PR reference, to read the diff directly with no manual paste required. Falls back to Manual — a pasted unified diff/patch — when there's no GitHub access or the user is working outside GitHub.

Required, one of:
1. A PR reference (`owner/repo#123`) — if `gh` is installed and authenticated, run `gh pr diff <owner/repo>#<number>` to fetch the diff and `gh pr view <owner/repo>#<number> --json title,body` for the PR description.
2. A pasted unified diff (`git diff`, `git show <sha>`, or a PR's raw "Files changed" diff) — any size, but note in the output if it looks truncated.

Optional, improves accuracy:
- The PR description or commit messages, if not already fetched via `gh` — used to check whether a test change has a stated justification (e.g., "removing flaky test", "superseded by #456").
- Which languages/frameworks are in play, if not obvious from file extensions (helps match the right skip/mock syntax).

## Procedure
1. **Obtain the diff.** If given a PR reference and `gh` is available, run `gh pr diff` and `gh pr view --json title,body,commits`. If `gh` errors or isn't available, ask the user to paste the diff instead — never fabricate diff content.
2. **Scope to test-relevant hunks.** Filter to files matching common test/CI patterns: path contains `test`, `spec`, `__tests__`, `tests/`; filenames like `*_test.*`, `*.test.*`, `*.spec.*`; and CI/coverage config files (`.github/workflows/*.yml`, `pytest.ini`, `jest.config.*`, `.coveragerc`, `codecov.yml`). If zero such files appear in the diff, stop and report "No test or CI-config files touched in this diff — nothing to check" rather than forcing a finding elsewhere.
3. **Apply the test-weakening checklist to every scoped hunk.** For each, check specifically for:
   - **Deleted or commented-out assertions**: a removed `assert`/`expect`/`assertEqual`/`should.equal`-style line with no equivalent assertion added elsewhere in the same test.
   - **Loosened assertions**: an exact-equality or specific-value check replaced by something strictly weaker — a type check instead of a value check, a widened numeric range/tolerance, a regex made more permissive, or a tautology (`assertTrue(True)`, `expect(true).toBe(true)`).
   - **New skip/disable/xfail markers**: `@pytest.mark.skip`, `@unittest.skip`, `it.skip`/`xit`/`describe.skip`, `@Disabled`, `t.Skip()`, `xfail`, or a test wrapped in `if False:` / commented out entirely.
   - **Mocking out the thing under test**: a real function/API/DB call that was previously invoked directly now replaced by a mock/stub/fake that returns a fixed value — especially when that fixed value matches what the production code under test now returns.
   - **Hardcoded expected values replacing computed ones**: an expected value that used to be derived (a calculation, a call to the same logic under test, a fixture) now a literal that happens to match the actual output introduced in the *same* diff.
   - **Inflated thresholds/timeouts**: a timeout, retry count, or tolerance value increased by an order of magnitude or more with no corresponding justification visible in the diff or PR description.
   - **Test or test file deletion** with no replacement test covering the same behavior.
   - **CI/coverage config loosened**: a lowered `fail_under` / coverage threshold, a disabled lint/type-check step, or a required check removed from a workflow file, in the same diff as production code changes.
   For every hit, record: file path, line number(s) from the diff, the exact quoted diff line(s), which checklist pattern matched, and a one-sentence plain-language explanation of why it's suspicious.
4. **Check for stated justification before finalizing confidence.** If the PR description or a commit message explicitly explains a flagged change (e.g., "removing this test — it was flaky and duplicated by #412", "increasing timeout because the new retry logic is intentionally slower"), lower that finding's confidence to `LOW` and note the stated justification verbatim rather than dropping the finding — the human reviewer should still see it, just with context.
5. **Never speculate about intent.** Report what pattern matched and where, not a claim that the agent "cheated" or "lied" — the same literal change can be a legitimate refactor or a gamed test; the skill's job is to surface it for a human to judge, not to convict.
6. **If the diff is large or looks truncated** (abrupt cutoff mid-hunk, a "diff too large to display" marker, or the user says it's partial), say so explicitly in the output and scope the report to what was actually reviewed — don't imply full coverage of a PR you only saw part of.
7. **Produce the output report** in the fixed format below, then give one overall recommendation line.

## Output format
```
# Test-Weakening Report — <PR ref or "pasted diff">

**Test/CI files touched**: <count> (<list if ≤10, else count + representative sample>)
**Findings**: <count> (<High>/<Medium>/<Low> confidence breakdown)

## Findings
| Confidence | File:Line | Pattern | Quoted diff | Why it's suspicious |
|---|---|---|---|---|
| HIGH | tests/test_billing.py:34 | Deleted assertion | `- assert invoice.total == 149.99` | The exact-value check on invoice total was removed with no replacement assertion in the same test. |
| LOW | tests/test_retry.py:12 | Inflated timeout | `- timeout=5\n+ timeout=120` | Timeout raised 24x; PR description states "retry logic intentionally slower now" — plausible but worth a second look. |
(or: "No test-weakening patterns found in the scoped files.")

## Overall Recommendation
<CLEAR — no action needed | REQUEST JUSTIFICATION — ask the author to explain the flagged change(s) before approving | HOLD FOR HUMAN REVIEW — one or more HIGH-confidence findings warrant a closer look before merge>

## Coverage Notes
<e.g., "Diff reviewed in full" or "Diff appeared truncated after line 400 — review only covers what was shown.">
```

## Guardrails
- Never claim malicious intent — report pattern + location + confidence, never "the agent cheated" or "the agent lied."
- Never fabricate a diff, file path, or line number — every finding must quote an actual line from the diff that was provided or fetched.
- Never approve, merge, comment on, or close the PR — this produces a report for a human to act on; it has no merge authority and should never claim one.
- Never treat a stated justification as automatic clearance — lower confidence, don't delete the finding; the human reviewer decides whether the justification holds up.
- Never flag a change outside test/spec/CI-config files as a "test-weakening" finding — if something else looks wrong in the diff, that's a different review's job.
- If zero test/CI files are touched, say so and stop rather than forcing findings elsewhere in the diff.
- If the diff is partial/truncated, say so explicitly rather than reporting as if full coverage was achieved.
