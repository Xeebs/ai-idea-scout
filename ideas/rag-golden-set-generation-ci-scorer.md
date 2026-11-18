# Golden Start: An LLM-Assisted Golden-Set Generator and CI Scorer for RAG Pipelines

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: RAG techniques
- **Source**: research/2026-11-18-rag-techniques.md · P3
- **Maturity verdict**: PARTIAL — `gh search repos` for "RAG golden set evaluation" and "RAG evaluation framework" turned up a dozen-plus 2026-dated repos (`2501Pr0ject/RAGnarok-AI`, `feleir/evalkit`, `ramirez-ai-labs/rag-evaluation-lab`, `gomate-community/BenchRAG`, `mlloliveira/EdgeRAG`) plus two fresh Show HN launches (`infrixo-systems/rag-evaluation-starter`, a Trendshift-listed lightweight evaluator) — a thick, unconsolidated landscape of narrow scorers, with mainstream RAGAS/TruLens/DeepEval maintained but not closing this specific niche.
- **Format**: PROJECT (skill-synthesizer NOVELTY_FAIL, cycle 154: 4+ close, well-adopted equivalents at the Skill Angle's exact scope — `unshDee/proofrag` Claude Code skill, `glebis/claude-skills` "rag-eval" skill, RAGAS `TestsetGenerator`, DeepEval `Synthesizer` — all already draft golden QA+context sets from a document corpus)
- **Data Sources**: MANUAL — the user points the tool at their own document corpus sample (a folder or set of files already used by their RAG pipeline) and provides their retriever/generator call as a thin adapter function; the tool itself generates the golden set from that corpus rather than requiring the user to hand-write QA pairs.

## The Gap
Two independent Show HN launches attacked the identical narrow problem — scoring a RAG pipeline against a golden set of question/answer/supporting-passage triples — within about two weeks of each other, each a single-digit-point post rather than a converged tool. `gh search repos` confirms over a dozen more 2026-dated repos doing roughly the same scoring logic solo. Every one of these tools assumes a golden set already exists; none addresses the actual bottleneck practitioners keep re-deriving from scratch — building and maintaining that golden set in the first place, which is why so many teams never adopt one at all and ship without regression coverage.

## The Project
A CI-integrated tool with two halves that no single existing repo combines: (1) a golden-set generator that samples a team's real corpus, uses an LLM to draft candidate question/answer/supporting-passage triples stratified across document types and difficulty, and routes them through a lightweight human-review queue (accept/edit/reject) instead of requiring an engineer to author every case by hand; (2) a packaged, zero-config scorer — retrieval recall, faithfulness, answer relevance, and a per-stage retrieval-vs-chunking-vs-generation breakdown, run against that golden set in CI on every pipeline-touching PR with a pass/fail gate.

The generator is the centerpiece, not an add-on: it's the piece every one of the dozen existing repos skips, and it's specifically why teams keep rewriting the scoring half from scratch instead of adopting one of the existing options — there's nothing to score against until the set exists.

## Tangible Impact
**Population**: small-to-mid engineering teams (roughly 2-20 engineers) building and maintaining a production RAG pipeline who currently ship without a regression-test layer — the same audience posting the Show HN launches and populating the dozen narrow GitHub repos found in gap analysis.
**Mechanism**: cuts the time-to-first-golden-set from a multi-day manual authoring task to an afternoon of reviewing LLM-drafted candidates, which removes the single biggest reason teams skip regression testing for RAG changes; once a golden set exists, the packaged CI gate catches retrieval/chunking regressions before merge instead of after a user notices a degraded answer.
**Measure**: time from "no golden set" to "first CI-gated regression run" (target: under a day vs. the multi-day-to-never baseline implied by current adoption); number of regressions caught pre-merge vs. post-merge in the weeks after adoption; human-review acceptance rate of LLM-drafted candidates (a proxy for whether the generator is actually saving curation time).

## Why Now
Two independent Show HN launches in the last 30 days confirm builders are actively shipping stopgaps right now, not just complaining in blog posts — the demand is live and unresolved. Current frontier models are now reliably good at drafting plausible QA-pairs-with-supporting-passages from a document sample, which is the capability that makes the generation half newly tractable; this wasn't a credible approach even a year ago when models hallucinated supporting-passage citations too often to trust a lightweight human-review pass.

## MVP Sketch
Scope: generator + scorer for one corpus format (plain text/markdown docs) and one pipeline adapter interface (a Python function taking a query, returning retrieved chunks and a generated answer). Stack: an LLM call for candidate generation, a small review CLI/web form, pytest-based scoring assertions, a GitHub Action wrapping it. The validating experiment: run the generator against a real internal doc set, measure human-reviewer acceptance rate on the first batch of drafted candidates, and confirm the resulting golden set actually catches a deliberately-introduced chunking regression in CI.

## Risks & Open Questions
- With a dozen-plus competing narrow tools already live, differentiation has to be real and visible from the first release, not just "same thing, better docs" — the generator half is the bet that carries this.
- LLM-drafted candidates could systematically miss the hardest real-world query types (multi-hop, ambiguous, adversarial) that actually matter for regression coverage; the human-review step needs to catch this, not rubber-stamp it.
- If a mainstream framework (RAGAS, DeepEval) ships its own golden-set generator first, this project loses its differentiator fast — worth checking their roadmaps before building.
- Adapter-interface friction (getting a team's real pipeline wired into the scorer) is often the actual reason teams abandon eval tools; the MVP experiment should test this friction directly, not just the generation quality.
