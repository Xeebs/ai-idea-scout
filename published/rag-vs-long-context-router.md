Every team that's ever built a document-QA product hits the same fork in the road: do we retrieve-then-generate, or just stuff the whole thing into a model's context window? Most teams pick one answer and live with it forever — not because they ran the numbers, but because nobody built the thing that would let them.

## The Gap

A May 2026 arXiv paper, "Route Before Retrieve" (Pre-Route), makes an uncomfortable point about the field's go-to precedent: Google's widely-cited "Self-Route" approach always tries RAG first and only falls back to long-context when retrieval comes up short. That's backwards, Pre-Route argues — the decision about which architecture a query needs should happen *before* you spend the cost of either one, not after RAG has already failed.

The numbers make the stakes concrete. One cited 2026 benchmark found long-context prompting edges out RAG on raw correctness, but at roughly 26x the per-query token cost. Another found the lines cross the other way above roughly 128K tokens of context, where RAG pulls ahead for most open models. Put those two findings together and the uncomfortable conclusion is that there is no single right answer — the right architecture depends on the query and the corpus, not on a company-wide decision made once in a design doc.

And yet that's exactly how most teams operate: always-RAG or always-long-context, chosen once and left alone. When someone does bother to build routing logic, they derive it ad hoc, per team, from scratch. A GitHub search for a RAG-vs-long-context router turned up exactly one implementation worth noting — a zero-star personal reproduction of the Self-Route paper. Everything else is either academic precedent (Self-Route, Pre-Route, RAGSmith) or a vendor blog describing a heuristic they built internally and never shared. There is no widely-adopted, open-source router anyone can actually drop in.

## The Project

The project is an open-source, pluggable router that sits in front of a pipeline capable of both RAG and long-context answering and decides, per incoming query, which architecture to use — calibrated against a team's own cost, latency, and accuracy tradeoffs rather than a fixed bet made at design time.

Three pieces make it work. First, a cheap query-classification step, informed by the published Self-Route/Pre-Route approach, using either a small fast model or a heuristic to judge a query's complexity and how much corpus coverage it actually needs. Second, a tunable decision policy the operator controls — something as simple as "prefer RAG unless the predicted accuracy gain outweighs its cost multiplier." Third, and maybe most important, a benchmarking harness that lets a team validate the router's choices against a post-hoc oracle — the architecture that, in hindsight, actually performed better for each specific query — before anyone has to trust it in production.

The centerpiece isn't a clever model. It's the discipline of treating "RAG or long-context" as a per-query decision instead of an org-wide default, and giving teams a way to prove that decision is actually paying for itself before they rely on it.

## Tangible Impact

**Population**: Engineering teams building production RAG/LLM applications over corpora in the roughly 50K-500K-token range per potential context — the band where the digest's own cited benchmarks show the RAG-vs-long-context choice is genuinely ambiguous, not a huge enterprise with unlimited long-context budget or a tiny app where RAG is obviously sufficient. This spans most mid-scale internal search tools, customer-support knowledge bases, and document-QA products currently committed to one architecture by default.

**Mechanism**: Routing per query avoids both failure modes the digest cites — paying 26x the token cost for long-context on a query RAG would have answered just as well, or getting a worse RAG answer on a query that actually needed full-document context — turning a one-time architectural bet into a continuously-optimized per-query decision.

**Measure**: average per-query cost reduction versus an always-long-context baseline at matched accuracy; accuracy improvement versus an always-RAG baseline at matched cost; percentage of queries where the router's choice matches the post-hoc oracle (the architecture that actually performed better for that specific query).

## Try It

A companion skill already exists: [`skills/rag-vs-long-context-router/`](../skills/rag-vs-long-context-router/) — "One-shot calculator that turns a sample of a team's query logs, corpus token-size distribution, and LLM pricing into a recommended RAG-vs-long-context routing policy with a cost/accuracy estimate — use when a team is deciding whether to build a per-query router instead of committing to one architecture by default."

This is deliberately the lighter-weight half of the idea: it doesn't run as a live router, it's the design calculation a team runs *once* to decide whether building the real router is even worth the engineering effort. To use it, either paste the contents of its `README.md` into any AI chat tool along with your query log sample, corpus token-count distribution, and LLM pricing — or drop the `rag-vs-long-context-router/` folder into `~/.claude/skills/` if you're working in Claude Code, and it'll be available on demand.

Worth noting up front, because it belongs in the open as much as the opportunity does: the one existing GitHub reproduction of the underlying Self-Route research is a zero-star personal project with no production validation behind it. The published research holds up in its own paper's benchmark — whether it holds up on your corpus, with your query mix, is exactly what the skill's calculation and the project's benchmarking harness are for. There's also a real risk that a much simpler static rule ("always long-context below N tokens, always RAG above") gets you 90% of the benefit without any of the routing complexity — if you're building this, that's the first baseline to beat, not an afterthought.

Surfaced from `research/2026-11-12-rag-techniques-iii.md`, pattern `P6`.
