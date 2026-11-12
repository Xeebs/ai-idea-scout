# Loop Guard: A Battle-Tested Control-Loop Library for Agentic RAG

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques.md · P1
- **Maturity verdict**: PARTIAL — `gh search repos "agentic RAG framework"` returned dozens of repos (DualStack-Agent, Corax-RAG-Agent, artoo, Crux, RAGents, rag-engine, py-jrag, etc.) but nearly all are single-author, narrow-scope, or thesis/hobby projects with no evidence of broad adoption. WebSearch found one packaged PyPI library (`retrievalagent`, built on LangGraph, with retry/evaluate/rewrite loop and max-iteration cap) and one research method (Stop-RAG, arXiv, learns when to stop retrieving) — both real but neither is an established, widely-adopted standard. No consensus shared library for the control loop (retry/stopping/malformed-tool-call handling) was found; the gap is real but partially addressed by narrow/unevaluated implementations.
- **Format**: BOTH

## The Gap

The "You Might Not Need RAG" blog post describes its author hand-rolling a retrieval loop — plan query, retrieve, critique, re-query — and only later discovering it already had a name ("agentic retrieval"). Vectorize's practitioner post on finally getting agentic RAG to work right separately documents fighting invalid JSON returned mid-loop. Both are solo narrative write-ups of custom plumbing, not references to a shared library, and gap-analyst confirmed the handful of GitHub frameworks that exist are narrow hobby projects, not a maintained standard anyone converges on.

## The Project

A small, dependency-light control-loop library that any RAG stack can drop a retrieval-generation call into: it owns the retry policy, a calibrated stopping criterion (so the loop doesn't retrieve forever or quit too early), and defensive parsing/repair for malformed tool-call JSON from the underlying model, with structured logging of why each loop exited (answered / max-iterations / low-marginal-gain / parse-failure-exhausted). It is explicitly scoped to the hundreds-to-low-thousands-of-document regime the source blog post names — not a claim to replace million-document retrieval infra — and ships framework adapters (plain function calls, LangGraph, LlamaIndex) rather than its own orchestration framework, so teams can adopt the loop without migrating their whole stack.

## Tangible Impact

**Population**: Solo developers and small teams (1–5 engineers) building internal or early-stage retrieval-augmented tools without a dedicated ML/platform engineer — the same profile as the two source-post authors, who both discovered mid-build that their hand-rolled loop was reinventing a known pattern badly. GitHub search suggests dozens of comparable one-off repos exist, each paying this tax independently.
**Mechanism**: Replacing a bespoke, untested retry/stop loop with a reviewed, tested library removes the two failure classes both source posts hit firsthand (infinite/premature stopping, unhandled malformed JSON) before they ship to users, cutting the debugging cycle those authors each described going through alone.
**Measure**: crash/hang rate from malformed tool-call responses before vs. after adoption on a replayed trace set; time-to-working-loop for a new integration (target: hours, not the multi-week trial-and-error both source posts describe); loop-exit-reason distribution on real traffic, which the two source projects had no visibility into at all.

## Why Now

Agentic RAG usage is rising fast enough that two independent practitioners hit and wrote up the same plumbing problem within the same research window, but tool-calling reliability from underlying models is still inconsistent enough (malformed JSON, early/late stopping) that the control-loop logic is genuinely worth factoring out now rather than waiting for model-side fixes that may not land uniformly across providers.

## Skill Angle

An "Agentic RAG Loop Audit" skill: given a pasted snippet or description of a team's existing hand-rolled retrieval loop, it reviews for the three failure modes named in the source evidence (missing retry cap, no calibrated stopping criterion, unhandled malformed tool-call JSON), and drafts the specific fix for each — useful standalone for teams who don't want to adopt the full library but want their existing loop reviewed against known failure patterns.

## MVP Sketch

2–4 weeks, 1–2 people: implement the core loop (retrieve → critique → re-query → stop) as a plain Python generator with pluggable retry/stop/repair policies, write adapters for raw function-calling and one framework (LangGraph), and validate against a reproduction of both source posts' failure cases (inject malformed JSON mid-loop; run on a corpus sized per the "hundreds-to-low-thousands" regime) to confirm the loop degrades gracefully instead of hanging or looping forever.

## Risks & Open Questions

- `retrievalagent` (PyPI) already does roughly this on LangGraph — the real gap may be adoption/awareness and framework-agnosticism, not a missing capability, which narrows this project's differentiation to "the one that isn't locked to LangGraph."
- A generic control loop risks being too thin to be worth adopting versus teams just copying a gist; the library needs genuinely hard-won defaults (calibrated stopping, JSON repair heuristics) to earn its keep.
- Scope creep toward "general agent orchestration framework" would compete directly with LangGraph/LlamaIndex rather than complementing them — must stay narrowly focused on the retrieval control loop only.
- Evidence base is two blog posts; worth a quick practitioner-forum check before building to confirm this isn't already solved by a tool the search missed.
