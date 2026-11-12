# Write Gate: A Pre-Commit Validation Firewall for Agent Memory

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-12-agentic-ai-autonomous-agents.md · P6
- **Maturity verdict**: PARTIAL — Mem0, Zep, and Letta are maintained, adopted products providing provenance/partitioning/invalidation primitives, and OWASP added "Memory & Context Poisoning" as its own Top-10-for-agentic-apps category in Dec 2025, but per Zep's and third-party write-ups these only cover the read/filter boundary; the write boundary (stopping a bad write before it lands) has only "coarse switches." The one named prevention-focused OSS project, Agent Memory Guard, is an early incubator rollback tool, not a validated mitigation.
- **Format**: BOTH — the always-on interception middleware is runtime infrastructure; auditing one flagged write or one suspicious long-running session for poisoning is a separable one-shot task.

## The Gap
A June 2026 enterprise slide deck (via businesstechnavigator.com) names "context overflow, forgotten instructions, and context poisoning" as live bottlenecks, quoting a claim that "the bottleneck is no longer inference scaling... it's memory scaling," and a WebSearch roundup of r/AI_Agents activity cites a thread about "an automation that ran for 11 days straight before failing" from accumulated bad memory. The gap-analyst confirmed existing memory products (Mem0, Zep, Letta) filter what gets *read back* into context, and OWASP now names the risk category explicitly, but nothing evaluated stops a corrupted or noisy fact from being *written* into long-term memory in the first place — the write boundary is still "coarse switches" per the vendors' own documentation.

## The Project
A validation layer that sits in front of a memory store's write path — wrapping Mem0, Zep, or a custom vector/graph backend — and checks every proposed write before it commits: does this fact contradict an existing high-confidence memory, does it originate from untrusted tool output rather than a verified source, and has the agent's recent write volume spiked in a way that looks like noise accumulation rather than genuine new information? Writes that fail a check are held for review, tagged low-confidence, or rejected outright, rather than silently landing and later poisoning retrieval. The write-time gate is the centerpiece — distinct from every existing approach, which only filters what's shown back to the model after the damage is already stored.

Components: a write-interception proxy (sits between the agent's memory-write calls and the backend); a contradiction checker (compares a new candidate fact against existing memory for the same entity/key); a provenance classifier (verified source vs. unverified tool output vs. model-generated inference); a write-rate anomaly detector tuned to long-running sessions; a review queue for held writes.

## Tangible Impact
**Population**: Teams running long-horizon autonomous agents — multi-day unattended coding, research, or workflow-automation sessions, the kind directly referenced by the "11 days straight before failing" thread — who today have no recourse when a session degrades except killing and restarting it, losing all accumulated progress.
**Mechanism**: Today, a bad memory write (a hallucinated fact, a poisoned instruction smuggled in via tool output, or noisy accumulated tool chatter) lands in long-term memory unchecked and compounds — every later decision the agent makes can build on the corrupted fact, and the failure is only visible once the session has already gone wrong. A write-time gate catches the corrupted fact at the moment it's proposed, before anything downstream depends on it, converting a silent multi-day failure into a flagged, reviewable event.
**Measure**: (1) Session survival time (wall-clock duration before a long-running agent requires manual reset) before vs. after adoption, on a benchmark of multi-day automation tasks. (2) Precision/recall of the write gate against a labeled set of known-good vs. known-poisoned candidate writes. (3) Rate of "agent acted on a contradicted or hallucinated fact" incidents per session, before vs. after.

## Why Now
Enterprises are now running agents in sessions measured in days rather than single conversations, and both an internal enterprise data source and a fresh OWASP Top-10 category confirm context/memory poisoning is treated as the live failure mode for exactly this class of session — while every shipped mitigation still only polices what memory shows the model, not what gets written into it.

## Skill Angle
Given a session's memory-write log (a sequence of facts an agent committed to long-term memory) and the session's task, review it for poisoning signals: contradictions between entries, facts sourced from untrusted tool output being treated as ground truth, and anomalous write-volume spikes. Flag specific entries that should be rolled back and explain why. This is useful today as a forensic review for any team debugging a degraded long-running session, independent of adopting the always-on gate.

## MVP Sketch
A lightweight proxy in front of one memory backend (Mem0) that intercepts writes, runs a contradiction check (embedding similarity + a cheap-model comparison against the existing entry for the same key) and a provenance tag (verified source vs. raw tool output), and holds anything failing either check in a review queue instead of committing it. Experiment: run a multi-day automation task (e.g., a research agent doing iterative literature synthesis over several days) with and without the gate, and compare how many corrupted facts make it into final memory and how long each session survives before manual intervention is needed. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- Mem0, Zep, or Letta could ship a write-time validation feature directly, which is the most direct competitive risk given they already own the memory layer and the integration surface.
- Contradiction detection is itself an imperfect judgment call — overly aggressive gating could block legitimate factual updates (a changed decision isn't the same as a poisoned one), creating friction that pushes teams to loosen the gate over time.
- The anomaly detector needs a baseline for "normal" write volume per task type, which may not generalize across very different agent workloads without per-deployment tuning.
- It's unclear from the digest evidence whether session failures are actually caused by write-time poisoning specifically, versus other long-horizon failure modes (tool flakiness, drift in the base model's behavior) — the MVP experiment is partly testing that attribution.
