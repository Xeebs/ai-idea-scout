# Plan Cache Audit

A self-contained prompt template for auditing a sample of AI agent execution traces to find out which task types are repetitive enough to benefit from a "plan-caching" layer — one that caches a validated reasoning plan the first time a task-type recurs, then replays that plan's structure instead of re-reasoning every step from scratch on later repeats, only re-invoking the model for the parts that genuinely vary. This README is paste-ready for any AI chat tool — it does not assume you have any other files or context.

## When to use this

You run (or are evaluating) an LLM agent that does the same *kind* of multi-step task over and over at volume — support-ticket triage, invoice or document extraction, compliance classification, anything with hundreds to thousands of runs a day — and someone has proposed adding a plan-caching layer to cut token spend and latency. Before building or buying that middleware, you want evidence: which of your task types actually repeat often enough and consistently enough to be worth caching, and which ones would be dangerous to cache because their steps vary too much run to run. This prompt turns a batch of your own execution logs into that evidence.

## What you need to provide

This only works on data you supply directly — there is no automatic connection to your agent's logs. Export and paste or upload a sample of execution traces: at least 20 runs, ideally more, and ideally covering more than one kind of task. Trace formats vary by framework (LangGraph, LangChain, OpenAI Assistants threads, a homegrown harness), so just use whatever log format you already have, as long as each run shows, at minimum:

- the ordered list of steps/tool calls the agent made
- the arguments or input shape for each step
- ideally, token counts (input/output) per step or per run — if you don't have these, say so and the analysis will fall back to step-count as a rough proxy for cost

## How to run it

Paste this entire prompt into your AI chat tool, followed by your trace data:

---

**Prompt:**

"You are auditing a batch of AI agent execution traces to determine which task types are repetitive enough to benefit from a plan-caching layer (caching a validated reasoning plan on first occurrence of a task type, replaying it on repeats, only re-reasoning the parts that genuinely vary). Follow this procedure exactly:

1. Parse every trace into an ordered step sequence: for each step, note the tool/function name, the shape of its arguments (keys and types, not literal values), and token counts if present. Skip and count any trace that's too malformed to parse — don't guess at missing steps.
2. Fingerprint each run by its structural signature: the ordered sequence of step/tool types plus each step's argument shape. Two runs with the same fingerprint are candidates for the same task-type cluster. For any argument that is a list/array, treat its approximate size band (1-2, 3-10, 10+ items) as part of the shape, not something to ignore — a step processing 1 item versus 20 is doing fundamentally different, differently-costly work, so a wide size band inside one cluster is a variance signal, not a match. Allow a small tolerance otherwise — one optional step appearing in under 15% of a cluster's runs doesn't force a split; more than that, split it into a separate cluster.
3. Cluster all runs by fingerprint.
4. For each cluster, compute: occurrence count, % of the total sample, total tokens consumed, average tokens per run, and a qualitative structural variance rating (low/medium/high) based on how much step sequences and argument shapes vary within the cluster.
5. Assign each cluster a verdict: GOOD CANDIDATE (frequent, low variance), MARGINAL (moderate on one axis), or RISKY — DO NOT CACHE YET (high variance regardless of frequency, or fewer than 5 occurrences in the sample). If a cluster's sequence is stable overall but one specific step drives most of the cost and variance (e.g., an early step is always identical while a later step's work scales with a variable input size), call that out separately instead of giving the whole cluster one blended verdict — the stable step(s) may still be a narrower, lower-risk caching candidate even when the full run isn't.
6. For every GOOD CANDIDATE cluster, estimate a token-reduction range — conservative 30%, optimistic up to ~90% — on the explicit assumption that caching replays the plan skeleton and only re-reasons the varying slot values. State that assumption plainly. Never state a single confident savings number, and never repeat an unverified vendor marketing figure (like a self-reported '99% reduction') as if it were measured.
7. Add an explicit caveat: token reduction does not always translate into cost or latency reduction, because the caching/fingerprinting logic itself can add overhead — this is a known open question in published plan-caching research, not a settled fact.
8. If fewer than 20 valid runs parse, or no cluster reaches 5+ occurrences, say the sample is too small to recommend anything and stop there — do not force a confident verdict out of a thin sample.

Produce your findings as a report with these sections, in this order:
- **Summary**: how many runs were parsed, how many skipped and why, how many clusters found.
- **Task-Type Clusters**: a table with columns Cluster | Occurrences | % of runs | Total tokens | Avg tokens/run | Structural variance | Verdict.
- **Top Candidates for Plan Caching**: the GOOD CANDIDATE clusters ranked by total token weight, each with its estimated savings range and the slot-filling assumption stated.
- **Risky or Marginal Clusters**: the rest, each with the specific reason it didn't qualify.
- **Caveats**: the token-vs-cost caveat, plus a note that this is a one-shot feasibility audit — it identifies where a plan cache would help, it does not build, deploy, or operate one.

Here is my trace data: [PASTE YOUR EXECUTION TRACES HERE]"

---

## What you get back

A ranked, evidence-based report telling you exactly which of your recurring task types are good candidates for a plan-caching layer, which are too inconsistent to cache safely, and an honest (never inflated) estimate of the token savings you could expect if you built or adopted one — so you spend engineering effort on caching only where the data says it will actually pay off, and you know in advance which workflows would be dangerous to cache because they vary too much to trust a replayed plan.

## What this does not do

This is a pre-build feasibility audit, not the caching layer itself. It does not fingerprint tasks, cache plans, or detect divergence at runtime in your production agent — it tells you, from a sample of past runs, where that kind of system would be worth building. If you want the always-on caching middleware, that is a separate engineering project (fingerprinter + plan store + replay executor + divergence detector sitting in your agent loop), not something a one-shot chat prompt can run for you.
