---
name: rag-agentic-building-blocks-library
description: Given a team's RAG use case, query types, and current pipeline, recommends which of the five agentic-RAG patterns (query rewrite, query decomposition, multi-hop retrieval, tool/source routing, self-check/self-correction) are actually worth adopting, in what order, and why — a one-shot design/triage aid, not the runtime library itself.
---

# Agentic RAG Pattern Fit

## When to use this

Reach for this skill when a team already has (or is about to build) a RAG pipeline and the question is specifically "which of the five known agentic-RAG patterns should we actually add, and in what order" — not "how do I build RAG" in general, and not "please implement this for me." The trigger moment: someone can describe their use case, list or paste a handful of representative real queries, and describe what their pipeline does today (e.g., "plain single-shot retrieve-then-generate," or "we already rewrite queries but nothing else"). They want a reasoned recommendation before spending engineering weeks bolting on patterns that may not pay for themselves.

Do not use this for: writing the actual implementation code for any pattern (that's a build task); auditing an existing hand-rolled agentic loop for bugs like missing retry caps or malformed tool-call handling (that's a code-review task — a different skill entirely, scoped to inspecting code someone already wrote); choosing the underlying retrieval architecture — dense vs. BM25 vs. hybrid vs. graph-RAG (that's an index/storage decision, separate from which reasoning patterns sit on top of retrieval); or running a real benchmark with measured recall@k/latency/cost on the team's actual data (this skill is a reasoned first-pass triage, explicitly lighter-weight than that, and should say so).

## Inputs

**Data source**: Manual — the user pastes (1) a one- or two-sentence description of the use case (e.g., "internal support bot over product docs," "research assistant over a legal case corpus"), (2) 5–15 representative real or realistic queries users actually ask (not abstract categories — actual question text), (3) a description of what the pipeline does today (e.g., "single-shot dense retrieval, no rewriting, no verification" or "we already do query rewriting via a prompt template"), and (4) any known constraints: latency budget per query, number of distinct retrieval sources/tools in play, and whether answers must be strictly grounded (e.g., compliance/legal/medical context) or can tolerate occasional ungrounded answers. No connector or live pipeline access is read or required — this is pure reasoning over what the user describes.

If the use case or the query sample is missing, ask for it before producing a recommendation — do not substitute a generic/assumed use case.

## Procedure

1. **Classify the query sample.** From the pasted queries, tag each as: single-fact lookup, multi-hop/compositional (needs facts from 2+ places combined), ambiguous/underspecified (needs rewriting to be answerable), or requiring a specific named source/tool (e.g., "check the database" vs. "check the docs"). Report the rough proportion of each type across the sample.
2. **Evaluate each of the five patterns against the classified sample and stated constraints**, using these decision rules. First, for any pattern the user's "what the pipeline does today" description says is already implemented, mark it **ALREADY ADOPTED** and move on — never re-recommend a pattern as a fresh ADOPT just because the decision rule below would otherwise favor it:
   - **Query rewrite** — ADOPT if any meaningful share of queries are ambiguous, colloquial, or missing context the retriever needs verbatim. This is the lowest-cost pattern (one extra LLM call); default to recommending it unless the sample is already query-perfect.
   - **Query decomposition** — ADOPT only if a meaningful share of queries are multi-hop/compositional; SKIP if the sample is almost entirely single-fact lookups, since decomposition adds LLM calls and latency with no benefit on those queries.
   - **Multi-hop retrieval (stateful, carries prior evidence forward)** — ADOPT only alongside decomposition, and only if the pipeline doesn't already carry retrieved evidence across steps; redundant to add without decomposition since there's nothing to chain.
   - **Tool/source routing** — ADOPT only if there are genuinely 2+ distinct sources/tools AND the user can supply (or commit to writing) clear per-source descriptions; flag explicitly that routing quality degrades to near-random without well-written source descriptions, so this is conditional on that commitment, not just the source count.
   - **Self-check/self-correction** — ADOPT if grounding matters (compliance/legal/medical, or the team has had hallucination complaints) or the latency budget tolerates a retry; SKIP or flag as "adopt with a hard retry cap" if the latency budget is tight, since unbounded self-correction loops are a known runaway-cost failure mode.
3. **Estimate relative cost** for each ADOPT recommendation in extra-LLM-calls-per-query terms (rewrite: +1 call; decomposition+multi-hop: +2 to +N calls depending on sub-question count; routing: +1 call; self-check: +1 to +(retry cap) calls) and flag if the stated latency budget looks incompatible with the combined recommendation.
4. **Sequence the adoptions.** Order ADOPT verdicts by cost-to-benefit: cheapest-and-highest-impact first (typically rewrite), ending with the most expensive/riskiest (typically self-check with retries, or decomposition+multi-hop if the multi-hop share is small but nonzero).
5. **Call out gaps explicitly** when the inputs don't support a confident verdict (e.g., "you didn't say whether answers need strict grounding — self-check's priority depends entirely on that; here's the recommendation under each assumption").

## Output format

A single markdown report with:
1. **Query sample breakdown** — the proportions from step 1.
2. **Pattern-by-pattern table**: Pattern | Verdict (ALREADY ADOPTED / ADOPT NOW / ADOPT LATER / SKIP) | Reasoning (tied to the specific inputs given) | Rough added cost.
3. **Recommended adoption order** — a numbered sequence for the ADOPT verdicts only.
4. **Open questions** — anything the user needs to answer before the recommendation firms up (e.g., missing latency budget, missing grounding requirement).
5. One line making explicit: this is a design triage, not a benchmark — recommend validating the top pick against a real multi-hop eval set before treating the ranking as final.

## Guardrails

- Never recommend all five patterns by default — that's the exact failure mode (production systems defaulting to "add everything") this skill exists to prevent; every ADOPT must trace to something specific in the pasted queries or stated constraints.
- Never write or paste implementation code for any pattern — this skill produces a recommendation and reasoning only.
- Never claim a measured accuracy or latency number — only relative/rough cost framing (extra LLM calls, qualitative latency risk) unless the user supplies real benchmark data.
- Never treat tool/source routing as adoptable purely because 2+ sources exist — always condition it on source-description quality, and say so explicitly if the user hasn't mentioned writing any.
- Never silently assume a grounding requirement — if the user didn't state whether strict grounding matters, ask or present the self-check verdict conditionally rather than picking one assumption.
- If fewer than 5 representative queries are supplied, say the classification confidence is low rather than presenting proportions as if precise.
