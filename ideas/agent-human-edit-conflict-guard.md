# No Clobber: Conflict-Safe Working Memory for Human+Agent Collaborative Editing

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-memory.md · P7
- **Maturity verdict**: PARTIAL — narrow implementations exist for the general concurrent-write problem but not specifically for the human-vs-agent staleness bug class: `edobusy/agenthold` (optimistic concurrency / git-like versioned shared state, agent-to-agent focused), `brainwires-agents`' `optimistic.rs` (version+hash compare-and-set), `mentedb-core`'s `ConflictResolver`. StateFuse (arXiv 2607.05844, CRDT-based conflict-aware replicated memory) and a "Governed Memory" open-problems write-up both explicitly frame concurrent write conflict detection/resolution as still unresolved. WebSearch found no result covering human-editor-vs-agent conflicts specifically — only the adjacent multi-agent case.
- **Format**: BOTH — the write-back concurrency middleware is runtime infrastructure; reviewing one product's agent-write-back flow for staleness exposure is a one-shot design-audit task.

## The Gap
GitHub PR "Events: Fix AI Publish to Use the Host's Completed Form" (amoai-tech/mdeai #491, 2026-10-22) documents and fixes a reproduced bug: "Host edits overwritten by old Mastra working memory... editing the title to 'Host corrected title' left the displayed field [stale]." The gap-analyst confirmed general-purpose optimistic-concurrency building blocks exist (agenthold, optimistic.rs, ConflictResolver) and the CRDT-based StateFuse paper addresses conflict-aware agent memory, but every one of them targets agent-to-agent or generic replicated-state conflicts — nothing targets the specific, increasingly common shape where a long-lived agent holds a cached working-memory snapshot of a document/record that a human is also editing live, and the agent's write-back silently clobbers the human's intervening edit.

## The Project
A write-back guard that sits between an agent's cached working memory and the record/document store it eventually writes to: every snapshot the agent reads carries a version stamp from the store, and before any agent write-back commits, the guard checks whether the live record's version still matches what the agent last read. If a human (or anything else) has mutated the record since, the write is held and routed through a merge/re-read/ask policy instead of committing a blind overwrite — turning a silent clobber into a detected, resolvable conflict. The centerpiece is the version-stamped read-then-guarded-write contract applied specifically at the human-edit boundary, not a general replicated-state protocol.

Components: a version-stamping wrapper around the record store's read API; a pre-commit staleness check on the agent's write path; a pluggable conflict policy (field-level merge, re-read-and-retry, hold-for-human-confirmation); an integration test harness that injects a human edit between an agent's read and write and asserts no silent clobber occurs.

## Tangible Impact
**Population**: Product teams building AI copilots that read-modify-write the same editable record a human is concurrently editing live — collaborative-doc copilots, CRM/ticketing-system AI assistants, and agent-form-filling integrations like the Mastra-based product in the source PR — a growing but currently uncounted slice of the broader agent-framework ecosystem (Mastra, LangGraph, CrewAI) wherever "agent writes back into a human-editable UI" is a feature, not a one-off script.
**Mechanism**: Today, an agent's stale working-memory snapshot writing back over a human's just-made edit is discovered only when a user notices their correction silently reverted (as in the source PR) and files a bug; a version-stamped guard makes that failure detectable before it ships to the user, converting an invisible data-loss bug into a logged, policy-resolved conflict the same way optimistic-concurrency control already does for classic multi-user database writes — just applied at the agent-memory boundary instead of the DB row boundary.
**Measure**: (1) Rate of detected read-then-stale-write attempts caught by the guard versus baseline silent-clobber incidents on a pilot integration. (2) User-visible "my edit was reverted" bug reports before vs. after adoption. (3) Added latency from the version-stamp check and conflict-policy branch on the write path.

## Why Now
Agent frameworks (Mastra, LangGraph, CrewAI) are shipping more read-modify-write integrations into live, human-editable surfaces rather than one-shot generation tasks, and the source PR shows this exact bug class reaching production and requiring an ad hoc, product-specific fix within the last 30 days — the pattern is now recurring across products faster than any one team's bespoke fix can generalize.

## Skill Angle
Given a description (or code) of an agent integration's read-modify-write flow against a human-editable record store, identify every point where the agent caches a snapshot and later writes back without re-checking the record's current state, and flag which of those are exposed to the human-edit-clobber bug class — citing the amoai-tech/mdeai #491 fix pattern as the reference shape of both the bug and its minimal remedy. Useful as a pre-ship review for any team adding an AI write-back feature to an existing collaborative surface.

## MVP Sketch
A thin version-stamping wrapper around one record store (e.g., a Postgres-backed document table), an agent SDK shim that tags every read with the stamp and refuses (or flags) a write-back whose stamp doesn't match the current record, and one conflict policy (hold-for-human-confirmation). Experiment: reproduce the amoai-tech/mdeai #491 scenario (agent reads, human edits, agent writes back) with and without the guard, and confirm the guard converts the silent clobber into a detected, non-destructive conflict. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- This may be solvable by each framework (Mastra, LangGraph) simply adopting an off-the-shelf optimistic-concurrency primitive internally, closing the gap without a standalone product — the strongest already-solvable-in-place risk.
- Field-level merge policies are themselves an imperfect judgment call; getting the default policy wrong (too aggressive holding) could make agent write-backs feel unreliable rather than safe.
- The bug class's prevalence beyond the one cited PR is unverified — this MVP's first job is confirming the pattern recurs across frameworks, not just in one Mastra-based product.
- CRDT-based approaches (StateFuse) could generalize to cover this case as a side effect of solving the broader agent-to-agent conflict problem, which would reduce this to a thin integration rather than a novel component.
