---
name: rag-sla-aware-query-planner
description: Audits a production RAG (retrieval-augmented generation) pipeline's cost structure against a sample of real query logs and drafts a difficulty-tiered routing plan — cheap retrieval+model for easy queries, expensive retrieval+model for hard ones — with an estimated savings range and a validation plan. Use when a team wants to know whether tiered routing is worth building before committing engineering time to a runtime planner, not a calibrated production classifier.
---

# RAG SLA-Aware Query Planner (Cost/Quality Tradeoff Audit)

## When to use this

Reach for this skill when someone operates a RAG pipeline in production — or is about to — and suspects they're running every query through the same expensive retrieval-and-model configuration regardless of how hard the query actually is. The trigger moment is specifically *before* they build a runtime query-difficulty classifier or router: they have (or can quickly pull) a sample of real query logs and a description of their current pipeline's cost, and they want a reasoned estimate of whether tiering by difficulty would meaningfully cut cost at their stated quality bar — a go/no-go on the idea, not the idea already built.

Do not use this for: implementing the actual routing logic or a production classifier (this skill produces a design/estimate document, not code); auditing whether a single already-generated answer is correct or faithful to its sources (that is answer-quality verification on one transcript, a different task); or general RAG performance tuning unrelated to cost (e.g., latency optimization with no cost angle, chunking strategy, embedding model choice) — those aren't what this skill was built to assess.

## Inputs

Required:
1. **Pipeline description** — the retrieval method(s) in use (keyword/BM25, dense/vector, hybrid, with/without reranking), typical retrieval depth (top-k), the generation model(s) and their tier (e.g., "GPT-4-class," "a 7B open model"), approximate daily/monthly query volume, and the current observed cost per query (or enough to derive it: $/1K tokens for each model plus typical token counts). If an explicit quality target exists (an accuracy threshold, an SLA, "must match human-eval baseline within 5%"), state it; if not, say so.
2. **A sample of real query logs** — at least 15, ideally 30-100 representative queries actually sent to the pipeline. For each, provide the query text and, if available, any of: the pipeline's current answer, a correctness/quality label, latency, or per-query cost. Logs without labels are usable — this skill classifies difficulty from the query text itself — but say plainly when no ground-truth quality signal exists so the savings estimate can be flagged as unvalidated.

Optional:
- Any routing heuristic already tried or considered (e.g., "we thought about routing by query length").
- A target cost-reduction goal, if the team has one in mind.

If fewer than 15 queries are provided, proceed but label the bucket percentages as a low-confidence draft and say explicitly that a larger, more representative sample is needed before the estimated savings range should be trusted. Never invent queries, costs, or quality labels that weren't provided.

## Procedure

1. **Summarize the current pipeline's flat cost.** State the single cost-per-query figure (or computed estimate) the pipeline incurs today for every query, and the stated or inferred quality bar it's trying to hit. If no quality bar was stated, say so and proceed using "matches current pipeline's own output" as the only available quality reference — flag this as a real limitation, since without an independent correctness signal the audit can only measure *consistency* with today's answers, not whether today's answers are actually correct.

2. **Classify every provided query into a difficulty bucket** using observable proxies from the query text alone (never fabricated metadata): **Lookup** (single-fact, named-entity, definitional — answerable from one passage, e.g., "what is our refund window"), **Moderate** (requires combining 2-3 facts or light reasoning, e.g., comparisons, "how does X differ from Y"), **Complex/multi-hop** (requires synthesizing across multiple documents, multi-step reasoning, open-ended or ambiguous phrasing, e.g., "why did this customer's renewal fail and what should we do"). Give each query a one-line rationale for its bucket. Flag any query that's genuinely ambiguous to bucket rather than forcing it — an honest "unclear" count is more useful than a falsely clean split.

3. **Build the bucket distribution table** — count and percentage of the sample in each bucket. State plainly that this distribution is a property of *this sample*, not a guaranteed property of full traffic, especially when the sample is under ~50 queries or wasn't drawn randomly.

4. **Recommend a tier-to-bucket mapping** based on known cost/quality tradeoff patterns: Lookup → shallow retrieval (low top-k, no reranking) + cheapest viable model tier; Moderate → mid-depth retrieval, optionally reranked, + a mid-tier model; Complex/multi-hop → full current pipeline (deep retrieval, reranking, largest model) unchanged. Never recommend downgrading the Complex bucket — the entire savings case rests on leaving hard queries exactly as expensive as they are today, not cutting corners on them.

5. **Estimate the savings range.** Compute a weighted average cost using the bucket distribution from step 3 and the tier costs implied by step 4 (derived from the pipeline description's own per-model/per-depth costs — never invent unit costs not derivable from what was provided). Present this as a **range** (e.g., "15-30% reduction"), not a single number, and name the two biggest sources of uncertainty driving that range (typically: sample representativeness, and whether the cheap tier actually holds the quality bar on Lookup queries — which this audit cannot verify without ground-truth labels).

6. **Flag risk cases explicitly.** Call out: queries that were hard to bucket, any Lookup-bucketed query that looks like it could be a disguised hard case (e.g., a short query with an ambiguous or loaded term), and the specific failure mode if the quality bar is tight (a cost audit does not replace calibration — a team with a strict SLA should expect to need the fuller calibrated planner, not just this routing sketch).

7. **Write the validation plan.** Recommend the smallest next step that tests the hypothesis without committing to the full infrastructure build: typically, shadow-route a held-out sample through the proposed cheap tier, compare answers against the current pipeline's output (or ground truth if available) on a sample stratified across the three buckets, and only promote the routing to live traffic once the Lookup bucket's quality gap (cheap vs. current) is measured and acceptable. State the minimum sample size needed for that validation (generally 50-100 queries per bucket for a first read).

## Output format

A single markdown document with these sections, in order:
1. **Pipeline Summary** — current flat cost/query, stated or inferred quality bar (with the inference flagged if applicable), sample size received.
2. **Bucket Distribution** — the table from step 3, with per-bucket rationale examples (2-3 representative queries per bucket).
3. **Recommended Tiering Plan** — the bucket-to-tier mapping from step 4.
4. **Estimated Savings Range** — the weighted-average computation from step 5, shown as a range with the uncertainty sources named.
5. **Risk Flags** — the specific cases and failure modes from step 6.
6. **Validation Plan** — the shadow-routing test from step 7, with the minimum sample size per bucket.

## Guardrails

- Never report a single-number savings figure — always a range, with the uncertainty sources named. A point estimate from an unlabeled log sample is false precision.
- Never recommend downgrading retrieval depth or model tier for the Complex/multi-hop bucket — the savings case depends entirely on leaving hard queries untouched.
- Never invent per-query costs, quality labels, or traffic volume not provided or derivable from the pipeline description — if a needed number is missing, say what's missing and give the estimate conditioned on an assumption, stated as an assumption.
- Never present the output as a calibrated SLA guarantee or a substitute for the full conformal-prediction-style planner — this is a go/no-go feasibility sketch, and the output must say so explicitly.
- Never silently drop or force-classify a query that's genuinely ambiguous to bucket — name it as ambiguous and note what additional signal (e.g., a correctness label, more context) would resolve it.
- If the provided log sample has no diversity (e.g., all queries look like Lookup, or fewer than 3 queries in any bucket), say the sample can't support a tiering recommendation yet rather than forcing a plan onto thin evidence.
