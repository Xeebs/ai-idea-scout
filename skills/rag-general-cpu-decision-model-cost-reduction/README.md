# RAG Gating Model Fit Check

A self-contained prompt template for checking whether it's worth replacing a frontier-model gating decision in a RAG pipeline (should-retrieve / chunk-relevance / groundedness-check) with a small sub-1B CPU model — and, critically, for not trusting any single model's own benchmark numbers while doing it.

Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.), fill in your own numbers, and send it.

## When to use this

Use this when your RAG pipeline calls an LLM not to generate the final answer, but to make a cheap-feeling yes/no or classification decision on every query or chunk — "should I even retrieve for this query?", "is this chunk relevant?", or "is this answer grounded in what was retrieved?" — and you're spending real, measurable cost or latency on that gating call, and you're wondering whether a small local/CPU model could replace it.

Do not use this for picking your final answer-generation model, for general cloud-bill optimization unrelated to a gating decision, or for choosing an embedding/retrieval model.

## What you need to hand over

**Data source: Manual.** You paste your own numbers below — this is a conversational advisory check, not something that reads your billing dashboard or API logs automatically.

1. Which gating task you want to offload (should-retrieve, chunk-relevance, groundedness-check, or name your own).
2. Your current setup: which model handles this gate today, roughly how many gating calls you make per day or month, and roughly how many tokens (prompt + completion) each call uses.
3. The $/1M input and output token pricing for that current model.
4. Current latency for this gating step (p50/p95 if you have it), and any latency budget driving the question.
5. How much accuracy drop versus your current model's judgment you'd actually tolerate, if any.
6. Whether you have (or could quickly produce) a small sample of past gating decisions — even 50-100 — that you could check a candidate model against.

If you don't have exact numbers for 1-4, give your best estimate and say so; don't skip them, since the savings math depends entirely on them.

## The prompt

```
I run a RAG pipeline that uses an LLM to make a gating decision — not to
generate the final answer, but to decide [should-retrieve / chunk-relevance /
groundedness-check / other — name it].

Here's my current setup:
- Current model handling this gate: [model name]
- Gating calls per month: [number]
- Approx tokens per call (prompt + completion): [number]
- Pricing for that model: $[x]/1M input tokens, $[y]/1M output tokens
- Current latency for this gating step: [p50/p95 if known]
- Latency budget, if any: [number or "no hard budget"]
- Accuracy drop I'd tolerate vs. my current model's judgment: [e.g. "under 5%", "none", "not sure"]
- Can I produce a small sample of past gating decisions to test against? [yes/no, size]

Please run a RAG Gating Model Fit Check:

1. Compute my current baseline monthly gating cost from the numbers above, showing
   the formula so I can re-derive it myself.
2. Give me a savings range if I swapped to a small (sub-1B parameter) CPU model
   for this gate — but be explicit that this isn't free: it needs CPU hosting,
   and don't just quote 100% savings.
3. List today's known small gating-model candidates for this task — Arc-decide
   (~0.4B, should-retrieve/RAG-check), nano-jev (33.4M, latency-focused),
   pyrrho-v1/v2-nano-g1/g3 (INT8 ONNX, relevance/groundedness classification),
   and a fine-tuned Llama-3.2-1B relevance grader (arXiv 2506.14084) — and flag
   every single one of their numbers as self-reported by that project's own
   author, not independently verified by anyone else. If you know of other
   candidates, list them too, with the same unverified flag unless you have an
   independent source.
4. Do NOT tell me which one is "best" or "most accurate" — none of these numbers
   has been independently confirmed. Instead, give me a concrete validation plan:
   which one or two candidates are easiest for me to try given my setup, how to
   test them against my own sample of past decisions, and what agreement-rate
   threshold I should decide on *before* running the test (not after).
5. Flag the risk that a model validated on one slice of my traffic may not hold
   up on other domains if my queries vary a lot.
6. End with a clear recommendation: is this worth piloting at my volume, and if
   so, which candidate to test first and why (ease of integration — not claimed
   accuracy).

Structure your answer as: Baseline, Savings Potential, Candidate Shortlist
(table), Validation Plan, Recommendation, Risks.
```

## What you get back

A structured report with six sections:
- **Baseline** — your current monthly gating cost and latency, with the math shown.
- **Savings Potential** — a caveated range, not a clean "100% savings" promise.
- **Candidate Shortlist** — a table of today's small gating models, each tagged "self-reported, unverified" unless you've supplied independent evidence yourself.
- **Validation Plan** — concrete steps to test a candidate against your own sample before committing, with a go/no-go threshold you set in advance.
- **Recommendation** — whether this is worth piloting at your volume, and which candidate to try first based on ease of integration.
- **Risks** — generalization risk across traffic domains, plus a reminder that this space moves fast (five single-author releases appeared in one month as of late 2026) so check for newer entrants before committing engineering time.

## Guardrails this skill follows

- It will never tell you a specific small model is "the best" or "most accurate" as settled fact — every number in this space today is self-reported by a single author, and the whole point of this check is not to quietly trust that.
- It will never invent a benchmark, latency, or accuracy number that isn't either in its own candidate list above or something you supplied.
- It will never estimate savings from guessed volume or pricing — if you don't give real numbers, it should ask, not assume.
- It will never tell you to do a full production cutover — the only recommendation it makes is whether to run a validation pilot, and which candidate to try first.
- It has no live connection to your cost dashboard, API logs, or RAG pipeline — everything it works from is what you paste in.
