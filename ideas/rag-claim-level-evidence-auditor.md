# ClaimTrace: Reviving Claim-Level Evidence Attribution for RAG

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P3
- **Maturity verdict**: PARTIAL — amazon-science/RAGChecker (1,137 stars) implements exactly this claim-level-vs-retrieval split, but last pushed 2024-12-13 (~2 years stale) with no second comparably-adopted implementation found via WebSearch (only blog discussion and small unmaintained forks).
- **Format**: BOTH

## The Gap

r/Rag's "Does RAG retrieval quality tell us anything about claim-level evidence support?" (2026-11-11) framed the problem explicitly: "Retrieval: did we retrieve relevant material... [generation] does each claim trace to a passage" — posed as an open question to the local-LLM/RAG community, not a reference to an existing standard. RAGChecker proved the idea works at scale and earned real traction, but it has been dormant for two years with no actively maintained successor.

## The Project

A maintained, actively-developed claim-level evidence evaluator: decompose a generated answer into atomic claims, check each claim's support against the specific retrieved passages (not the whole corpus), and report claim-support precision/recall separately from standard retrieval-relevance metrics (e.g., recall@k). Ship it as a library with CI integration (fail a build if claim-support rate drops below threshold) and a small hosted leaderboard/benchmark so teams can compare pipelines on the same held-out eval set, picking up where RAGChecker's momentum stalled.

## Tangible Impact

**Population**: Engineering and compliance teams building RAG systems for regulated or high-stakes domains — clinical-decision-support tools citing medical literature, legal-research assistants citing case law, financial-advisory tools citing filings — where a single unsupported claim that merely "looks" retrieval-relevant can create real liability. Legal-tech and health-tech are among the fastest-growing RAG verticals through 2025–2026, so this subset, while smaller than the general RAG market, is the one where a per-claim audit most directly reduces downstream harm to patients, clients, and investors who act on the answers.
**Mechanism**: Decoupling claim support from retrieval relevance catches a failure mode that passage-level metrics miss entirely (a relevant passage retrieved, but the generated claim subtly misstates or extends what it says), and wiring the check into CI catches that regression before a wrong citation reaches a patient, client, or regulator rather than after.
**Measure**: claim-level support precision/recall against a held-out annotated eval set; number of unsupported claims caught in CI per month in a pilot deployment; reduction in reported "hallucinated citation" incidents after adoption.

## Why Now

RAGChecker proved demand and feasibility two years ago and has been abandoned since, leaving a validated approach with no current maintained home — exactly the de-risked-but-unexecuted gap the pipeline looks for, and regulated-domain RAG adoption has grown enough since then that the audience for this is larger than when RAGChecker launched.

## Skill Angle

A "Claim Audit" skill: hand it a transcript (query, retrieved passages, generated answer) and it scores each atomic claim against the specific passages that were retrieved, flagging unsupported or over-extended claims — usable as a one-off spot-check on a single answer or a sampled set, without requiring the CI integration the full project builds.

## MVP Sketch

2–4 weeks, 1–2 people: fork/rebuild the core RAGChecker claim-extraction-and-matching logic against a current LLM, wrap it as a CLI that takes (query, passages, answer) triples and outputs per-claim scores, and validate against RAGChecker's own published eval set to confirm parity before adding CI hooks or a leaderboard.

## Risks & Open Questions

- Claim extraction and matching quality depends heavily on the judge LLM used; needs validation that scores are stable across model updates.
- RAGChecker's two-year dormancy might reflect weak demand rather than just neglect — worth confirming via direct outreach to regulated-domain RAG teams before building.
- A hosted leaderboard invites the same maintenance burden that killed the original project; the MVP should stay a library first, leaderboard only if usage justifies it.
- LLM-as-judge claim scoring is itself imperfect and needs its own accuracy ceiling established against human-annotated ground truth.
