# Canary Suite: A Unified Abstention-and-Hallucination Eval Harness for RAG

- **Status**: EXPLORING (promoted 2026-11-20 cycle 286: evidence density — ≥2 independent threads)
- **Date**: 2026-11-20
- **Topic**: RAG techniques
- **Source**: research/2026-11-20-rag-techniques.md · P8
- **Maturity verdict**: PARTIAL — WebSearch found several academic-only point solutions: LIT-RAGBench (arXiv 2603.06198, has an explicit Abstention category, code released but turnkey-ness unconfirmed), Secure-RAG (non-peer-reviewed preprint proposing a unified suite), FATHOMS-RAG (arXiv 2510.08945, multimodal pipeline benchmark). Established eval libraries (RAGAS, DeepEval, TruLens) are widely adopted but, per Secure-RAG's own framing, require manual assembly to cover abstention — no single mature, turnkey harness unifies abstention + hallucination scoring, confirming the gap is real.
- **Format**: BOTH
- **Data Sources**: MANUAL — the team uploads/pastes their RAG pipeline's own eval set: query + retrieved-context + generated-response triples, plus a labeled set of out-of-scope "canary" questions (queries with no correct answer in the corpus) the pipeline should refuse rather than guess on. A fast-follow CONNECTED upgrade pulling these triples directly from a trace export (LangSmith or Langfuse, both mature observability platforms) is a natural next step once the manual version is validated (see Risks).

## The Gap

Many academic hallucination-detection benchmarks and leaderboards already exist (RAGTruth, RAGBench, BERGEN, Vectara's faithfulness leaderboard), plus a preprint (arXiv 2608.26385) arguing binary-graded benchmarks "reward guessing over abstaining" and proposing penalty-aware scoring with "knowledge-gap canary" questions. But the digest's own search "did not surface a single turnkey harness that covers all of these at once" — multiple point solutions exist, but nothing unified and widely adopted, and the abstention half specifically has no turnkey coverage.

## The Project

A harness that takes a team's own pipeline eval set plus a labeled canary set and produces one combined report: hallucination rate on answerable questions (via an established point metric, not reinvented) and abstention precision/recall on the canary set (the specific category the digest's search found no turnkey tool covers) — instead of a team manually wiring together 2–3 separate academic benchmarks and still missing the abstention half. Components: a pluggable metric adapter (wraps an existing faithfulness scorer), a canary-question runner, and a single combined scorecard.

## Tangible Impact

**Population**: RAG engineering teams (1–10 people) preparing to ship a support/QA or internal-knowledge assistant into production who need to validate it won't confidently guess on out-of-scope questions before launch — the same profile raising "why is there no abstention benchmark" on HuggingFace/OpenAI community forums; a population in the thousands given how many internal RAG assistants reached production in 2025–2026.
**Mechanism**: Running real query/response pairs plus a labeled canary set through one unified harness, instead of manually assembling 2–3 separate academic benchmarks and still missing abstention coverage, closes the exact "no single turnkey harness" gap the digest's search confirmed empty — giving teams one pre-launch signal instead of a false sense of coverage from hallucination-only tools.
**Measure**: abstention precision/recall on the canary set (how often the pipeline correctly says "not found" vs. guesses); hallucination rate on answerable questions, using an established point metric; time for a team to run a full pre-launch eval (target: hours via one harness invocation vs. the multi-tool manual assembly Secure-RAG's own framing describes).

## Why Now

Enough fragmented point solutions now exist (RAGTruth, RAGBench, BERGEN, Vectara's leaderboard, LIT-RAGBench's abstention category) that unifying them is an integration problem, not a research problem — and the "reward guessing over abstaining" critique (arXiv 2608.26385) landed recently enough that no one has yet packaged its penalty-aware scoring into a turnkey tool teams can run before a launch.

## Skill Angle

A "Pre-Launch Abstention Audit" skill: given a handful of a team's own query/response pairs and canary questions pasted in, reviews them for guessing-vs-abstaining failures and flags specific wrong-guess patterns worth testing at scale before running the full harness — a quick, no-infra sanity check on the project's core question.

## MVP Sketch

2–4 weeks, 1–2 people: wire together one existing hallucination metric (e.g., a RAGAS faithfulness check) with a canary-question abstention scorer (correct-refusal rate against a hand-built canary set), producing one combined report. Validate against LIT-RAGBench's published abstention category results to confirm the harness's abstention scoring matches that benchmark's established numbers before trusting it on a team's own unlabeled pipeline.

## Risks & Open Questions

- LIT-RAGBench's code is already released; this project's differentiation is turnkey unification plus a team's-own-data workflow, not the underlying metric — narrows if LIT-RAGBench gets wrapped into a CLI first.
- Canary-question quality determines everything; a weak or too-easy canary set could make a pipeline look abstention-safe when it isn't.
- Combining metrics from different papers into "one report" risks reproducing the same fragmentation (whose faithfulness definition wins) that already plagues RAGAS/DeepEval/TruLens per the digest's cited survey.
- The MANUAL-only MVP is a weaker product than a CONNECTED version pulling traces directly from LangSmith/Langfuse — worth scoping that upgrade as a fast-follow rather than a day-one requirement.
