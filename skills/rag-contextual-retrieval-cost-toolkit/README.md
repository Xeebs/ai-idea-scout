# Contextual Retrieval Cost Calculator

A paste-into-any-AI-chat-tool prompt that answers one question before you build anything: **"Is Anthropic's contextual retrieval technique worth the indexing cost for my corpus, and should I apply it to every chunk or just some?"**

Contextual retrieval means prepending a short LLM-generated sentence of context to each chunk before you embed it and index it for BM25 — Anthropic reported it cuts top-20 retrieval failure by up to 49% (67% with reranking). The catch: generating that per-chunk context costs an LLM call per chunk, and every public writeup on it says "use prompt caching" without giving you numbers for your own corpus. This tool gives you those numbers as a planning estimate, before you write any code.

## What this does not do
It does not read your actual documents, run any code, call any API, or measure real retrieval accuracy. It is a cost-estimation conversation based on what you describe. It will not tell you "this will definitely work" — it tells you "here's roughly what three different ways of doing this would cost, and which one to try first."

## What to hand it

Paste the following, filled in with your own numbers:

```
I'm considering Anthropic's contextual retrieval technique for my RAG corpus. Here's my setup:

- Total chunk count (or document count + chunks per doc): <e.g. "about 40,000 chunks across 3,000 documents">
- Average chunk length: <e.g. "~250 tokens per chunk">
- Document type/structure: <e.g. "internal engineering wikis — mostly narrative prose with
  some embedded tables and code snippets">
- LLM I'd use for context generation: <e.g. "Claude Haiku" or "GPT-4o-mini">
- Current pricing for that model (if you know it): <e.g. "$0.80/M input tokens, $4/M output
  tokens" — or say "I don't know, use your best recent estimate and flag it">
- Prompt caching available on this provider: <yes/no/not sure>

Please estimate the indexing cost of:
1. Applying contextual retrieval to every chunk with no caching (naive baseline)
2. Applying it to every chunk using whole-document prompt caching
3. Applying it only to chunks that are likely context-dependent (selective), using caching

Then recommend which one I should start with, and tell me plainly what this estimate can't
tell me about actual retrieval accuracy on my data.
```

## What it will produce

A short report with five parts, in this order:

1. **Inputs recap** — restates what you gave it, and flags anything it had to assume because you left it blank.
2. **Cost estimate table** — three rows (naive full-corpus, cached full-corpus, cached + selective), each with an estimated total token volume, an estimated dollar cost, and that cost as a percentage of the naive baseline.
3. **Recommendation** — one paragraph telling you which approach to start with. As a rule of thumb: if your corpus is mostly self-contained chunks (FAQ entries, glossary definitions, atomic code functions), selective application saves real money. If your corpus is almost entirely context-dependent (dense narrative, tables without headers, pronoun-heavy writing), selective filtering won't save much and the simpler cached-full-corpus approach may be the better tradeoff. If your corpus is under roughly 500 chunks, the dollar difference between all three approaches is probably small enough that it's not worth engineering around.
4. **Caveats**, stated plainly, not buried in a footnote:
   - Every cost number is an estimate. If you didn't supply current pricing, the number used is a last-known figure that must be checked against the provider's live pricing page before you budget against it.
   - The ambiguous-chunk percentage used for the "selective" scenario is a heuristic based on your document-type description, not a measurement of your actual chunks. A real classifier run against a sample of your real chunks would give you a more trustworthy number.
   - This estimate says nothing about whether contextual retrieval will actually improve your retrieval accuracy. Anthropic's cited 49-67% failure-rate reduction was measured on Anthropic's own benchmark. You'd need a before/after eval on your own query set to know if it helps your corpus specifically.
5. **Next step** — one sentence on what to build next if you want a real answer instead of an estimate (classify a sample of a few hundred real chunks, then run a before/after retrieval eval on your own query set).

## How to read the output
Treat this as a go/no-go planning aid, not a budget you can commit to a stakeholder without double-checking current API pricing yourself. It's meant to save you from applying an expensive technique uniformly to a corpus where most chunks don't need it — and from building the full selective-classification + eval-harness tooling before confirming the cost tradeoff is even worth the engineering effort.

## Limitations (be upfront about these)
- If you don't know your corpus size or chunk length precisely, estimate on the high side — underestimating chunk count is the most common way this kind of planning estimate ends up wrong in the field.
- This does not replace an actual eval harness. If the estimate says "selective application looks worth it," the next real step is building a small classifier and testing it against a retrieval eval on your own data — not shipping straight to production.
- Prompt caching pricing, cache TTLs, and discount percentages vary by provider and change over time. Any specific caching discount percentage this tool cites should be treated as illustrative, not current, unless you supplied it yourself.
