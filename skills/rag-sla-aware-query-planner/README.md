# RAG SLA-Aware Query Planner (Cost/Quality Tradeoff Audit)

A copy-paste prompt for auditing whether difficulty-tiered routing would meaningfully cut the cost of a production RAG (retrieval-augmented generation) pipeline, before anyone commits engineering time to building a runtime router. It takes a description of your current pipeline's cost and a sample of real query logs, buckets the queries by difficulty, and produces a reasoned savings estimate and a validation plan — not a calibrated production classifier.

## When to use this

Use this when you're running a RAG pipeline in production (or about to) and suspect every query — a simple one-fact lookup and a genuinely hard multi-hop question alike — is going through the same expensive retrieval depth and model tier. The right moment is *before* you build an actual query-difficulty classifier or router: you have (or can quickly pull) a sample of real query logs and know roughly what your current pipeline costs per query, and you want a go/no-go read on whether tiering is worth building, not the router already built.

This is NOT for writing the actual routing code or a production classifier (this produces a design/estimate document, not an implementation). It's NOT for checking whether one specific already-generated answer is correct or faithful to its sources (that's a single-transcript fact-check, a different task). And it's NOT general RAG tuning unrelated to cost — latency optimization, chunking strategy, or embedding model choice aren't what this prompt is built to assess.

## What to hand over

Required:
1. **Your pipeline description** — the retrieval method(s) you use (keyword/BM25, dense/vector, hybrid, with or without reranking), typical retrieval depth (top-k), the generation model(s) and tier (e.g., "GPT-4-class," "a 7B open model"), roughly how many queries you handle per day or month, and your current cost per query (or enough to derive it — $/1K tokens per model plus typical token counts). If you have an explicit quality target or SLA, state it; if not, say so.
2. **A sample of real query logs** — at least 15, ideally 30-100 queries actually sent to your pipeline. For each, give the query text and, if you have them: the current answer, a correctness/quality label, latency, or per-query cost. Logs without quality labels still work — difficulty gets classified from the query text itself — but say so, since without ground truth the savings estimate can only be flagged as unvalidated, not proven.

Optional but helpful:
- Any routing heuristic you've already considered (e.g., "we thought about routing by query length").
- A target cost-reduction number, if you have one in mind.

If you have fewer than 15 queries, the audit can still run, but the bucket percentages get labeled a low-confidence draft, and you'll be told plainly that a bigger, more representative sample is needed before trusting the savings range. Nothing gets invented on your behalf — no made-up queries, costs, or quality labels.

## The procedure to follow

1. **State the current flat cost and quality bar.** Pin down the single cost-per-query figure the pipeline incurs today for every query, and the stated or inferred quality target. If no quality bar was given, that gets flagged explicitly — without an independent correctness signal, the audit can only measure *consistency* with today's answers, not whether today's answers are actually right.

2. **Bucket every query by difficulty**, using only the query text (never invented metadata): **Lookup** (single-fact, named-entity, definitional — answerable from one passage), **Moderate** (combining 2-3 facts or light reasoning, comparisons), **Complex/multi-hop** (synthesizing across multiple documents, multi-step reasoning, open-ended or ambiguous). Each query gets a one-line rationale. Genuinely ambiguous queries get flagged as ambiguous rather than forced into a bucket.

3. **Build the bucket distribution** — count and percentage per bucket — stated plainly as a property of *this sample*, not of your full traffic, especially if the sample is under ~50 queries or wasn't drawn randomly.

4. **Recommend a tier-to-bucket mapping**: Lookup gets shallow retrieval (low top-k, no reranking) plus the cheapest viable model; Moderate gets mid-depth retrieval, optional reranking, and a mid-tier model; Complex/multi-hop keeps your current full pipeline exactly as-is. The Complex bucket never gets downgraded — the whole savings case rests on leaving hard queries untouched, not cutting corners on them.

5. **Estimate a savings range, not a single number.** The weighted-average cost is computed from the bucket distribution and the tier costs implied by step 4, using only unit costs derivable from what you provided — never invented. It's presented as a range (e.g., "15-30% reduction") with the two biggest sources of uncertainty named — typically sample representativeness, and whether the cheap tier actually holds the quality bar on Lookup queries (which this audit alone can't verify without ground-truth labels).

6. **Flag the risk cases.** Hard-to-bucket queries, any Lookup-looking query that might secretly be a hard case (a short query with an ambiguous or loaded term), and the honest caveat that if your SLA is tight, this routing sketch isn't a substitute for a fully calibrated planner — it's the feasibility check that tells you whether building one is worth it.

7. **Write a validation plan, not a victory lap.** The recommended next step is to shadow-route a held-out sample through the proposed cheap tier, compare its answers against your current pipeline's output (or ground truth, if you have it) stratified across the three buckets, and only promote routing to live traffic once the Lookup bucket's quality gap is measured and acceptable. A minimum sample size for that first read — generally 50-100 queries per bucket — gets stated.

## Output format

A single document with six sections, in this order:

1. **Pipeline Summary** — current flat cost/query, quality bar (flagged if inferred rather than stated), sample size received.
2. **Bucket Distribution** — the counts/percentages per bucket, with 2-3 representative example queries per bucket.
3. **Recommended Tiering Plan** — the bucket-to-tier mapping from step 4.
4. **Estimated Savings Range** — the weighted-average computation, shown as a range with uncertainty sources named.
5. **Risk Flags** — the specific cases and failure modes from step 6.
6. **Validation Plan** — the shadow-routing test from step 7, with the minimum sample size per bucket.

## Rules this always follows

- Never a single-number savings figure — always a range, with uncertainty sources named. A point estimate from an unlabeled log sample would be false precision.
- Never recommends downgrading retrieval depth or model tier for the Complex/multi-hop bucket — the savings case depends on leaving hard queries exactly as expensive as today.
- Never invents per-query costs, quality labels, or traffic volume that weren't provided or derivable from the pipeline description — missing numbers get named as missing, with any estimate conditioned on a stated assumption.
- Never presents the output as a calibrated SLA guarantee or a substitute for a full conformal-prediction-style production planner — this is a go/no-go feasibility sketch, stated as such.
- Never silently drops or force-classifies a genuinely ambiguous query — it gets named as ambiguous, with a note on what additional signal (a correctness label, more context) would resolve it.
- If the log sample has no real diversity (e.g., everything looks like Lookup, or fewer than 3 queries land in some bucket), the honest answer is that the sample can't support a tiering recommendation yet — not a plan forced onto thin evidence.

## Example of what this produces

Pipeline: a SaaS help-desk vendor running hybrid retrieval (BM25 + dense, top-20) with reranking, feeding a GPT-4-class model for every query, ~500,000 queries/day, averaging $0.018/query, no explicit SLA stated beyond "answers should match what our support team would say." Sample: 40 real support queries.

Bucketing finds 45% Lookup ("what's your refund window," "how do I reset my password"), 35% Moderate ("why was I charged twice this month"), 20% Complex ("my integration broke after your last update and I've already tried X — what's actually going on"). The recommended plan routes Lookup to shallow retrieval (top-5, no rerank) with a cheaper model, Moderate to mid-depth retrieval with the same reranker but a mid-tier model, and leaves Complex untouched. The estimated savings range comes out around 20-35%, with the uncertainty flagged as: no correctness labels were provided, so the quality impact on the 45% Lookup bucket is unverified, and the sample is support-queue text only — not necessarily representative of the full 500K/day mix. The validation plan recommends shadow-routing 100 Lookup-bucketed queries through the cheap tier for two weeks and comparing against current output before touching live traffic.
