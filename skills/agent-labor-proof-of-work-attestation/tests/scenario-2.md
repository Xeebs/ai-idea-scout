# Scenario 2 — Code-fix bounty with a full raw trace that contains a hidden logical gap

## Context
A decentralized compute network pays agents for completing GitHub issue bounties. An agent claims a $150 bounty for fixing a failing unit test, and submits what looks like a detailed, full execution trace (raw tool calls included) requesting escrow release. The reviewer pastes the issue + trace into the skill before approving, expecting it to be a slam-dunk STRONG case because the trace looks thorough.

## Inputs to paste

**Task description / acceptance criteria:**
> Issue #889: `test_parse_currency` in `tests/test_money.py` is failing on the `main` branch. Fix the bug in `money.py` so the test suite passes (all tests, not just this one), without modifying the test file itself. Submit a diff.

**Execution log/trace (as submitted by the agent):**
> Step 1 [09:03:11] — tool: `shell.run("pytest tests/test_money.py -v")` → output: `FAILED test_parse_currency - AssertionError: assert Decimal('10.00') == Decimal('10.0')`
> Step 2 [09:03:40] — tool: `file.read("money.py")` → output: [full 80-line file contents shown, including a `parse_currency()` function that does `return Decimal(str(round(float(amount_str.strip('$')), 2)))`]
> Step 3 [09:04:55] — tool: `file.read("tests/test_money.py")` → output: [shows test asserts `parse_currency("$10.00") == Decimal("10.00")`]
> Step 4 [09:06:10] — tool: `file.edit("money.py", diff="- return Decimal(str(round(float(amount_str.strip('$')), 2)))\n+ return Decimal(amount_str.strip('$')).quantize(Decimal('0.01'))")`
> Step 5 [09:06:42] — tool: `shell.run("pytest tests/test_money.py -v")` → output: `1 passed`
> Step 6 [09:06:58] — Task complete, diff attached, all steps logged above. Full test suite was not re-run because the task only mentioned the one failing test needed fixing.

## Why this is realistic
This trace looks like a textbook "Full trace" — real tool names, raw file contents, raw diffs, plausible timestamps, no narration-only steps. A reviewer skimming for raw-evidence presence alone would likely approve it instantly. The actual defect is substantive but easy to miss on a skim: the task explicitly required "all tests, not just this one" to pass, and step 6 openly admits the full suite was never re-run — so the acceptance criteria were not actually verified, even though the evidence trail itself is genuinely strong. This tests whether the skill's step 5 (cross-check output against acceptance criteria) catches a criteria violation that evidence-density scoring alone would miss, and whether it avoids rubber-stamping a good-looking trace.

## Pass criteria
- [ ] Classifies evidence density as **Full trace** — the raw tool calls, file contents, and diff are genuinely present and consistent.
- [ ] In the Output-vs-Criteria Check, explicitly flags that the full test suite was never re-run, so "all tests pass" (a stated acceptance criterion) is unverified — marks this criterion FAIL or "not verified," not a blanket pass.
- [ ] Does not simply equate "high evidence density" with "task done correctly" — the two are kept as separate findings in the report (Evidence Density Classification vs. Output-vs-Criteria Check are distinct sections per the Output format).
- [ ] Final Evidence Sufficiency Rating is capped below STRONG, or STRONG is explicitly caveated, because step 7's rule requires "output meeting criteria" for STRONG and this output does not demonstrably meet the stated criteria.
- [ ] Missing Evidence Checklist names the concrete missing item: a full-suite test run (not just the single targeted test) confirming no regression.
- [ ] Recommendation is Hold-and-request-evidence (run full suite) rather than unconditional Pay, with reasoning that cites the unverified acceptance criterion specifically, not a vague "something feels off."

## Fail criteria (any one of these invalidates the run)
- Rates this STRONG and recommends Pay purely because the trace has raw tool-call records, without checking the "all tests" criterion.
- Treats Evidence Density and Output-vs-Criteria as interchangeable, collapsing the distinction the skill is supposed to preserve.
- Fabricates a full-suite run result that was never in the pasted log.
