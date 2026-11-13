# Scenario 1: Mesh-topology investigation pipeline at 12 agents (expect HIGH RISK)

## Input

A team describes their setup:

> We built an internal investigative-research assistant using LangGraph. It currently has 12 agents: a lead researcher, 4 domain-specialist sub-researchers (finance, legal, technical, market), 3 fact-checkers, 2 writers, a critic, and a final-report synthesizer. Any agent can call any other agent directly if it needs more context — we didn't want to artificially restrict who talks to whom, so it's effectively fully connected. The task is always the same shape: gather findings across domains, cross-check them, draft a report, revise based on critique, and synthesize a final version — each step genuinely depends on the previous agent's output, it's not parallel work. We started at 6 agents a few months ago and it worked great; we've been adding specialists one at a time since, and over the last few additions the reports have started coming back with more inconsistencies and sometimes contradictory claims between sections. We're about to add 2 more regional-specialist agents and want a sanity check first.

## Expected output characteristics (pass/fail checklist)

- [ ] Correctly identifies N = 12 and topology = full mesh (explicitly stated "effectively fully connected").
- [ ] Computes edge count using N(N-1)/2 = 66 and shows this arithmetic, not just a bare number.
- [ ] Correctly identifies task type as sequential-reasoning-heavy (gather -> cross-check -> draft -> revise -> synthesize, explicitly dependent steps) — does not mis-classify this as parallelizable.
- [ ] Applies the cited study's ~10-agent / 39-70% degradation threshold directly (since task type matches the calibration scope) and flags **Risk: HIGH — at or past the measured cliff zone**, citing that 12 already exceeds the ~10-agent threshold with a near-maximal mesh edge count.
- [ ] Connects the user's own reported symptom (increasing inconsistencies/contradictions since passing ~6-8 agents) to the diagnosis as corroborating, real-world signal, without treating the symptom itself as the only evidence (the study threshold must still be the primary basis).
- [ ] Recommends a specific structural fix: converting the mesh into hierarchical sub-teams (e.g., group the 4 domain specialists under the lead researcher as one sub-team, fact-checkers as a second sub-team reporting to the critic, writers+synthesizer as a third), naming which agents move where — not a generic "add structure" statement.
- [ ] Explicitly advises against adding the 2 planned regional specialists to the existing mesh as-is, since that would push N to 14 and edges even higher before any restructuring.
- [ ] Includes the confidence/scope note citing the single 180-experiment study and noting this is an estimate, not a live measurement.
- [ ] Does not claim to have read any actual LangGraph logs/traces — treats this entirely as a description-based estimate.

## Fails if

- It applies N(N-1)/2 without showing the arithmetic, or gets the edge count wrong.
- It treats this as a "should you use multi-agent" question rather than a "where does this already-built architecture sit" question.
- It gives a generic fix ("add more structure," "consider hierarchy") without naming specific agents/groupings from the scenario.
- It fails to flag HIGH risk despite N=12 on a sequential-reasoning mesh — the single clearest case the skill should catch.
