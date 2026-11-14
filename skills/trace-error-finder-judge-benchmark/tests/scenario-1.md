# Scenario 1 — Warehouse reconciliation agent, two entrants, sufficient sample

## Setup

A mid-size 3PL ("Fenwick Logistics") runs an internal agent that reconciles warehouse inventory counts against their WMS after each nightly cycle count — it reads a count-discrepancy report, queries the WMS API for expected quantities, and either auto-adjusts small variances or opens a ticket for a human to review. The ops team has been using a prompted GPT-4-class judge to flag which reconciliation traces the agent botched, and is now piloting a specialist trace-error-finder product ("ClearSignal") that claims much lower cost per trace. They want a quick read on whether ClearSignal is actually catching what their prompted judge catches before paying for a wider rollout.

## Input handed to the skill

**10 traces**, each as a short tool-call log, with a human ground-truth note. Example of 3 of the 10 (the full set given to the AI has all 10):

- **Trace 3**: Agent reads discrepancy report (SKU-4471, expected 212, counted 198), queries WMS, WMS returns 212, agent auto-adjusts to 198 and closes without flagging that a 14-unit variance exceeds the 10-unit auto-adjust threshold. **Ground truth: FAIL — category: threshold-rule violation (auto-adjusted above the 10-unit cap instead of escalating).**
- **Trace 7**: Agent reads discrepancy report (SKU-1180, expected 40, counted 40), queries WMS, confirms match, logs "no action needed," closes. **Ground truth: PASS — clean trace.**
- **Trace 9**: Agent reads discrepancy report (SKU-9902, expected 75, counted 0), queries WMS twice (first call times out, agent retries), WMS returns 75, agent interprets the retry's late response as a *second* discrepancy and opens two duplicate tickets for the same SKU. **Ground truth: FAIL — category: duplicate-ticket-on-retry.**

(Remaining 7 traces follow the same format: a mix of 4 more FAIL traces across categories like "wrong-SKU-queried" and "ignored WMS error response" and 3 more PASS/clean traces — total ground truth across the 10: 6 FAIL, 4 PASS.)

**Entrants requested:**
1. "This chat" — act as a GPT-4-class-style prompted judge directly on the 10 traces.
2. "ClearSignal" (specialist model) — team already ran it and supplies its 10 verdicts, e.g.: Trace 3: FAIL/threshold-rule violation; Trace 7: PASS; Trace 9: PASS (ClearSignal missed the duplicate-ticket issue); ... (full 10 supplied), with cost/latency: "$0.03/trace, 1.4s avg" for ClearSignal, and the team separately notes their existing prompted-judge pipeline runs at "$0.60/trace, 5.8s avg" (to be attributed to "this chat" entrant as its real-world cost context, even though the chat session itself can't be billed the same way — supplied for the table).

## Pass criteria

- [ ] The AI restates the sample (10 traces, 6 FAIL / 4 PASS ground truth) and the two entrants before scoring anything.
- [ ] It generates its own PASS/FAIL + category + evidence quote for all 10 traces as the "this chat" entrant, using one fixed rubric.
- [ ] It takes the ClearSignal verdicts exactly as supplied (e.g., does not "fix" ClearSignal's missed Trace 9 call) and scores them against ground truth as-is.
- [ ] Output includes a Scoring Table with TP/FP/FN/TN, Precision, Recall, F1 for both entrants, and the supplied cost/latency figures (not invented ones) in the same table.
- [ ] Trace 9 (where ClearSignal missed a real FAIL) appears in or is eligible for the Disagreement Spotlight.
- [ ] The Recommendation is explicitly hedged (e.g., "on this 10-trace sample," "directional, not conclusive") and names which entrant looks stronger along with the biggest reason the result could flip at scale.
- [ ] Caveats section states the sample-size limitation (10 traces, only 6 FAIL examples) and suggests roughly how many more labeled traces would be needed for confidence.
- [ ] Nothing is invented: no cost/latency number appears for an entrant beyond what was supplied, and no claim about why ClearSignal missed Trace 9 beyond what's inferable from the supplied verdict and trace content.

## Self-check notes

Walking through the procedure: 10 traces with ground-truth notes and two entrants (one live-gradable, one pre-supplied) satisfies the minimum-5-traces and ground-truth-required guardrails, so the skill proceeds. The fixed rubric (PASS/FAIL + category + evidence quote) applies cleanly to the "this chat" entrant since the trace descriptions given above are detailed enough to reason about threshold rules, retries, and WMS round-trips. ClearSignal's supplied verdicts are treated as given, producing a real scoring discrepancy on Trace 9 that becomes genuine Disagreement Spotlight material. Cost/latency figures were explicitly supplied for both entrants, so the table has real numbers rather than "not provided" placeholders. This scenario exercises the full happy path. **Pass.**
