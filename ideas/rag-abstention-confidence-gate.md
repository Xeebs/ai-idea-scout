# Say I Don't Know: A Confidence-Gated Abstention Layer for RAG

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P4
- **Maturity verdict**: PARTIAL — GitHub search for "RAG abstain" turns up only narrow, unstarred repos (MrMomoLegend/rag-abstain, egbunam05/rag-abstain, gangmin-park/aviation-rag-abstain). Google Research's "sufficient context" paper (ICLR 2025, arXiv 2411.06037) proposes exactly this selective-generation intervention, but WebSearch found no accompanying open-source library — research-validated, only one-off hacks implement it.
- **Format**: BOTH

## The Gap

r/Rag's "My RAG alternative says 'not found' instead of hallucinating" (2026-11-09) stated the standard mitigation plainly fails: "similarity thresholds help, but they're brittle across queries and corpora." The poster had to build a bespoke one-off project (M.N.E.M.O.) rather than adopt an existing component. Separately, Google Research's ICLR 2025 "sufficient context" paper validates the underlying idea academically, but no open-source library implements it as a drop-in retrieval layer.

## The Project

An abstention layer that sits between retrieval and generation: a calibrated classifier judges whether the retrieved context is actually sufficient to answer the specific query (following the "sufficient context" framing rather than a raw similarity-threshold cutoff), and if not, the system returns a structured "not found" response — optionally with partial findings and a suggested next action (escalate to a human, broaden the search) — instead of forcing the LLM to generate from thin or irrelevant context. Components: a sufficiency classifier (trainable per-corpus or usable zero-shot), a structured abstain-response schema, and a calibration toolkit so operators can tune the abstain/answer tradeoff against their own eval set instead of guessing a similarity threshold.

## Tangible Impact

**Population**: End users of customer-facing RAG assistants where a confidently wrong answer causes real harm or lost trust — patients using hospital benefits/symptom-lookup chatbots, applicants using government-program eligibility assistants, students and employees using course- or policy-support tools. These deployments are expanding rapidly through 2025–2026; the dedicated ICLR 2025 paper on this exact failure mode signals it is recognized as a first-order RAG problem, not a niche edge case.
**Mechanism**: Replacing a brittle similarity threshold with a calibrated sufficiency check reduces how often users receive a fluent, confident answer built on context that doesn't actually contain the answer — converting a silent wrong-answer failure into a visible "I don't have that, here's who to ask" handoff that preserves user trust and routes them correctly.
**Measure**: abstention precision/recall against a labeled in-corpus/out-of-corpus eval set; hallucination rate on out-of-scope queries before/after deployment; user trust or task-success delta measured via pre/post pilot survey.

## Why Now

The underlying research (sufficient-context classification) is validated and current-generation models are cheap enough to run a sufficiency check per query without materially increasing latency or cost — the capability exists, only the packaged, reusable implementation is missing.

## Skill Angle

An "Abstention Policy Design" skill: given a description of a RAG pipeline and a sample of its queries/retrieved contexts, it drafts a calibrated abstention policy (what "sufficient context" means for this corpus, a starter eval set of should-abstain vs. should-answer cases, and a recommended structured fallback response) — useful for teams evaluating whether to adopt the pattern before committing to the runtime layer.

## MVP Sketch

2–4 weeks, 1–2 people: implement the sufficiency classifier as a lightweight LLM-judge call (query + retrieved passages → sufficient/insufficient + confidence), wrap it as a middleware library that intercepts the generation step, and validate on a constructed eval set of should-answer vs. should-abstain queries against a real corpus, comparing hallucination rate and abstention accuracy against a plain similarity-threshold baseline.

## Risks & Open Questions

- An LLM-judge-based sufficiency classifier adds latency and cost per query; needs to prove it beats a tuned threshold on both accuracy and cost.
- Over-abstaining is its own failure mode (a system that says "not found" too often is useless) — the eval set must capture both false-abstain and false-answer rates.
- The three existing unstarred "RAG abstain" repos may already cover part of this; worth a closer look at why none gained traction before assuming it's purely a distribution problem.
- Calibration is corpus-specific; a one-size-fits-all classifier may need per-deployment tuning, adding setup friction that could blunt adoption.
