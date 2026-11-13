---
name: rag-vs-long-context-router
description: One-shot calculator that turns a sample of a team's query logs, corpus token-size distribution, and LLM pricing into a recommended RAG-vs-long-context routing policy with a cost/accuracy estimate — use when a team is deciding whether to build a per-query router instead of committing to one architecture by default.
---

# RAG-vs-Long-Context Routing Policy Calculator

## When to use this
A team already has (or is building) a pipeline capable of both retrieval-augmented generation and long-context (stuff-the-documents-in) answering, and is currently locked into one of the two by default. The trigger moment is someone asking "should we route queries between RAG and long-context, or is it not worth the engineering effort?" — before anyone writes a classifier or a runtime router. This skill does the one-shot math that answers that question and, if the answer is yes, hands back a starting routing rule. It is NOT the always-on runtime router itself — it's the design calculation a team runs once to decide if building that router is worth it.

## Inputs
**Data source**: Manual — the user pastes (a) a sample of real or representative query log rows (at minimum: the query text or a short description, and ideally a category label such as "single-fact lookup" vs. "multi-hop/summarization"), (b) the corpus's token-count distribution for the context a query would need (percentiles or a histogram — e.g., "p50 context needed: 3K tokens, p90: 40K tokens, p99: 220K tokens"), and (c) the LLM provider's per-token pricing for input and output tokens on the model(s) in play, plus any retrieval/embedding cost per query if the RAG path has one. No connector or live pipeline access is required or used.

If any of the three inputs is missing, ask for it before computing anything — never substitute a guessed number for pricing or corpus size.

## Procedure
1. **Parse the query log sample.** For each query, determine (a) the approximate context size needed to answer it correctly — use a provided label if present, otherwise infer from the corpus token-distribution bucket the query implies (a query naming one document/section implies a small context; a query asking to "summarize all," "compare across," or "how many total across X" implies a context spanning most or all of the corpus) — and (b) a complexity bucket: single-fact lookup, multi-hop/synthesis, or full-corpus summarization. State the inferred bucket for every query that lacked an explicit label, so the user can correct it.
2. **Compute cost per query for two fixed baselines**, using the supplied pricing:
   - Always-RAG: (embedding/retrieval cost, if given) + (input tokens = the retrieved chunk size, typically the small end of the distribution) × input price + (output tokens, assume a stated or typical answer length) × output price.
   - Always-long-context: (input tokens = the full relevant context size per that query's bucket) × input price + output tokens × output price.
3. **Find the break-even context size** — the token count at which always-long-context's per-query cost equals always-RAG's per-query cost. This is the starting candidate threshold.
4. **Build a candidate routing rule**: route to long-context only when the query's needed-context estimate is below the break-even threshold AND its complexity bucket is single-fact or narrow multi-hop (not full-corpus summarization, which long-context handles categorically better but RAG cannot do at all regardless of cost — flag these as "must route long-context" rather than cost-optimized). Otherwise route to RAG.
5. **Simulate the routed policy against the log sample**: tally what fraction of sampled queries would go to each path under the candidate rule, and compute the blended cost per query.
6. **Estimate the accuracy side honestly.** If the user supplied their own eval results (e.g., "on 50 held-out queries, RAG scored X%, long-context scored Y%"), use those numbers directly and label them as user-measured. If not, state the directional finding from published benchmarks (long-context tends to score higher on correctness at materially higher per-query cost; RAG's relative advantage grows as corpus size grows past the point where retrieval can be precise) as "estimated from published literature, not measured on this team's data" — never present it as a measured number for their corpus.
7. **Make the build-or-skip call.** If the routed policy's blended cost saves less than roughly 15-20% versus whichever fixed baseline the team currently uses, or the log sample has fewer than ~30 queries, or the sample is nearly all one complexity bucket, say so explicitly and recommend a simple static heuristic (or staying with the current default) instead of building a full runtime router — the engineering cost of a router is not justified by a small or unproven gain.

## Output format
A single markdown report with these sections, in order:
1. **Inputs recap** — what was supplied, flagging anything inferred rather than given.
2. **Query bucket breakdown** — a table of complexity bucket × estimated context size × count/percentage from the sample.
3. **Cost comparison table** — always-RAG, always-long-context, and routed-policy blended cost per query, plus the break-even context-size threshold.
4. **Recommended routing policy** — the concrete rule (threshold + complexity carve-outs) if building is justified, stated as a rule someone could code directly.
5. **Accuracy caveat** — explicitly labeled as user-measured or literature-estimated, per step 6.
6. **Build-or-skip recommendation** — one paragraph, with the specific percentage savings and sample size that justify the call.

## Guardrails
- Never invent or carry over the idea's own example benchmark numbers (the "26x cost multiplier," "128K-token crossover") as universal constants — always compute the break-even threshold from the pricing and corpus distribution the user actually supplied.
- Never report an accuracy delta as measured when it's actually a literature estimate; always label the source of every accuracy claim.
- Never proceed with a guessed price or token distribution — stop and ask if any of the three required inputs is missing.
- Never recommend building the full always-on runtime router when the sample is too small (<~30 queries) or too homogeneous to support a real threshold — say the sample is insufficient instead of forcing a recommendation.
- Never conflate this one-shot calculator with the always-on runtime router described elsewhere — this skill produces a policy recommendation and cost estimate on a sample, not a deployed classifier.
