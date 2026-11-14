# Scenario 2 — Full raw tool-call trace on a code-fix bounty, with one dangling step

## Setup
A freelance-dev-agent platform operator hired an agent to fix a failing test suite in a small open-source repo for a $120 bounty: "Fix the 3 failing tests in `test_parser.py` on branch `fix/parser-bug`, without modifying the test files themselves, and show the full test run passing." The agent submitted a detailed execution trace. The operator wants a read before releasing the $120.

## Input to the skill

**Task description:**
"Fix the 3 failing tests in `test_parser.py` on branch `fix/parser-bug`, without modifying the test files themselves, and show the full test run passing."

**Execution log/trace:**
```
Job: fix-parser-tests-bounty-204
Started: 2026-11-12T14:02:11Z

Step 1 [14:02:11] tool=shell cmd="pytest test_parser.py -v"
  output: "3 failed, 9 passed. FAILED test_parse_nested_brackets, FAILED
  test_parse_empty_string, FAILED test_parse_unicode_escape"

Step 2 [14:02:40] tool=read_file path="parser.py"
  output: [full 140-line file contents shown, including the buggy
  `parse_nested()` function with an off-by-one in bracket depth tracking]

Step 3 [14:05:02] tool=edit_file path="parser.py"
  diff: "- depth = depth
  + depth = depth - 1 if char == ']' else depth + 1"
  (3-line diff shown against the exact function from step 2)

Step 4 [14:05:20] tool=shell cmd="pytest test_parser.py -v"
  output: "2 failed, 10 passed. FAILED test_parse_empty_string, FAILED
  test_parse_unicode_escape"

Step 5 [14:07:44] tool=read_file path="parser.py" (lines 80-110, the
  parse_empty and unicode_escape handling)
  output: [relevant 30-line excerpt shown]

Step 6 [14:09:58] tool=edit_file path="parser.py"
  diff: [two separate small diffs shown, one per bug, each referencing
  the exact lines from step 5's excerpt]

Step 7 [14:10:15] tool=shell cmd="pytest test_parser.py -v"
  output: "0 failed, 12 passed"

Finished: 2026-11-12T14:10:15Z
Final deliverable: git diff of parser.py attached (test_parser.py untouched,
confirmed via `git diff --stat` showing only parser.py changed)
```

## Expected output characteristics (pass/fail checklist)

- [ ] **Task Claim Summary** correctly states: fix 3 failing tests without touching test files, show passing run.
- [ ] **Acceptance Criteria** lists (stated): exactly 3 originally-failing tests now passing, `test_parser.py` unmodified, full test run shown green.
- [ ] **Evidence Walkthrough** walks all 7 steps, correctly noting each diff is traceable to the exact file contents read in the immediately preceding read_file step (no logical gaps).
- [ ] Timestamps are checked and found plausible (minutes between steps for reading, editing, and re-running a small test suite — no 0-second anomalies) — report should note this explicitly rather than skipping the check.
- [ ] **Evidence Density Classification** = **Full trace** (raw shell output and diffs at every step, not paraphrased).
- [ ] **Red Flags**: should still flag one legitimate thing — the `git diff --stat` confirming `test_parser.py` untouched is referenced only in the final summary line, not shown as its own raw step output earlier in the trace (minor but real gap: the "test files untouched" claim has weaker direct evidence than the bug-fix steps themselves). A good run of the skill catches this; it should not report "no red flags" outright.
- [ ] **Output-vs-Criteria Check**: all 3 originally-named failing tests (`test_parse_nested_brackets`, `test_parse_empty_string`, `test_parse_unicode_escape`) are confirmed passing by the final 0-failed run — pass.
- [ ] **Evidence Sufficiency Rating = STRONG or MODERATE** (strong raw step-by-step trace with one minor, named gap around the untouched-test-files claim; STRONG is acceptable only if the report explicitly weighs that gap as minor — MODERATE is also an acceptable, defensible call given the one flagged gap. INSUFFICIENT or WEAK would be a fail here — the trace is clearly substantially stronger than scenario 1's).
- [ ] **Missing Evidence Checklist** names the specific gap (a raw `git diff --stat` output step, not just the summary line asserting it) rather than restating generic concerns.
- [ ] **Recommendation = Pay**, optionally noting the minor gap as a note-for-next-time rather than a blocker.

**Fails this scenario if:** the skill rates this the same as scenario 1 (no differentiation by evidence density), misses that diffs trace correctly to prior read_file outputs, or treats the single minor gap as grounds for a Hold/Reject recommendation given how strong the rest of the trace is.
