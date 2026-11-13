# Fault Line: An Automated Retrieval/Chunking/Generation Failure Classifier for RAG

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: RAG techniques
- **Source**: research/2026-11-13-rag-techniques.md · P2
- **Maturity verdict**: OPEN — genuine multi-channel search found only diagnostic *methods*, not a shipped automated classifier: the manual "known-good context" test, RAGChecker's claim-level analysis (which splits retrieval from generation but has no chunking category and has been stale since 2024-12), and a TU Delft academic failure taxonomy (paper, not tooling). A LangChain forum thread ("When is it actually a failure? Diagnosing agent behavior beyond LangGraph traces") explicitly states that tools which detect post-retrieval failures can't trace them back to the specific insufficient chunk and calls that runtime attribution layer missing. No source names a shipped tool automating the 3-way (retrieval/chunking/generation) classification.
- **Format**: BOTH
- **Data Sources**: CONNECTED — pulls the failed interaction's full trace (query, retrieved chunk IDs + text + source document span, final generated answer) from the team's existing LLM observability platform via its trace-export API — LangSmith and Langfuse both ship mature, documented trace-export APIs today. MANUAL fallback for teams on a custom stack: paste the (query, retrieved chunks with document+offset metadata, generated answer) triple directly. The Skill Angle variant is MANUAL only — a single pasted trace, no connector needed for a one-off classification.

## The Gap

Multiple 2026 production-RAG postmortems surfaced via WebSearch ("Production RAG Systems — 7 Lessons We Learned the Hard Way" and a RAG-evaluation framework guide) converge on the same advice: attribute every wrong answer to retrieval, chunking, or generation before trying to fix it, because teams "lacking an evaluation framework often don't know their system is broken." Every source describes this as manual triage practice an engineer performs by eyeballing the trace — none names a tool that does the classification automatically, and the closest existing tool (RAGChecker) explicitly has no chunking category and has sat unmaintained for two years.

## The Project

A classifier that takes one failed RAG interaction (query, the retrieved chunks with their source-document spans, and the generated answer) and outputs a specific verdict with evidence: **retrieval failure** (the right passage was never fetched — checked by re-running retrieval with a known-good query reformulation or against a labeled gold passage), **chunking failure** (the right document was fetched but the chunk boundary split the answer-bearing sentence or table row away from its context — checked by looking at adjacent chunks and the original document span), or **generation failure** (sufficient, correctly-chunked context was retrieved but the model still answered wrong or unsupported — checked via claim-level support scoring against exactly the retrieved passages). Ships as a CLI/library that ingests traces from LangSmith or Langfuse export, plus a dashboard that aggregates verdicts across a batch of failures so a team sees "62% of your failures this week are chunking, not retrieval" instead of guessing per-incident.

## Tangible Impact

**Population**: Engineering teams running production RAG systems who currently triage failures by hand — the same audience the cited "lessons learned" posts and LangChain forum thread describe directly. RAG is now a standard component of customer support, internal knowledge, and developer-tooling products, so this spans any team past the prototype stage with a live failure backlog, not a narrow vertical.
**Mechanism**: Today a team sees a wrong answer and has to manually decide whether to re-tune the retriever, re-chunk the corpus, or re-prompt the generator — each a different, expensive fix with no signal about which one is actually broken. An automated per-failure verdict with evidence turns that guess into a routed ticket, so engineering time goes to the actual broken stage instead of being spread across all three on a hunch.
**Measure**: agreement rate between the classifier's verdict and a human engineer's independent manual triage on a held-out failure set (precision/recall per failure class); median time from "user reports a bad answer" to "root-cause stage identified," before vs. after adoption; percentage of fixes that target the correctly-identified stage on the first attempt.

## Why Now

Claim-level support scoring and "sufficient context" classification are now both validated, cheap-to-run LLM-judge techniques (used independently in RAGChecker and Google Research's ICLR 2025 sufficient-context paper), and LangSmith/Langfuse's trace-export APIs matured enough in 2025–2026 to make pulling a structured failure trace trivial — the individual primitives this classifier composes all exist; no one has wired them together into a single attribution verdict.

## Skill Angle

A "Diagnose This RAG Failure" skill: hand it one pasted trace (query, retrieved chunks with their document context, generated answer, and optionally what the correct answer should have been) and it returns the retrieval/chunking/generation verdict with its supporting evidence and a one-line recommended next step — useful for a quick single-incident triage without wiring up the full observability-platform integration the project's continuous monitoring version requires.

## MVP Sketch

2–4 weeks, 1–2 people: build the three per-stage checks (retrieval re-run against a gold-passage set, adjacent-chunk boundary inspection, claim-support scoring) as independent functions, combine them into a single verdict-with-evidence function, wrap it as a CLI accepting a LangSmith/Langfuse trace export or a manually pasted JSON triple, and validate against a constructed set of known-cause synthetic failures (deliberately broken retrieval, deliberately bad chunk boundaries, deliberately unsupported generation) to confirm the classifier correctly attributes each.

## Risks & Open Questions

- Real failures are often multi-cause (a mediocre retrieval result compounded by a bad chunk boundary) — the classifier needs a defensible way to report mixed/ambiguous verdicts rather than forcing one label.
- Claim-support scoring and sufficiency classification are themselves imperfect LLM-judge calls; the attribution tool inherits their error rate and needs its own accuracy ceiling established against human-labeled ground truth.
- The two existing diagnostic approaches (RAGChecker, the TU Delft taxonomy) might not have been packaged into a tool because demand is thinner than the blog-post advice suggests — worth validating with a few target teams before building the full dashboard.
- Depends on trace-export APIs exposing chunk-level metadata (document span, boundaries) consistently; teams on bespoke logging without that metadata will be stuck on the manual-paste path only.
