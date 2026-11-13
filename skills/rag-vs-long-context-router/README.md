# RAG-vs-Long-Context Routing Policy Calculator

A paste-in prompt for any AI chat tool. Use it when your team already has (or is building) a pipeline that can answer questions either by retrieval-augmented generation (RAG) or by stuffing relevant documents straight into a long-context model, and you're locked into one of the two by default — and you want to know, with real numbers, whether building a per-query router is worth the engineering effort, and if so, what rule it should use. This is a one-shot design calculation you run before building anything, not a running system.

## What you need to provide

This is a manual, paste-in skill — no API or connector access is used or needed. Hand over three things:

1. **A sample of query logs** — at least 30 real or representative queries your system has handled or will handle, ideally labeled by type (e.g., "single-fact lookup," "multi-hop," "summarize across documents"). If you don't have labels, just paste the query text and the calculator will infer buckets and show you its guesses so you can correct them.
2. **Your corpus's token-size distribution** — roughly how large the context needed to answer a typical query is, at a few percentiles (e.g., "most queries need ~3K tokens of context, 90th percentile needs ~40K tokens, worst case ~220K tokens"). A rough estimate is fine.
3. **Your LLM provider's per-token pricing** — input and output price per token (or per million tokens) for whichever model(s) you'd use for RAG and/or long-context, plus any retrieval/embedding cost per query if your RAG path has one.

If you don't have one of these three, say so — the calculator will tell you what's missing rather than guessing at numbers.

## What it does

Paste the prompt below along with your three inputs into any AI chat tool.

```
You are a RAG-vs-long-context routing policy calculator. I will give you:
1. A sample of query logs (text and, if available, a complexity label: single-fact lookup, multi-hop/synthesis, or full-corpus summarization)
2. My corpus's token-size distribution (percentiles of context needed per query)
3. My LLM provider's per-token input/output pricing, and any retrieval/embedding cost per query

Do the following, in order, and show your work:

1. For every query in my sample, state its complexity bucket (use my label if given; otherwise infer one from the query text and corpus distribution, and flag it as inferred).
2. Compute the cost per query for "always-RAG" (retrieval cost if any, plus small-context input tokens, plus output tokens, at my supplied pricing) and "always-long-context" (full relevant-context input tokens plus output tokens, at my supplied pricing).
3. Find the break-even context size where always-long-context costs the same as always-RAG per query.
4. Propose a routing rule: route to long-context only below that break-even size AND when the query isn't a full-corpus summarization (which only long-context can do regardless of cost — flag those as "must route long-context"); otherwise route to RAG.
5. Simulate that rule against my query sample: what fraction goes each way, and what's the blended cost per query versus each fixed baseline.
6. Give an honest accuracy caveat: if I gave you my own eval numbers, use those and say so; if not, state the general direction from published research (long-context tends to score higher on correctness at much higher cost; RAG's relative advantage grows as corpus size grows) and explicitly label it as a literature estimate, not something measured on my data.
7. Tell me plainly whether building an always-on router is worth it: if the routed policy saves less than roughly 15-20% versus my current default, or my sample has fewer than ~30 queries, or it's almost all one complexity bucket, say the gain doesn't justify building a router and suggest sticking with a simple static rule or my current default instead.

Never invent pricing or token-size numbers — if I haven't given you one of the three inputs, ask me for it before computing anything. Never present a literature-based accuracy estimate as if it were measured on my data. Give me the answer as a report with these sections: Inputs Recap, Query Bucket Breakdown (table), Cost Comparison (table, with the break-even threshold), Recommended Routing Policy (a concrete rule), Accuracy Caveat, and Build-or-Skip Recommendation.

Here is my data:
[paste query log sample]
[paste corpus token-size distribution]
[paste pricing]
```

## What you get back

A short report:
- **Inputs recap** — what you gave it, and anything it had to infer.
- **Query bucket breakdown** — a table of complexity type, context size, and share of your sample.
- **Cost comparison** — always-RAG vs. always-long-context vs. the proposed routed policy, per query, plus the break-even token threshold.
- **Recommended routing policy** — a concrete, codeable rule (a token threshold plus complexity carve-outs), only if the numbers justify building one.
- **Accuracy caveat** — clearly labeled as either your own measured numbers or a literature-based estimate.
- **Build-or-skip call** — a direct recommendation, with the specific savings percentage and sample size behind it.

## What this is not

This is not a deployed, always-running classifier that sits in front of your pipeline and routes live traffic — it's the napkin math you do first to decide whether that's worth building at all, and if so, what starting rule to code. It also won't tell you your system's real accuracy numbers unless you supply your own eval results; without those, it gives you the general direction from published research and says so plainly.
