# RAG Freshness Watchdog: Catching Index-vs-Source Drift Before Users Do

Someone updates a policy doc. The wiki shows the new version. The RAG assistant keeps quoting the old one, confidently, for weeks — because nothing in the stack ever checks whether the index agrees with the source anymore.

## The Gap

A poster on r/Rag asked the question directly: "How do you check that your RAG index actually matches your source documents?" Their own description of the failure mode was blunt — "Over time they disagree: a file is updated but the old chunks stay in the index" — and they framed it as a request for a pattern, not a report of using one: "I'd like to hear how others handle it." That's the tell. Nobody in the thread named a standard tool, because there isn't one.

It isn't that nobody's tried. A search turned up a cluster of early, narrow attempts: PyPI packages `raghealth`, `ragfresh`, and `ragdrift`, a "RAG Staleness Check" Show HN project, and a drift-detection feature bolted onto `rag-sentinel`. `ragfresh` sits at 0 GitHub stars and admits outright that it "does not handle chunked stores yet." Nine cycles later, the same gap resurfaced independently in a fresh digest — this time from the production-failures and access-control angle, with a blog post describing users getting answers based on information "months out of date," and separate reporting flagging "stale permissions" between source systems and vector indexes as "the main risk" in permission-aware RAG. Two unrelated threads, a month apart, converging on the same unmet need is exactly the kind of recurrence that moves a gap from "interesting" to "worth building." The honest verdict is PARTIAL, not OPEN — real point-solutions exist — but none of them has become the thing a team just reaches for.

## The Project

The watchdog's job is reconciliation, not retrieval. It continuously compares three sources of truth that quietly drift apart in every real RAG deployment: the raw document store (S3, filesystem, or CMS, tracked by content hash), a processing/status ledger recording which hash was chunked when and into how many pieces, and the live vector index itself — the chunk IDs that actually exist there right now. Disagreement between any two of those three surfaces falls into one of three concrete drift classes: stale chunks (the source updated, but the old chunks never got removed), orphaned chunks (the source was deleted, but the index was never pruned), and missing chunks (a new source was added and never indexed at all). Each one gets flagged for re-indexing or routed to an operator, instead of silently waiting to be noticed by whoever reads a wrong answer next.

The build itself is a reconciliation job (polling or event-driven, depending on how fast a team's content actually changes), a status-ledger schema that gives the job something concrete to compare against, and a set of adapters for the vector databases teams are already running — pgvector, Pinecone, Qdrant, Weaviate. None of that is exotic engineering; the gap isn't technical difficulty, it's that nobody has packaged the three-way comparison as a drop-in layer instead of something every team quietly reinvents, badly, on their own.

## Tangible Impact

**Population**: Teams operating RAG assistants over living, frequently-edited document sets — internal policy/HR/IT wikis, insurance and benefits documentation, compliance Q&A tools, customer-support knowledge bases — where source content changes weekly or daily. Two independent r/Rag threads raising the same unmet need within one month suggests this is common pain among small-to-mid RAG teams, a population likely numbering in the thousands given the growth of internal LLM assistants through 2025–2026.
**Mechanism**: Automated reconciliation catches drift within a monitoring cycle instead of relying on someone noticing a stale answer; this directly stops the assistant from citing outdated policy, pricing, or support guidance to the employees or customers who query it.
**Measure**: % of injected test drift (synthetic file updates) detected and time-to-detect; reduction in "outdated info" tickets/complaints tagged by support teams after deployment; number of stale/orphaned chunks found and remediated per reconciliation run in a real deployment.

## Try It

A companion skill, `skills/rag-index-drift-watchdog/`, already exists for teams who want the design-review version before committing to the full service. Per its `SKILL.md`: it "reviews a described RAG ingestion architecture (source store, status ledger, vector index, update cadence) for where index-vs-source drift can occur undetected, classifies the specific stale/orphaned/missing-chunk exposures found, and drafts a minimal reconciliation job spec to close them — or explains why the team's existing reindex strategy already covers it."

To use it: paste `skills/rag-index-drift-watchdog/README.md` into any AI chat tool (ChatGPT, Claude, Copilot) and walk it through your own source store, status ledger, and vector index setup — or, if you're on Claude Code, drop the `rag-index-drift-watchdog/` folder into `~/.claude/skills/` and it activates the next time you're diagnosing why an assistant is citing something stale.

Two caveats belong here, straight from the idea's own risk list, not buried below the fold: reconciliation cost scales with corpus size and update frequency, so it has to stay cheap enough to run often or it becomes its own infra burden; and some teams may already be catching drift informally just by re-indexing nightly — before building the full watchdog, it's worth confirming that beats "just re-index" on cost and latency for your actual corpus size. The existing point-solutions are also young enough (`ragfresh` was created in August 2026, at 0 stars) that one of them maturing fast is a real possibility worth rechecking before a multi-week build.

Surfaced from `research/2026-11-11-rag-techniques.md`, pattern `P2`.
