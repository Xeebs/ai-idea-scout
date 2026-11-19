---
name: rag-general-cpu-decision-model-cost-reduction
description: Estimates savings and risk from swapping a RAG pipeline's frontier-model gating calls (should-retrieve, chunk-relevance, groundedness-check) for a small sub-1B CPU decision model, and produces a validation plan instead of trusting any single-author model's self-reported benchmark. Use when a user asks whether a small/local model can replace an LLM gating step in their RAG pipeline to cut cost or latency.
---

# RAG Gating Model Fit Check

## When to use this
A user is running a production RAG pipeline that calls a frontier model (GPT-4/4o-mini, Claude, Gemini, etc.) not to generate the final answer, but to make a cheap-feeling gating decision on every query or chunk: "should I retrieve for this query at all?", "is this chunk actually relevant?", or "is this answer grounded in the retrieved context?". They suspect a small model could handle this and want to know (a) whether the savings are worth the engineering effort, and (b) which of today's small sub-1B "decision model" releases (Arc-decide, nano-jev, pyrrho, a fine-tuned Llama-3.2-1B grader, or similar) is actually trustworthy enough to try — as opposed to just trusting that project's own README numbers.

Do not use this for: choosing a model for the final answer-generation step, general LLM cost optimization unrelated to a gating/routing decision, or picking a retrieval/embedding model.

## Inputs
**Data source**: Manual — the user pastes their own pipeline's numbers (gating task, current model, call volume, token sizes, pricing, latency budget) directly into the conversation; this skill does not read a live cost dashboard or API. This is distinct from the underlying project idea this skill is derived from, where the trained decision model itself would be Connected at runtime (same query+chunk inputs the pipeline already passes to its existing gating call, no new connector needed) — this skill only produces the advisory feasibility read, not that runtime integration.

Ask for, or extract from what's given:
1. **Gating task** — which decision is being offloaded: should-retrieve, chunk-relevance scoring, groundedness/hallucination check, or another named gate.
2. **Current setup** — which model handles this gate today, the average number of gating calls per day or month, and the approximate prompt+completion token count per call.
3. **Pricing** — $/1M input and output tokens for the current model (ask if not given; do not guess a number).
4. **Latency context** — current p50/p95 latency for this gating step, and what latency budget (if any) is driving the question.
5. **Risk tolerance** — how much accuracy drop versus the current frontier-model judge they'd actually accept, if any.
6. **Eval capacity** — whether they have, or can quickly produce, a small labeled or labelable sample of past gating decisions (even 50-100 examples) to validate a candidate against.

If 1-4 are missing, ask for them before producing output — do not estimate savings on invented volume or pricing numbers.

## Procedure
1. **Compute the baseline.** Using inputs 2-3: `monthly gating cost = calls/month * (input_tokens * $/1M_input + output_tokens * $/1M_output) / 1,000,000`. State this plainly as the number being targeted for reduction.
2. **State the savings ceiling, with caveats.** A sub-1B model run on CPU has near-zero per-call marginal API cost, but is not free — it requires provisioning CPU inference capacity (a server, a serverless CPU endpoint, or spare capacity on existing infrastructure) and ongoing ops. Present savings as "up to ~100% of the gating line item above, minus whatever that CPU hosting costs," not as a clean 100% win.
3. **List today's known candidates for the stated gating task**, each tagged with its actual provenance so the user never mistakes a self-report for an independent result:
   - **Arc-decide** (~0.4B, MIT license) — should-retrieve / RAG-check decisions; self-reported, single-author Show HN release (Oct 2026).
   - **nano-jev** (33.4M params, ~9-17ms/decision on 8-thread CPU) — self-reported latency only, single-author Hugging Face release.
   - **pyrrho-v1 / pyrrho-v2-nano-g1/g3** (INT8 ONNX) — ABSTAIN/DISPUTED/TRUSTWORTHY classification and evidence-sufficiency judging; self-reported, single-author.
   - **Fine-tuned Llama-3.2-1B relevance grader** (arXiv 2506.14084) — reports precision improving 0.13 to 0.78 on its own eval set; one paper, not independently re-run.
   If the user names a model not on this list, say plainly that it hasn't been checked and gets the same treatment as the rest: unverified until validated per step 4.
   **Never state or imply that any one of these is "the best" or "most accurate" option** — every number above is self-reported by that project, not independently confirmed. That lack of an independent benchmark is the exact gap this task exists to work around, not something to paper over.
4. **Build a validation plan, not a recommendation.** Because no independently-verified benchmark exists across these models today, the deliverable is a go/no-go test the user runs themselves:
   - Pull a stratified sample of 50-300 real past gating decisions (or synthesize them if truly none exist) that already have, or can get, a frontier-model judgment as ground truth.
   - Pick the one or two candidates from step 3 that are easiest to stand up given the user's task and stack (same task coverage, simplest runtime — e.g., ONNX/INT8 over a from-scratch fine-tune if they lack ML infra).
   - Run that candidate on the sample, compute agreement rate with the frontier-model ground truth, and compare against the risk tolerance from input 5.
   - Set a concrete go/no-go threshold before running the test (e.g., "go" if agreement ≥ 90% and no systematic false-negative pattern on the minority class), not after seeing the result.
5. **Flag the generalization risk.** Note explicitly that a model validated on one domain/corpus may not hold up on a different one without retraining — if the user's traffic spans multiple domains, say the validation sample should be stratified across them, not drawn from one slice.
6. **Produce the report** in the Output format below.

## Output format
A **Gating Model Fit Check** with these sections, in order:
1. **Baseline** — current monthly gating cost (with the formula and inputs used, so the user can re-derive it) and current latency.
2. **Savings Potential** — a range, explicitly caveated by CPU hosting cost and the "no independent benchmark yet" caveat; never a single clean number presented as fact.
3. **Candidate Shortlist** — a table: Model | Params | Task Coverage | Claimed Perf/Latency | Provenance Flag (always "self-reported, unverified" unless the user supplies independent evidence).
4. **Validation Plan** — the concrete steps from procedure step 4, with the user's own go/no-go threshold stated back to them.
5. **Recommendation** — "pilot-worthy" or "not yet" based on whether their volume/budget justifies even running the validation, plus which candidate to test first and why (ease of integration, not claimed accuracy).
6. **Risks** — generalization-across-domains risk, and a one-line reminder that this field had five single-author releases in one month, so check for newer entrants before committing engineering time.

## Guardrails
- Never present any candidate's self-reported number as independently verified fact — always carry the provenance flag through to the final output.
- Never fabricate a benchmark number, latency figure, or accuracy claim not present in this file's candidate list or supplied directly by the user.
- Never estimate savings from assumed call volume, token size, or pricing — ask for missing inputs rather than filling them in.
- Never recommend a full production cutover; the only recommendation this skill makes is whether to run the validation pilot, and which candidate to test first.
- Never treat this skill as connected to the user's live cost or observability dashboard — all numbers come from what the user pastes into the conversation.
