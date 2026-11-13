# Scenario 1: Four-layer pipeline with a full TPR/FPR split

## Input (as the user would paste it)

> We're about to ship a 4-layer guardrail stack in front of our support-agent LLM, in this order:
>
> 1. **Content filter** — measured on our eval set: TPR 0.92, FPR 0.03. Fail-closed (blocks on timeout).
> 2. **Topic classifier** — TPR 0.88, FPR 0.05. Fail-closed.
> 3. **Tool-call guard** — TPR 0.95, FPR 0.02. Fail-closed.
> 4. **Output validator** — TPR 0.85, FPR 0.04. Fail-open (we didn't want it blocking replies if the validator service hiccups).
>
> Our traffic is roughly 10% adversarial / jailbreak-style requests and 90% ordinary benign support questions. We assumed that stacking 4 layers each around 85-95% accurate gives us a pretty safe system. Can you tell us what this actually catches and blocks, and whether we're over- or under-engineered anywhere?

## Expected behavior

The skill should:

1. List the 4 layers in order with their TPR/FPR/fail-policy as given, with no `POLICY UNSTATED` flags (all four layers' fail policy was given).
2. Compute a **naive baseline** using TPR values only: 0.92 × 0.88 × 0.95 × 0.85 ≈ **0.654 (65.4%)**, explicitly labeled as the naive/back-of-envelope number.
3. Compute the **missed-hazard rate** = product of FNRs (0.08 × 0.12 × 0.05 × 0.15) ≈ **0.000072 (0.0072%)** — i.e. extremely low.
4. Compute the **false-block rate** = 1 − product of (1−FPR) ≈ **0.133 (13.3%)** — i.e. a meaningfully high fraction of benign traffic gets wrongly blocked.
5. State the delta in plain language: the naive 65.4% estimate massively undersells how well the stack actually catches hazards (missed-hazard is near-zero), but says nothing at all about the much more serious 13.3% false-block risk on ordinary benign traffic — the real risk here is over-blocking legitimate users, not under-catching attackers.
6. Project incident counts per 1,000 requests using the 10%/90% mix: roughly 0.1 hazardous requests missed per 1,000 (10% of 1000 × 0.000072), and roughly 120 benign requests wrongly blocked per 1,000 (90% of 1000 × 0.133).
7. Sensitivity ranking: identify the **tool-call guard** (FPR 0.02, FNR 0.05 — the lowest FNR) as the layer the stack depends on most for catching hazards (removing it increases missed-hazard rate by roughly 20x, the largest jump of the four). Identify the **topic classifier** (FPR 0.05, the highest FPR) as the **biggest false-block contributor** (removing it drops the false-block rate the most, by roughly 4.5 percentage points).
8. Fail-open tail-risk note: flag the **output validator** explicitly — if its detector times out or errors, hazardous content in the final response passes through unflagged, and this is not captured in the 0.0072% missed-hazard number above.
9. Include the independence-assumption caveat and the "planning estimate, not a certification" caveat.

## Pass criteria

- [ ] Naive estimate computed and labeled as naive, landing near 65% (±3 points acceptable for rounding).
- [ ] Missed-hazard rate computed near 0.007%–0.01% (order of magnitude correct: well under 0.1%).
- [ ] False-block rate computed near 11%–15% (order of magnitude correct: double digits, clearly non-trivial).
- [ ] Output explicitly states the delta/contrast between naive estimate and the two real metrics, in plain language, not just raw numbers side by side.
- [ ] Tool-call guard (or equivalent lowest-FNR layer) correctly identified as most load-bearing for catching hazards.
- [ ] Topic classifier (or equivalent highest-FPR layer) correctly identified as the biggest false-block contributor.
- [ ] Output validator flagged by name as fail-open with an explicit statement that this risk is not included in the missed-hazard number.
- [ ] No fabricated numbers — every number used traces back to a value the user supplied or a value computed from it.
- [ ] Independence-assumption caveat present somewhere in the final output, not omitted.

## Fail conditions

- Treating the naive 65.4% figure as the final answer without computing the separate missed-hazard/false-block split.
- Missing or misidentifying which layer is the biggest false-block contributor.
- Failing to flag the output validator's fail-open policy as an unmodeled tail risk.
- Fabricating a traffic-mix number the user didn't give, or fabricating FPR/TPR values for a layer.
