# Agentic RAG Pattern Fit

A self-contained prompt template for deciding which of the five known agentic-RAG patterns — query rewrite, query decomposition, multi-hop retrieval, tool/source routing, and self-check/self-correction — your team should actually adopt, and in what order. Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your own details, or drop this folder into a Claude Code `skills/` directory.

## When to use this

Use this when you already have, or are about to build, a RAG pipeline and the real question is narrower than "how do I build RAG" — it's "which of the five agentic patterns are actually worth bolting on, and which would just add latency and cost with no payoff." The right moment to use it is before you start wiring up a new pattern, not after.

This is not the right tool if you want:
- Actual implementation code for any pattern — this gives you a recommendation and reasoning, not code.
- A code review of a RAG loop you've already written (missing retry caps, malformed tool-call handling, etc.) — that's a different task.
- A choice between retrieval architectures (dense vs. BM25 vs. hybrid vs. graph-RAG) — that's an indexing decision, separate from which reasoning patterns sit on top.
- A real measured benchmark (recall@k, latency, cost on your actual data) — this is a reasoned first-pass triage that should be validated against a real eval set afterward, not a substitute for one.

## What to hand over

You need to supply, in your own words:
1. **Your use case** in one or two sentences (e.g., "internal support bot over our product docs," "research assistant over a corpus of legal filings").
2. **5–15 real or realistic queries** your users actually ask — the actual question text, not abstract categories. More than 5 gives higher-confidence results; fewer than 5 will be flagged as low-confidence.
3. **What your pipeline does today** — e.g., "plain single-shot retrieve-then-generate, no rewriting, no verification" or "we already rewrite queries but nothing else."
4. **Known constraints** — your per-query latency budget if you have one, how many distinct retrieval sources/tools are in play, and whether answers must be strictly grounded (compliance, legal, medical) or can occasionally tolerate an ungrounded answer.

Everything here is information you type or paste yourself — this skill does not connect to any API, database, or live pipeline. It only reasons over what you describe.

If you don't have a use-case description or query sample ready, provide those first — a recommendation without them is just a generic checklist, not a tailored one.

## The procedure, in prose

1. **Classify your queries.** Each pasted query gets tagged as one of: single-fact lookup, multi-hop/compositional (needs facts combined from two or more places), ambiguous/underspecified (needs rewriting before it's answerable as-is), or source-specific (clearly points at one particular tool or database rather than general documents). The proportions of each type across your sample drive everything downstream.

2. **Score each of the five patterns** against your classified sample and stated constraints. First, anything you said your pipeline already does gets marked ALREADY ADOPTED and isn't re-recommended as a new build, even if the decision rule below would otherwise favor it:
   - **Query rewrite** — recommended by default unless your sample queries are already unambiguous and well-specified. It's the cheapest pattern (one extra model call), so the bar to adopt it is low.
   - **Query decomposition** — only worth it if a real share of your queries are multi-hop/compositional. If your sample is almost all single-fact lookups, this gets a SKIP — it adds calls and latency for queries that don't need it.
   - **Multi-hop retrieval (carrying prior evidence forward across steps)** — only makes sense paired with decomposition. Recommending it alone, without decomposition, is flagged as redundant.
   - **Tool/source routing** — only worth it if you genuinely have two or more distinct sources or tools, AND you're willing to write (or already have) clear per-source descriptions. Routing quality falls apart with vague or missing source descriptions, so this verdict is explicitly conditional on that commitment, not just on source count.
   - **Self-check/self-correction** — worth it if grounding really matters for your use case (compliance, legal, medical, or you've had hallucination complaints) or your latency budget can absorb a retry. If your latency budget is tight, this gets flagged as "adopt only with a hard retry cap" — unbounded self-correction loops are a known way to blow up cost and latency.

3. **Rough cost estimate** for each recommended pattern, in terms of extra model calls per query (rewrite: +1; decomposition + multi-hop together: +2 or more depending on how many sub-questions typically result; routing: +1; self-check: +1 to +however many retries you cap it at). If the combined recommended set looks incompatible with your stated latency budget, that gets called out directly.

4. **A recommended adoption order** — cheapest, highest-payoff pattern first (usually query rewrite), most expensive/riskiest last (usually self-check with retries, or decomposition+multi-hop when the multi-hop share of your queries is real but small).

5. **Open questions** — anything your inputs didn't cover that materially changes the recommendation (most commonly: you didn't say whether grounding is strict, so self-check's priority is given under both assumptions rather than guessed).

## Output format

Expect back:
1. A short breakdown of your query sample by type and the rough proportions.
2. A table: Pattern | Verdict (ALREADY ADOPTED / ADOPT NOW / ADOPT LATER / SKIP) | Reasoning tied to your specific inputs | Rough added cost.
3. A numbered recommended adoption order, covering only the ADOPT verdicts.
4. A list of open questions you should answer before treating the ranking as final.
5. A closing line reminding you this is a design triage, not a benchmark — validate the top recommendation against a real eval set before committing engineering time.

## Guardrails

- It will never hand back "adopt all five" as a default recommendation — every ADOPT has to trace to something specific you described, since defaulting to everything is exactly the bloat this exercise exists to avoid.
- It will never produce implementation code — only the recommendation and reasoning.
- It will never state a precise accuracy or latency number unless you supplied real measured data — only relative cost framing (extra calls, qualitative latency risk).
- It will never mark tool/source routing as worth adopting purely because you have multiple sources — it should always check whether you can commit to writing clear per-source descriptions first.
- It will never silently guess your grounding requirement if you didn't state one — expect it to ask, or to show the self-check verdict under both assumptions.
- If you give fewer than 5 sample queries, expect it to flag the classification as low-confidence rather than presenting precise-looking proportions.
