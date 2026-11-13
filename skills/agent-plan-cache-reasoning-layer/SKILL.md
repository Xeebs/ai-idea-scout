---
name: agent-plan-cache-reasoning-layer
description: Audits a sample of agent execution traces to find which task types are structurally repetitive enough to benefit from a plan-caching layer (reuse a validated reasoning plan instead of re-reasoning every step), and estimates the token/cost savings and risk of introducing one. Use when a team is considering a caching/memoization layer for a high-volume agent loop and wants evidence before building or buying one.
---

# Plan Cache Audit

## When to use this

A team runs an LLM agent (support-ticket triage, invoice/data extraction, compliance classification, or any multi-step tool-calling loop) at volume — hundreds to thousands of runs a day — and someone has proposed adding a plan-caching layer (cache a validated reasoning plan the first time a task-type recurs, replay its structure and only re-reason the genuinely novel slots on repeats) to cut token spend and latency. Before anyone builds or buys that middleware, they need evidence: which task types actually repeat often enough and consistently enough to be worth caching, and which ones would be dangerous to cache because their step sequence varies too much run to run.

Use this skill when someone hands you a batch of agent execution traces and asks "is a plan cache worth it for us" or "which of our workflows should we cache first."

## Inputs

**Data source**: Manual — the user pastes or uploads a sample of agent execution trace logs (JSON, JSONL, or a pasted transcript) covering at least 20 runs, ideally spanning more than one task type. There is no mature, named connector for this today — trace formats differ by framework (LangGraph, LangChain, OpenAI Assistants threads, a custom harness's own log schema), so there is nothing standard to connect to; the user must export and paste/upload their own logs.

Each trace should include, per run, at minimum: an ordered list of steps (tool/function calls or reasoning stages), the input arguments or a shape description for each step, and ideally token counts (input/output) per step or per run. If token counts are missing, say so and estimate relative cost by step count instead of token volume.

## Procedure

1. **Parse** every trace into an ordered step sequence: `(step_type/tool_name, argument_shape, tokens_in, tokens_out)` per step. If a trace is malformed or missing required fields, skip it and note the count skipped — never guess at missing steps.
2. **Fingerprint** each run by its structural signature: the ordered sequence of step/tool types plus the *shape* of each step's arguments (keys and types, not literal values — e.g., `{category: enum, confidence: float}` not `{category: "billing", confidence: 0.91}`). Two runs with the same fingerprint are the same task-type candidate. For any argument that is a list/array, treat its approximate size band (e.g., 1-2, 3-10, 10+ items) as part of the shape, not a literal value to ignore — a step that processes 1 item versus 20 items does fundamentally different, differently-costly work even though both are nominally "an array," so a cluster spanning a wide size band is a variance signal, not a match.
3. **Cluster** runs by identical or near-identical fingerprint (allow minor tolerance: one optional step added/removed counts as the same cluster if it happens in <15% of that cluster's runs; otherwise split into two clusters).
4. **Score each cluster** on three axes:
   - **Frequency**: occurrence count and % of total runs sampled.
   - **Token weight**: total tokens consumed by the cluster, and average tokens/run within it.
   - **Structural variance**: how much step sequences and argument shapes vary within the cluster (low variance = stable; high variance = risky — this is a proxy for how often a cached plan would silently stop fitting, i.e., the "divergence" risk the underlying caching layer exists to prevent).
5. **Derive a cacheability verdict per cluster**: `GOOD CANDIDATE` (high frequency, low variance), `MARGINAL` (moderate on one axis), or `RISKY — DO NOT CACHE YET` (high variance regardless of frequency, or frequency too low to amortize caching overhead — fewer than 5 occurrences in the sample). If a cluster's overall step sequence is stable but one specific step inside it drives most of the variance and cost (e.g., an early step is always identical while a later step's work scales with a variable input size), call this out separately rather than giving the whole cluster one blended verdict — the stable earlier step(s) may still be a narrower, lower-risk caching candidate on their own even when the full run isn't.
6. **Estimate savings as a range, never a point figure**: for `GOOD CANDIDATE` clusters, estimate a conservative (30%) and optimistic (up to ~90%, citing published plan-caching benchmarks) token-reduction range on the slot-filling assumption — only the varying arguments get re-reasoned, the validated plan skeleton is replayed. State the assumption explicitly. Do not repeat unverified marketing figures (e.g., a vendor's self-reported "99%") as if they were measured.
7. **Flag the latency/cost caveat**: note explicitly that token reduction does not always translate to cost or latency reduction if the caching/fingerprinting logic itself adds overhead — this is a known open risk in published plan-caching research, not a settled fact.
8. **Write the report** in the Output format below.

## Output format

A single markdown report with these sections, in this order:

1. **Summary** — sample size (runs parsed, runs skipped and why), number of distinct task-type clusters found.
2. **Task-Type Clusters** — a table: `Cluster | Occurrences | % of runs | Total tokens | Avg tokens/run | Structural variance (low/med/high) | Verdict`.
3. **Top Candidates for Plan Caching** — the `GOOD CANDIDATE` clusters ranked by total token weight, each with the estimated savings range and the slot-filling assumption stated.
4. **Risky or Marginal Clusters** — the rest, with the specific reason each didn't qualify (low frequency / high variance / insufficient data).
5. **Caveats** — the token-vs-cost caveat (step 7) and a note that this is a one-shot analysis, not a deployed caching system; it tells you where to look, it does not build or run the cache itself.

## Guardrails

- Never fabricate trace data, token counts, or step sequences not present in what was handed over. If a trace is incomplete, skip it and say so in the Summary — do not interpolate.
- Never state a savings estimate as a single confident number; always a conservative/optimistic range with the assumption stated.
- Never recommend caching a cluster with high structural variance, regardless of how frequent it is — that is precisely the failure mode (stale plans producing silently wrong output) the underlying caching architecture is designed to avoid.
- Never claim this analysis builds, deploys, or operates a caching layer — it is strictly a pre-build feasibility audit.
- If fewer than 20 valid runs are provided, or no cluster has 5+ occurrences, say the sample is too small to recommend anything and stop — do not pad a thin sample into a confident verdict.
