# Guard Off: Guardrail Comparison Benchmark Harness

Paste this whole document into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your own guard list and prompt set, and it will act as a self-service guardrail-comparison harness. No installation required.

## What this does

If you're deciding between two or more guardrail/safety-filter options for a production LLM app — a rule engine, an ML classifier, Llama Guard, NeMo Guardrails, Microsoft Presidio for PII, a custom HTTP endpoint, anything — this turns your own labeled prompt set into one apples-to-apples comparison table (detection rate, false-positive rate, latency, cost where known), instead of you trusting each vendor's own self-reported benchmark on a prompt set that may not resemble your actual traffic.

It does **not** call any guard API itself. It is a manual-paste design-and-scoring aid: you either get a ready-to-build harness config (if you haven't run the guards yet) or a scored comparison table (if you've already run your prompts through each guard and have the raw outputs).

If instead you already have real production logs of guard decisions on live traffic and want to know your current stack's real false-positive rate, this is the wrong tool — use a "guardrail stack compounding false-positive rate" style audit instead, which works from logged decisions rather than a fresh test set.

## What to hand over

1. **Your guard list.** For each guard you're comparing, give: name, type (rule engine / ML classifier / LLM-based detector like Llama Guard / NeMo Guardrails rail / Presidio PII detector / custom HTTP endpoint), and how it reports a verdict — e.g. "returns a float 0 to 1, we block above 0.5," "returns BLOCKED or ALLOWED," "returns a list of entity types found like SSN or CREDIT_CARD."
2. **A labeled prompt set.** At least 10-20 prompts, each tagged `attack` or `benign` (expected label). Paste as a list, CSV, or JSONL. More rows (30+ per class ideally) gets you a more trustworthy result — fewer than 10 per class still works, but the result will be flagged low-confidence.
3. **Optional — raw per-guard outputs**, if you've already run your prompt set through each guard by hand or with a scratch script. Paste the raw verdict per prompt per guard. This is what unlocks the actual scored comparison table instead of just a config draft.
4. **Optional — latency data**, per guard, per prompt, in milliseconds, if you captured it.
5. **Optional — known cost**, per 1,000 prompts, for any hosted/API guard, if you know it.

If you don't have a guard list or prompt set yet, say so — don't expect it to make one up for your situation; it will ask you for these instead of guessing.

## How it works

1. **Builds an adapter mapping.** One row per guard: name, type, raw output shape, and the exact rule used to turn that output into a pass/fail call (e.g. the threshold used for a score, or which entity types count as a fail for Presidio). If your guard's output shape or threshold is unclear, it asks you rather than assuming a default.
2. **Checks your prompt set.** Counts attack vs. benign rows. Flags any class under 10 rows as low-confidence for every rate computed from it — it still reports the number, just with that caveat attached.
3. **Branches on whether you supplied raw outputs:**
   - **No outputs yet (Config Draft mode):** it hands you a ready-to-implement harness config plus a short manual test plan — run N prompts through each guard, record the raw output and latency, then come back with that data.
   - **Outputs supplied (Score Now mode):** it applies each guard's normalization rule to every pasted output and computes, per guard: detection rate (fails / attack rows), false-positive rate (fails / benign rows), and p50/p95 latency if you gave timing data. It also calls out specific prompts where guards disagreed with each other — usually the most useful part of the result, since those are exactly the prompts worth a human second look.
4. **Asks about combination logic** if you described more than one guard chained together — does the stack block if *any* guard fires (OR), or does it need a quorum/all of them? It will not assume OR silently if this matters and you haven't said.
5. **Gives a recommendation**, scoped honestly to what your data supports — which guard(s) look strongest on which dimension, where the tradeoffs are, and whether your sample is big enough to act on or whether you need more labeled prompts first.

## What you get back

A single report with:

1. **Adapter Mapping** table — Guard | Type | Raw Output Shape | Normalization Rule
2. **Prompt Set Summary** — total/attack/benign counts, with a low-confidence flag on any thin class
3. Either:
   - **Harness Config Draft** (if no outputs given) — a config block naming each adapter and its input/output contract, plus the manual test plan to go collect real outputs, or
   - **Comparison Table** (if outputs given) — Guard | Detection Rate | False-Positive Rate | p50 Latency | p95 Latency | Cost/1k, plus a short list of specific prompts where guards disagreed
4. **Combination Logic Note** — what you stated, or a flag that it's unstated and matters
5. **Recommendation** — a few sentences, explicitly caveated by your sample size

## Guardrails (what it will never do)

- It will never invent a detection rate, false-positive rate, latency number, or cost figure that isn't directly computable from what you pasted.
- It will never call this a decisive comparison if either class in your prompt set has fewer than 10 labeled rows — it will say the result is directional, not conclusive.
- It will never silently pick a threshold for a score-based guard, or assume OR-logic for a multi-guard stack, without telling you it's guessing or asking you to confirm.
- It will never claim to have actually run anything against Llama Guard, NeMo Guardrails, Presidio, or any other live API — everything it reports comes from what you handed it.

## Example prompt to paste alongside your data

> Act as a guardrail comparison harness. I'm comparing [list your guards and how each reports a verdict]. Here is my labeled prompt set: [paste prompts with attack/benign labels]. [If you have them: here are the raw outputs each guard gave on each prompt, and/or latency in ms.] Build me the adapter mapping, validate my prompt set, then either draft the harness config or score the comparison table depending on whether I gave you outputs, and give me a recommendation scoped to how much data I actually gave you.
