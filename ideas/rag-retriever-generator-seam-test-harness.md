# Seam Test: An Integration-Test Harness for the Retriever/Generator Handoff in RAG

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: RAG techniques
- **Source**: research/2026-11-18-rag-techniques.md · P5
- **Maturity verdict**: PARTIAL — `gh search repos` for "retriever generator integration test," "RAG seam test," and "agent testing framework tool call" all returned zero results. Only a single blog post (tianpan.co, "Testing the Retrieval-Generation Seam") names the concept, and general frameworks (DeepEval, Ragas, LangSmith) can be repurposed but have no seam-specific failure-mode feature — DeepEval's own docs warn that feeding it ideal `retrieval_context` just measures the generator in isolation. Kept at PARTIAL (not OPEN) per the tie-break rule since generic eval tooling provides partial building blocks.
- **Format**: BOTH
- **Data Sources**: MANUAL — the team provides a small curated set of fixture documents (including deliberately borderline-relevant/noisy chunks) and wires their actual retriever and generator functions into the harness via a thin adapter interface; there is no external system to connect to since the whole point is testing the team's own pipeline code against controlled inputs.

## The Gap
A direct, first-person Hacker News question — "How to control unit tests in Agentic Pipelines" — got one comment and no resolution. Two independent practitioner write-ups (Netguru, tianpan.co) independently diagnose the same structural hole from the field: teams unit-test the retriever and the generator separately, but the handoff between them — does the generator actually use the retrieved chunk correctly, does a borderline-relevant chunk silently poison the output — has no standard test layer, so seam failures slip through green CI. LangWatch's own "Agent Testing Pyramid" still treats this as a conceptual layer, not a shipped tool.

## The Project
A test harness, usable as a library inside existing test runners (pytest, Jest), purpose-built for seam-level assertions that component-level unit tests structurally can't express: feed the generator a mix of relevant, borderline, and irrelevant chunks and assert the answer correctly ignores the noise; feed the retriever's actual top-k output (not an idealized `retrieval_context`) into the generator and assert faithfulness holds; inject a chunk that contradicts another retrieved chunk and assert the generator flags the conflict instead of silently picking one. The core novelty is treating the seam itself as the unit under test — a named, independently-failing assertion class, separate from "does retrieval score well" and "does generation score well" in isolation.

Key components: a fixture-corpus format for seam-test cases (clean/noisy/conflicting chunk sets), a thin adapter interface for wiring in any retriever/generator pair, a library of seam-specific assertion helpers, and CI-runner integration so a seam regression blocks a PR the same way a unit-test failure would.

## Tangible Impact
**Population**: small-to-mid engineering teams (the same practitioner population posting the HN question and the two blog write-ups) shipping a RAG pipeline with component-level test coverage but no integration-layer coverage — teams past the prototype stage who already have CI but keep shipping seam-level regressions that neither their retriever tests nor their generator tests catch.
**Mechanism**: gives these teams a concrete, named failure-mode class to write tests against (noise poisoning, chunk-misuse, contradiction-blindness) instead of relying on ad hoc mocking (the HatchWorks-recommended stopgap) or hoping end-to-end evals happen to catch it; a seam regression that would previously only surface as a confusing production answer quality drop instead fails a specific, debuggable CI assertion.
**Measure**: number of seam-class regressions caught in CI vs. in production after adoption; time-to-diagnose a seam failure (should drop sharply once the failing assertion names the mechanism, vs. starting from "the answer looked wrong"); percentage of a team's RAG pipeline test suite that is seam-level vs. component-level after adoption (a proxy for real uptake, not just installation).

## Why Now
The gap is freshly and independently diagnosed twice in the last 30 days (the HN question, the tianpan.co post) with no resolution in either — this is live, unmet demand, not old news. Current LLM-as-judge and deterministic-check tooling (the building blocks DeepEval/Ragas already ship) are mature enough to compose into seam-specific assertions without inventing new eval technology; the gap is the missing seam-specific framing and fixture format, not a missing capability.

## Skill Angle
A review skill: given a description of a RAG pipeline's retriever and generator components (pasted code or an architecture summary), identify the specific seam failure modes most likely to bite this pipeline (e.g., no handling for contradicting chunks, no defense against borderline-relevant noise) and draft the corresponding seam-test cases — a one-shot architecture-review task distinct from the project's ongoing CI infrastructure.

## MVP Sketch
Scope: the fixture format, adapter interface, and three seam-assertion helpers (noise-resistance, faithfulness-to-actual-retrieval, contradiction-detection) for a Python/pytest stack. Stack: pytest plugin architecture, an LLM-as-judge call for the faithfulness/contradiction assertions, a small CLI to scaffold fixture corpora. The validating experiment: take one open-source RAG pipeline with existing component-level tests, deliberately introduce a seam-class bug (e.g., swap in a generator that ignores a contradicting chunk), and confirm the existing component tests pass while the new seam test correctly fails.

## Risks & Open Questions
- LLM-as-judge-based seam assertions inherit judge-bias and flakiness risk — the harness needs a calibration step (per this repo's own `tiered-judge-calibration-pipeline` idea) rather than trusting a single judge call, or it will itself become an unreliable gate.
- Teams may resist adding a third test layer on top of already-maintained component and end-to-end suites; the MVP experiment should also measure setup friction, not just detection capability.
- If a mainstream framework (DeepEval, Ragas) ships a native seam-assertion feature first, this narrows fast to a thin wrapper — worth watching their release notes.
- The fixture-corpus curation (crafting genuinely borderline/conflicting chunks) is itself a skill; a poorly-curated fixture set could produce false confidence as easily as no test at all.
