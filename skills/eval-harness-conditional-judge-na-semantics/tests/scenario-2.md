# Scenario 2 — Fail-open conflation: condition-evaluation error silently treated as a normal skip (programmatic TS harness)

Tests the second, opposite failure mode named in the idea (a fail-closed convention's inverse): a broken condition hidden behind what looks like a clean run.

## Input the user pastes

**Judge-condition config (`judges.ts`, excerpt):**
```typescript
export const judges: JudgeConfig[] = [
  {
    name: "toxicity-check-non-english",
    condition: (c: Case) => c.locale.toLowerCase() !== "en",
    check: async (c: Case) => runToxicityModel(c.response),
    aggregation: { metric: "min_pass_rate", threshold: 0.90 },
  },
  {
    name: "length-budget",
    condition: () => true,
    check: async (c: Case) => c.response.length <= c.maxLength,
    aggregation: { metric: "min_pass_rate", threshold: 1.0 },
  },
];

async function runJudge(judge: JudgeConfig, cases: Case[]) {
  const results = [];
  for (const c of cases) {
    try {
      if (!judge.condition(c)) continue; // skip
      results.push(await judge.check(c));
    } catch (e) {
      continue; // treat any error (condition or check) as skip
    }
  }
  return aggregate(results, judge.aggregation);
}
```

**Sample eval run raw output (console/log excerpt, `run-2026-11-17.log`):**
```
[run-2026-11-17] cases_selected=25
[toxicity-check-non-english] case c3: locale=undefined -> condition() threw TypeError: Cannot read properties of undefined (reading 'toLowerCase') -> caught, skipped
[toxicity-check-non-english] case c7: locale="es" -> condition true -> check passed
[toxicity-check-non-english] case c12: locale=undefined -> condition() threw TypeError -> caught, skipped
[toxicity-check-non-english] case c19: locale="fr" -> condition true -> check passed
[toxicity-check-non-english] result: 2/2 passed, pass_rate=1.0, status=PASSED
[length-budget] result: 25/25 passed, status=PASSED
[run-2026-11-17] overall_status=PASSED
```

**User's message**: "We're migrating case data and some records are missing `locale` for now. I noticed `toxicity-check-non-english` still shows PASSED at 100%. Just want a gut check before I ignore this — anything to worry about here?"

## Pass criteria

- [ ] Correctly identifies `toxicity-check-non-english` as in-scope (has a `condition` gate) and `length-budget` (unconditional `() => true`) as out of scope.
- [ ] Classification table lists c3 and c12 separately from c7/c19: for c3/c12, harness's actual reported outcome is "skipped" (silently, via the catch-all `catch (e) { continue }`), correct taxonomy outcome is `ERRORED` (the condition function itself threw, not "condition evaluated false"), Match = No. For c7/c19, harness outcome `APPLICABLE_PASS`, taxonomy outcome `APPLICABLE_PASS`, Match = Yes.
- [ ] Diagnosis explicitly names the fail-open/conflation bug: quotes the `catch (e) { continue }` block in `runJudge`, explaining it catches both a genuine condition-false case and a condition-*evaluation error* identically, so the 100% pass rate is computed only over the 2 cases that happened not to error — the user's "PASSED at 100%" is misleading because it silently excludes the 2 broken-locale cases rather than flagging them.
- [ ] Explicitly warns this is the inverse failure mode from a simple false-fail: here the run looks clean, but a real bug (missing `locale` field during the data migration) is being hidden, not surfaced — directly answers the user's "anything to worry about" with yes, and says why.
- [ ] Does NOT recommend simply changing the catch block to treat errors as a pass or as a plain skip merged with condition-false cases — must keep `ERRORED` distinct from `NOT_APPLICABLE`/skip, per the guardrail against re-conflating them.
- [ ] Suggested patch distinguishes condition-evaluation errors from check-evaluation errors (e.g., wrap `judge.condition(c)` in its own try/catch that reports `ERRORED` with the case ID and error message, separate from the `continue`-on-false-condition path and separate from errors thrown by `judge.check`), and adds an alert/log line for `ERRORED` outcomes distinct from the `NOT_APPLICABLE`/skip case.
- [ ] Given the toxicity/safety nature of this judge, raises (or at minimum considers and states a reasoned "yes/no") the fail-closed override question — reasonable to flag given it's explicitly a content-safety judge currently being silently starved of applicable cases due to a data bug.
- [ ] Report follows the five-section output format.

## Self-check notes
Walking the procedure: step 1 scope check passes. Steps 2-3 inventory + cross-reference are directly readable from the log lines, which explicitly show the TypeError text for c3/c12 versus the normal pass path for c7/c19 — no guessing required. Step 4 classification correctly separates `ERRORED` (condition threw) from what the code currently calls "skipped." Step 5 diagnosis matches the exact bug shape described in the idea's Tangible Impact section ("the opposite failure a fail-closed convention can introduce — silently passes a run that should have been flagged"). Step 6 patch is expressible as a small addition to the existing `runJudge` function in the same TypeScript idiom, not a rewrite. Step 7's override question is answerable from the given content ("toxicity" + "safety" framing) even without additional user input. All five output sections are producible from the given input alone — scenario passes.
