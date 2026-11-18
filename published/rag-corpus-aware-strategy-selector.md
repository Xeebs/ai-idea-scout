# Fit Check: A Corpus-Aware Retrieval Strategy Selector for RAG

Every team standing up a RAG system faces the same unglamorous question in week one: dense, hybrid, reranked, or graph? Right now the honest answer is "whichever one the last tutorial you read happened to use." There are more eval frameworks measuring RAG quality than there are tools that actually tell you which *architecture* fits your corpus in the first place — a gap the people building the eval frameworks haven't noticed they're not closing.

## The Gap

The clearest articulation of the problem comes from an OpenAI community forum thread titled, bluntly, "RAG is not really a solution" — its author's complaint isn't that RAG is bad, it's that there's no systematic way to pick a technique for a given corpus before you build. That's not a lone gripe. A 2025 arXiv survey lines up five actively-promoted eval frameworks — RAGAS, DeepEval, TruLens, SCARF, RAG Playground — and shows each one defines "relevance," "correctness," and "faithfulness" differently. Teams have no shortage of metrics; what they lack is an agreed way to turn a sample of their own corpus into a concrete, evidence-backed decision among dense, BM25, hybrid, reranked, and graph retrieval.

The closest anyone has gotten to fixing this is RAGRouter-Bench, a January-2026 benchmark that standardizes five RAG paradigms across 7,727 queries. It's the right foundation — except its own April-2026 follow-up paper says outright that "no classifier has been trained on this benchmark." A `gh search` for "RAG evaluation framework" turns up more than ten actively-maintained repos (RAGnarok-AI, evalkit, BenchRAG, EdgeRAG, and a scatter of DeepEval-based projects), each with its own metric set and none dominant. Put together: the comparison data now exists to build a corpus-aware selector, but nobody has actually built one. Discussion and an unsolved benchmark are not the same thing as a tool you can run.

## The Project

The fix is a small harness, not another eval framework competing for the same seventh slot. It takes a sample of a team's real corpus plus a handful of representative queries — ideally with graded relevance judgments, but able to bootstrap synthetic ones when a team doesn't have labeled queries yet — and runs that sample through four to six standard retrieval configurations: dense, BM25, hybrid, reranked, and a lightweight graph variant. Rather than inventing a seventh metric scheme to add to the pile the arXiv survey already catalogued, it borrows one consistent set from the existing eval-framework landscape and applies it uniformly across every configuration.

What comes out the other end is a ranked recommendation backed by actual numbers measured on *their* data — recall@k, latency, and cost per query for each configuration — not a generic best-practices essay a team could have gotten from any blog post. The goal is to replace "we picked hybrid because that's what the tutorial used" with "we picked hybrid because it beat dense by 12 points of recall@10 on our own 50-query sample, at an acceptable latency cost."

## Tangible Impact

**Population**: Engineering teams (typically 1–10 people) standing up a new RAG system who lack a dedicated ML/retrieval specialist — the same profile implied by the OpenAI forum complaint and the proliferation of single-purpose eval repos, where teams default to whatever technique a tutorial used rather than what fits their corpus.
**Mechanism**: Running the actual candidate architectures against the team's own sampled data instead of relying on generic advice surfaces which technique genuinely fits their corpus shape (document length, redundancy, structure) before they commit engineering weeks to one path, cutting the "built the wrong architecture, now rebuilding" cycle visible across the fragmented eval-framework landscape.
**Measure**: recall@k and cost/latency delta between the harness's top recommendation and the team's originally-planned default; rebuild rate (how often a team that ran the harness later rearchitects their retrieval layer, versus a baseline cohort that skipped it); time from "starting RAG build" to "architecture locked in."

## Try It

A companion skill exists at [`skills/rag-corpus-aware-strategy-selector/`](../skills/rag-corpus-aware-strategy-selector/): *"Given a description of a team's corpus and a handful of representative queries, reasons through which retrieval architecture (dense, BM25/keyword, hybrid, hybrid+reranker, or graph-RAG) is the best starting point and why. Use when a team is about to build or rebuild a RAG pipeline and wants a first-pass, judgment-based recommendation before committing engineering weeks to one path — not a benchmarked result and not a full end-to-end RAG build-out guide."*

This is deliberately a lighter, judgment-only stand-in for the full harness above — it reasons through corpus characteristics and query types using a documented heuristic rubric, not a live benchmark run, and it says so explicitly in its output. To use it: paste the contents of `skills/rag-corpus-aware-strategy-selector/README.md` into any AI chat tool along with your corpus profile (document count, length, structure, domain) and 5–10 example queries, or drop the whole `skills/rag-corpus-aware-strategy-selector/` folder into `~/.claude/skills/` if you're working in Claude Code.

A few honest caveats worth weighing before leaning on either the skill or the full harness. Synthetic query generation — the fallback for corpora without labeled queries — risks biasing the recommendation toward whatever question style the generator favors, and should be validated against at least one dataset with real human queries before being trusted on an unlabeled corpus. Graph-RAG, offered as one of the candidate configurations, carries its own entity-resolution and maintenance costs; surfacing it as an option on recall numbers alone without flagging those costs would be a disservice, not a feature. And RAGRouter-Bench is still an active research effort — a classifier trained on it could ship from another team mid-build and partially obsolete this project's novelty, which is worth monitoring rather than assuming away. There's also a reflexive risk in the design itself: "one consistent metric set" could end up reproducing the exact fragmentation this project is trying to fix, if that metric set later falls out of favor and isn't kept swappable.

---

Surfaced from `research/2026-11-12-rag-techniques.md`, pattern `P2`.
