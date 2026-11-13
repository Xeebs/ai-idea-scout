# ClaimTrace: Reviving Claim-Level Evidence Attribution for RAG

Most RAG evaluation stops at the wrong question. It asks "did we retrieve relevant material" and treats a passing score there as proof the answer is trustworthy — but a passage can be exactly on-topic and the generated sentence built from it can still misstate, over-extend, or quietly invent a detail the passage never said. That's the gap a poster on r/Rag named explicitly on 2026-11-11, framing it as two separate unsolved problems rather than citing a tool that already handles both: "Retrieval: did we retrieve relevant material... [generation] does each claim trace to a passage." The strange part is that someone already proved this exact split works at scale — and then the project went quiet for two years.

## The Gap

The r/Rag thread wasn't a rhetorical complaint; it was posed as an open question to "people experimenting with local LLM and RAG pipelines," which is itself a signal that nothing obvious was already filling the need. And the trail does lead somewhere real: amazon-science/RAGChecker, a 1,137-star repo, implements precisely this — claim-level recall against the specific retrieved chunks, reported separately from retrieval-relevance metrics. It worked, it earned adoption, and then its last commit landed on 2024-12-13, leaving it roughly two years stale. A search for a comparably-adopted successor turned up nothing but blog posts discussing the idea (Galileo, oneuptime) and a handful of small, unmaintained forks — no second project picked up where it left off. That combination is what keeps this gap at PARTIAL rather than fully closed: the concept isn't speculative, it's a validated approach with no current maintained home.

## The Project

ClaimTrace is a maintained, actively-developed claim-level evidence evaluator built on the same split RAGChecker proved out. It decomposes a generated answer into atomic claims, checks each claim's support against the specific passages that were actually retrieved for it — not the whole corpus, not a vague topical match — and reports claim-support precision and recall as a metric distinct from standard retrieval-relevance scores like recall@k. The point is to make the two failure modes visible separately: a pipeline can retrieve perfectly and still generate an answer that drifts from what the retrieved text supports, and today's tooling collapses both into one number.

Three pieces make it adoptable rather than another one-off script: a library that does the claim-extraction-and-matching work against a current LLM (rebuilding RAGChecker's core logic rather than inheriting its two-year-old dependencies), a CI integration that can fail a build when claim-support rate drops below a set threshold, and a small hosted leaderboard/benchmark so teams can compare pipelines on the same held-out eval set — the kind of shared reference point RAGChecker had the traction to build toward but never got the maintenance to sustain.

## Tangible Impact

**Population**: Engineering and compliance teams building RAG systems for regulated or high-stakes domains — clinical-decision-support tools citing medical literature, legal-research assistants citing case law, financial-advisory tools citing filings — where a single unsupported claim that merely "looks" retrieval-relevant can create real liability. Legal-tech and health-tech are among the fastest-growing RAG verticals through 2025–2026, so this subset, while smaller than the general RAG market, is the one where a per-claim audit most directly reduces downstream harm to patients, clients, and investors who act on the answers.
**Mechanism**: Decoupling claim support from retrieval relevance catches a failure mode that passage-level metrics miss entirely (a relevant passage retrieved, but the generated claim subtly misstates or extends what it says), and wiring the check into CI catches that regression before a wrong citation reaches a patient, client, or regulator rather than after.
**Measure**: claim-level support precision/recall against a held-out annotated eval set; number of unsupported claims caught in CI per month in a pilot deployment; reduction in reported "hallucinated citation" incidents after adoption.

## Try It

A companion skill exists at [`skills/rag-claim-level-evidence-auditor/`](../skills/rag-claim-level-evidence-auditor/): *"Audits a RAG (retrieval-augmented generation) answer by breaking it into atomic claims and checking each one against the exact passages that were retrieved for it — catching answers that cite a relevant-looking passage but misstate, over-extend, or fabricate what it actually says. Use when someone has a query + retrieved passages + generated answer and needs to know which specific sentences are actually backed by the evidence, not just whether retrieval looked topically relevant."*

This is the spot-check version of the project — useful on a single transcript or a sampled batch, without standing up the full CI integration or leaderboard. To use it, paste the contents of `skills/rag-claim-level-evidence-auditor/README.md` into any AI chat tool along with a query, the retrieved passages, and the generated answer you want audited, or drop the whole `skills/rag-claim-level-evidence-auditor/` folder into `~/.claude/skills/` if you're working in Claude Code.

Two things worth being honest about before building or adopting either version. First, claim extraction and matching quality depends heavily on which judge LLM does the scoring, and that needs validation that scores stay stable across model updates rather than silently drifting. Second, RAGChecker's two-year dormancy might not be pure neglect — it's worth confirming real demand with regulated-domain RAG teams directly before investing in the CI and leaderboard layers, and a hosted leaderboard in particular risks recreating the same maintenance burden that let the original project go quiet; the MVP stays a library first, leaderboard only if usage earns it.

---

Surfaced from `research/2026-11-11-rag-techniques.md`, pattern `P3`.
