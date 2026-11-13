# Stack Math: Guardrail Compounding-Failure Calculator

Paste this whole prompt into any AI chat tool when you have a multi-layer guardrail pipeline (content filter → topic classifier → tool-call guard → output validator, or any similar stack) and want to know what it *actually* catches and blocks — not a rule-of-thumb guess.

## When to use this

Use it when you have two or more chained guardrail/safety checks in front of or around an LLM, each with its own measured accuracy from your own eval set or production logs, and you want the real end-to-end number before shipping or re-tuning the stack. It answers: "if I stack these specific layers at these specific measured accuracy rates, what hazardous traffic actually slips through, and how much benign traffic gets wrongly blocked?"

It does **not** model what happens if a detector service itself crashes, times out, or goes down — that's a separate operational-outage question, not an accuracy-compounding one. This tool only computes what measured *detection accuracy* compounds to across a pipeline.

## What to hand over

This only works with real numbers you already have — don't invent any to make the prompt "work." For each layer in your pipeline, in order, give:

1. **Name** of the layer (e.g. "content filter," "topic classifier," "tool-call guard," "output validator").
2. Either:
   - **True-positive rate (TPR)** — how often it correctly catches genuinely hazardous input, AND **false-positive rate (FPR)** — how often it wrongly flags benign input, OR
   - If that split isn't measured yet, a single blended **accuracy** number (the tool will still compute a simplified estimate, but will tell you it can't give you the full breakdown without the TPR/FPR split).
3. **Fail-open or fail-closed** — what the layer does if it can't render a decision at all (times out, crashes, abstains). This gets reported as a tail-risk note, not folded into the math.

Optionally, a **traffic mix**: the rough share of hazardous vs. benign requests you actually see (e.g. "10% adversarial, 90% benign"). Without this, you still get per-request rates, just not projected incident counts.

If you're missing the TPR/FPR split or the fail-open/closed policy for a layer, say so explicitly rather than guessing — a correct "unknown" is more useful than a confident-looking fabricated number here.

## What happens next

1. **Inventory** — every layer is listed with whatever numbers you gave, in your declared order, with any missing fail-open/closed policy flagged as unstated rather than assumed.
2. **Naive baseline** — the tool multiplies every layer's single accuracy number together (∏ accuracy). This reproduces the back-of-envelope rule of thumb you may have seen ("stack five guardrails at 90% each and you get ~59% system correctness"). This number is explicitly labeled as the naive guess, not the answer.
3. **Real compounded metrics** — for every layer where you gave a full TPR/FPR split:
   - **Missed-hazard rate** = the product of every layer's miss rate (1 − TPR). A hazardous item only escapes if *every* layer independently fails to catch it.
   - **False-block rate** = 1 minus the product of every layer's (1 − FPR). A benign item gets wrongly blocked if *any single* layer flags it.
   - The tool states plainly that this assumes each layer's errors are independent — if your layers share a model family or the same blind spot, your real missed-hazard rate will be worse than this ceiling.
4. **Traffic-mix projection** (if you gave one) — expected incident counts per 1,000 requests, split into missed-hazard incidents and false-block incidents.
5. **Sensitivity ranking** — the tool removes each layer one at a time (on paper) and reports how much the missed-hazard rate and false-block rate move, naming:
   - the **weakest-link catcher** (the layer the stack depends on most for actually catching hazards),
   - the **biggest false-block contributor** (the layer most responsible for wrongly blocking benign traffic),
   - any layer that's **flaggable as redundant** (removing it barely moves either number).
6. **Fail-open tail-risk note** — every fail-open layer gets an explicit callout: if its detector errors or times out, hazardous traffic passes through unflagged, and this risk is *not* included in the missed-hazard number above (that number is detection-accuracy only, not outage risk).
7. **Delta and caveats** — a plain-language sentence contrasting the naive guess against the real computed numbers (this is usually the most useful single line in the whole report), plus the independence-assumption caveat and a note that this is a planning estimate, not a safety certification.

## Output you'll get

A single structured report with these sections, in this order: Pipeline as understood (table) → Naive estimate → Computed metrics (missed-hazard rate, false-block rate, projected incidents if mix given) → Delta (naive vs. real, in one sentence) → Sensitivity ranking (weakest-link catcher, biggest false-block contributor, redundant layer if any) → Fail-open tail-risk notes → Caveats (independence assumption, any layer excluded for missing data, "planning estimate, not certification").

## Rules this follows

- It will never invent a per-layer accuracy, TPR, or FPR number you didn't provide. Missing data gets flagged and asked for, never guessed.
- It will never assume a fail-open or fail-closed policy for a layer you didn't specify — it reports that as unstated.
- It will never fold detector-outage/crash risk into the missed-hazard or false-block numbers — those are detection-accuracy metrics only; a separate question ("what happens when the detector itself breaks") needs a different kind of review.
- It will never present its output as a compliance sign-off or safety guarantee — it's a planning number built from your own self-reported measured rates, which carries whatever staleness or representativeness problems those numbers already have.
- It will always keep the independence-assumption caveat visible in the final report, not buried — correlated failures across layers make the real-world risk higher than the computed ceiling.
- If you give it fewer than two layers, it will tell you there's nothing to compound rather than forcing an answer.
