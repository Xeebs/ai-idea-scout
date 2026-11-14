---
name: guardrail-comparison-benchmark-harness
description: Normalizes a team's own labeled adversarial/benign prompt set and guard stack description into a side-by-side detection-rate/false-positive-rate/latency comparison table (or a ready-to-build harness config if no outputs exist yet). Use when someone is deciding between guardrail options (Llama Guard, NeMo Guardrails, a custom classifier, a rule engine, Presidio, etc.) and wants an apples-to-apples read instead of trusting each vendor's own self-reported numbers.
---

# Guard Off: Guardrail Comparison Benchmark Harness (Design & Scoring Aid)

## When to use this
Trigger this when someone is choosing between two or more guardrail/safety-filter options for a production LLM app and says something like "which guard should we actually use," "I ran our prompts through Llama Guard and our custom classifier but the outputs look nothing alike," or "has anyone built a way to compare these guards on our own data instead of trusting each one's own benchmark." The tell is always a *comparison* need across heterogeneous guard output shapes (a score vs. a block/pass decision vs. a list of flagged entities) on the team's *own* prompts — not a request to tune a single guard's threshold, and not a request to audit production logs after the fact (that's a different, already-built skill: `guardrail-stack-compounding-fpr-harness`, which works from real logged decisions rather than a fresh labeled test set).

This skill does not call any guard API itself. It is a one-shot design-and-scoring aid: it drafts the adapter/config a team would need to build the real automated harness, and — if the team has already run their prompts through each guard by hand and pastes the raw outputs — scores those outputs into one comparison table.

## Inputs
**Data source**: Manual + Connected (hybrid, per the parent idea `guardrail-comparison-benchmark-harness.md`) — this skill itself only exercises the Manual half. The team pastes/uploads everything; it never calls Llama Guard, NeMo Guardrails, Presidio, or any custom endpoint directly. The Connected half — a real orchestration layer that calls those already-mature APIs live and re-runs on demand — is the companion CI-mode project this skill's output is meant to justify building, not something a chat session can execute.

What to hand over:
1. **The guard list** — for each guard under consideration: its name, its type (rule engine, ML classifier, LLM-based detector like Llama Guard, NeMo Guardrails rail, Presidio PII detector, or custom HTTP endpoint), and how it reports a verdict (e.g. "returns a float 0-1, we block above 0.5," "returns BLOCKED/ALLOWED," "returns a list of entity types found").
2. **A labeled prompt set** — at minimum 10-20 rows, each a prompt plus an expected label of `attack` or `benign`. Pasted inline, as a CSV, or as JSONL. More rows (ideally 30+ per class) materially raises confidence in the resulting rates — say so if the set is thin.
3. **Optional: raw per-guard outputs already collected** — if the team has already run the prompt set through each guard by hand (or via their own scratch script) and has the raw verdict per prompt per guard, paste those too. This unlocks scoring mode instead of config-draft-only mode.
4. **Optional: timing data** — per-guard, per-prompt latency in ms, if captured, to compute p50/p95.
5. **Optional: known per-1k-prompt cost** for any hosted/API guard, if the team knows it.

If the guard list or prompt set is missing entirely, ask for it — do not fabricate a stand-in guard stack or prompt set.

## Procedure
1. **Build the adapter mapping.** For each guard in the list, write one row: guard name, type, raw output shape as described, and the normalization rule that converts that raw shape into a single `pass` / `fail` call (for a score+threshold guard, state the threshold used; for an entity-list guard like Presidio, state the rule — e.g. "fail if any entity type in {SSN, CREDIT_CARD} is found"). If a guard's output shape or threshold is ambiguous or unstated, ask the user to clarify rather than assuming a default threshold or combination rule.
2. **Validate the prompt set.** Count rows per label. If either class has fewer than 10 labeled rows, proceed but flag every downstream rate for that class as low-confidence — never suppress a number for being thin, but never present a thin-sample rate with the same confidence as a well-sampled one.
3. **Branch on whether raw per-guard outputs were supplied:**
   - **Mode A — Config Draft** (no outputs yet): produce a ready-to-implement harness config (see Output format) the team can hand to an engineer to wire up the real adapters, plus a short manual test plan: run N prompts through each guard, record raw output + latency, come back with that data for Mode B.
   - **Mode B — Score Now** (outputs supplied): apply each guard's normalization rule from Step 1 to every pasted output, then compute per guard: detection rate = fails / attack rows, false-positive rate = fails / benign rows, and p50/p95 latency if timing was given. Show per-prompt disagreements (prompts where guards split on the verdict) as a short highlight list — this is usually the most actionable part of the output, since it points at exactly which prompts to manually inspect.
4. **State the combination logic explicitly if the team described a multi-guard stack** (OR = block if any guard fires, vs. AND/quorum). Never assume OR silently — ask if it wasn't stated and it matters to the comparison being drawn.
5. **Close with a recommendation**, scoped to what the data actually supports: which guard(s) look strongest on detection vs. false-positive rate vs. latency/cost, where the tradeoffs are, and — explicitly — whether the sample size is large enough to act on this or whether more labeled prompts are needed first.

## Output format
A single markdown report with these sections, in order:
1. **Adapter Mapping** — table: Guard | Type | Raw Output Shape | Normalization Rule
2. **Prompt Set Summary** — total rows, attack count, benign count, and a low-confidence flag on any class under 10 rows
3. **Mode A: Harness Config Draft** (only if no outputs were supplied) — a YAML-shaped config block naming each adapter, its input/output contract, and the manual test plan to collect real outputs
   OR
   **Mode B: Comparison Table** (only if outputs were supplied) — table: Guard | Detection Rate | False-Positive Rate | p50 Latency | p95 Latency | Cost/1k (if known), plus a "Disagreements" list of specific prompts where guards split
4. **Combination Logic Note** — stated or flagged-as-unstated
5. **Recommendation** — 2-4 sentences, explicitly caveated by sample size

## Guardrails
- Never invent a detection rate, false-positive rate, latency figure, or cost number that isn't directly derivable from what the user pasted. If a figure can't be computed from the given data, say so instead of estimating silently.
- Never declare a decisive winner when either class (attack or benign) has fewer than 10 labeled rows — say the result is directional/inconclusive instead.
- Never silently assume a block/pass threshold for a score-based guard, or an OR-combination rule for a multi-guard stack — ask when either is unstated and affects the comparison.
- Never claim this skill ran anything live against Llama Guard, NeMo Guardrails, Presidio, or any other API — it only ever processes what the user pasted.
- Never treat this as a substitute for the production-log audit skill (`guardrail-stack-compounding-fpr-harness`) — that one measures real traffic after deployment; this one benchmarks guard options against a test set before adoption. Point the user to the right one if they describe the other situation.
