# Write Gate: Stop a Poisoned Fact Before It Ever Reaches Memory

Every long-running agent has a soft spot nobody is guarding: the moment a fact gets written into its memory. Teams have spent the last year building increasingly careful filters for what an agent is allowed to *read back* out of memory — but almost nothing checks what goes *in*. By the time a hallucinated detail, a contradicted fact, or a poisoned instruction smuggled in via tool output gets caught, it's already been sitting in long-term storage, quietly shaping every decision downstream. One thread making the rounds in r/AI_Agents describes an automation that ran for eleven days straight before it finally failed — eleven days of accumulated bad memory before anyone noticed.

## The Gap

A June 2026 enterprise slide deck circulating via businesstechnavigator.com names "context overflow, forgotten instructions, and context poisoning" as live bottlenecks for agent deployments, with one line landing hard: "the bottleneck is no longer inference scaling... it's memory scaling." Community activity on r/AI_Agents backs this up at the ground level — the eleven-day-failure thread is exactly the shape of problem enterprises are describing from the top down.

The obvious response — buy a memory product — doesn't close this gap. Mem0, Zep, and Letta are all real, maintained, widely adopted systems with genuine provenance, partitioning, and invalidation primitives, and OWASP has now formalized "Memory & Context Poisoning" as its own category in the Top 10 for agentic apps. But every one of these, per the vendors' own documentation, operates at the *read* boundary: they filter what gets shown back to the model. None of them stop a bad write from landing in the first place. The one OSS project found aimed specifically at prevention, Agent Memory Guard, is an early-stage incubator rollback tool — not a validated mitigation anyone can point to and say "this is solved." The write boundary is still, in the vendors' own words, "coarse switches."

## The Project

Write Gate is a validation layer that sits directly in front of a memory store's write path — wrapping Mem0, Zep, or a custom vector/graph backend — and inspects every proposed write before it's allowed to commit. Three checks run on each candidate fact: does it contradict an existing high-confidence memory for the same entity or key; did it originate from untrusted tool output rather than a verified source; and does the agent's recent write volume look like a spike of accumulating noise rather than genuine new information. Anything that fails a check doesn't silently land — it gets held for review, tagged low-confidence, or rejected outright.

That write-time intervention is the whole idea. Every existing approach filters what the model is shown after a bad fact is already stored; Write Gate catches it at the moment it's proposed, before anything downstream has had the chance to build on it. The pieces: a write-interception proxy between the agent's memory calls and the backend, a contradiction checker comparing new candidates against existing memory, a provenance classifier (verified source vs. unverified tool output vs. model-generated inference), a write-rate anomaly detector tuned for long-running sessions, and a review queue for anything held.

## Tangible Impact

**Population**: Teams running long-horizon autonomous agents — multi-day unattended coding, research, or workflow-automation sessions, the kind directly referenced by the "11 days straight before failing" thread — who today have no recourse when a session degrades except killing and restarting it, losing all accumulated progress.
**Mechanism**: Today, a bad memory write (a hallucinated fact, a poisoned instruction smuggled in via tool output, or noisy accumulated tool chatter) lands in long-term memory unchecked and compounds — every later decision the agent makes can build on the corrupted fact, and the failure is only visible once the session has already gone wrong. A write-time gate catches the corrupted fact at the moment it's proposed, before anything downstream depends on it, converting a silent multi-day failure into a flagged, reviewable event.
**Measure**: (1) Session survival time (wall-clock duration before a long-running agent requires manual reset) before vs. after adoption, on a benchmark of multi-day automation tasks. (2) Precision/recall of the write gate against a labeled set of known-good vs. known-poisoned candidate writes. (3) Rate of "agent acted on a contradicted or hallucinated fact" incidents per session, before vs. after.

## Try It

There's no companion Claude Code skill for this one yet. The pre-commit write-time gate is genuinely infrastructure, not a prompt-driven task — a skill-synthesis pass turned up five or more close public equivalents for the *forensic review* angle (Agensi's "Agent Memory Audit," memory-poison-auditor, memory-audit, memory-quality-auditor, forensify, at least one with 500+ installs already), so that half of the idea is already well covered. What's still missing is the always-on write-time proxy itself, which is a build, not a prompt.

Worth being direct about the risk here too: Mem0, Zep, and Letta already own the memory layer and the integration surface, so the most likely way this gap closes is one of them shipping write-time validation directly rather than a standalone project ever needing to exist. And contradiction detection is an imperfect judgment call on its own — a changed decision isn't the same as a poisoned one, and an overly aggressive gate creates exactly the kind of friction that gets quietly loosened over time.

Surfaced from `research/2026-11-12-agentic-ai-autonomous-agents.md`, pattern `P6`.
