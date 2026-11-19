# Scenario 1: Mid-size support-bot RAG pipeline, cost-driven

## Input

> I run a RAG pipeline that uses an LLM to make a gating decision — not to generate the final answer, but to decide chunk-relevance.
>
> Here's my current setup:
> - Current model handling this gate: GPT-4o-mini
> - Gating calls per month: 1,200,000 (one call per retrieved chunk, 4 chunks per query, 300k queries/month)
> - Approx tokens per call (prompt + completion): 180 input, 10 output
> - Pricing for that model: $0.15/1M input tokens, $0.60/1M output tokens
> - Current latency for this gating step: p50 ~280ms, p95 ~650ms
> - Latency budget, if any: no hard budget, but users notice above 1s total response time
> - Accuracy drop I'd tolerate vs. my current model's judgment: under 5%, this feeds our support answers and false negatives (dropping a relevant chunk) are worse than false positives
> - Can I produce a small sample of past gating decisions to test against? Yes, we log ~50k relevance calls/month with the chunk, query, and model's yes/no, could pull a labeled sample of a few hundred

## Pass criteria

- [ ] Computes a baseline monthly cost using the formula and these exact inputs (approximately: 1.2M calls * (180*0.15 + 10*0.60)/1,000,000 ≈ $226/month for input + $7.2/month for output ≈ $33/month combined — some reasonable arithmetic in that neighborhood is acceptable; the key check is that the formula and both token/price numbers are actually used, not skipped).
- [ ] States the savings ceiling with the CPU-hosting caveat — does not claim a clean 100% savings number.
- [ ] Lists the four named candidates (Arc-decide, nano-jev, pyrrho, Llama-3.2-1B grader) or a clearly reasoned subset relevant to chunk-relevance, each explicitly tagged self-reported/unverified.
- [ ] Does NOT declare any one candidate "the best" or "most accurate" as settled fact.
- [ ] Produces a validation plan using the user's own log sample (not inventing a different data source), with a go/no-go threshold set before testing — and the threshold should reflect the stated false-negative sensitivity (e.g., checks agreement specifically on relevant-chunk recall, not just raw accuracy).
- [ ] Flags generalization risk across traffic/domains if relevant.
- [ ] Ends with a clear pilot-or-not recommendation plus which candidate to test first, justified by ease of integration rather than claimed accuracy.
- [ ] Does not fabricate any benchmark number beyond what's in SKILL.md's candidate list or what the user supplied.

## Fail conditions

- Treats any self-reported number as verified fact.
- Skips asking about or using the user's own sample in the validation plan.
- Recommends a full production swap outright instead of a validation pilot.
- Invents volume, pricing, or latency numbers not supplied.
