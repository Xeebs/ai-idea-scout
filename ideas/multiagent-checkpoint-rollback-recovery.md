# Last Good State: Checkpoint-and-Rollback Recovery for Mid-Run Multi-Agent Failures

- **Status**: EXPLORING
- **Date**: 2026-11-14
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-14-multi-agent-architectures.md · P2
- **Maturity verdict**: PARTIAL — LangGraph, CrewAI, and Google ADK already ship checkpointing primitives (confirmed via `gh search repos "langgraph checkpoint"` — multiple maintained checkpoint-saver backends: MySQL, DynamoDB, Firestore), and academic work (COCO, arXiv 2508.13815; a NeurIPS 2026 reliability/fallback-patterns paper) targets rollback directly. But a Feb 2026 Diagrid engineering post explicitly argues "checkpoints are not durable execution — why LangGraph, CrewAI, Google ADK and others fall short for production agent workflows," noting no built-in fallback routing or dead-letter queue. Practitioners (a Latenode community thread) are still hand-rolling true rollback-to-last-consistent-state logic themselves.
- **Format**: BOTH — the durable rollback/dead-letter runtime is PROJECT-shaped infrastructure; reviewing an existing pipeline design for which steps need checkpointing and flagging non-idempotent side effects is a separable one-shot design task.
- **Data Sources**: CONNECTED (project) — reads and writes checkpoint state through the team's existing orchestration framework's checkpointer (LangGraph's checkpoint-saver API, or a generic key-value store for frameworks without one); this primitive already exists maturely, and this project adds the fallback-routing/dead-letter layer the Diagrid critique says is missing on top of it, rather than re-deriving checkpointing from scratch. MANUAL (skill) — user pastes a description of their pipeline's steps and which ones have side effects (DB writes, emails, payments, external API calls).

## The Gap
A Latenode community builder describes a three-agent customer-analysis pipeline: "If agent two fails partway through processing agent one's output, you're left in an inconsistent state. Recovery logic is complex." Another practitioner in the same thread describes checkpointing shared state after each step and manually rolling back to the last checkpoint as their workaround — hand-rolled, not a framework feature. The Diagrid post independently confirms the gap from the framework side: existing checkpoint primitives save state, but none of the major frameworks ship automatic fallback routing or a dead-letter queue for a step that fails after a checkpoint, leaving the actual recovery decision (retry, roll back, escalate, abandon) to be coded by hand every time.

## The Project
A recovery middleware layered on top of an existing framework's checkpoint primitive: on a step failure, it automatically rolls shared state back to the last consistent checkpoint rather than leaving partially-applied outputs in place, classifies the failure (transient vs. likely-permanent) against a configurable policy, and routes unrecoverable failures to a dead-letter queue for human review instead of silently corrupting downstream state or crash-looping. Non-idempotent side effects (an email already sent, a payment already charged) are flagged at design time so rollback never pretends to undo something it can't.

Components: a checkpoint-wrapper adapter for one framework first (LangGraph); a rollback engine that restores shared state to the last checkpoint on failure; a dead-letter queue for failures that exhaust retry/rollback policy; a side-effect registry where each step declares whether its action is idempotent/reversible, non-idempotent, or external-and-irreversible, used to gate whether automatic rollback is even safe to attempt.

## Tangible Impact
**Population**: Teams building production multi-step agent pipelines with real side effects — customer-analysis pipelines that write CRM records, document-processing chains that trigger downstream notifications, ops pipelines that call external APIs — already using LangGraph/CrewAI/Google ADK's checkpoint primitives but still hand-rolling the actual recovery decision, per the Latenode thread and the Diagrid critique's named list of frameworks.
**Mechanism**: Today a mid-run failure after a checkpoint either leaves shared state half-applied (requiring manual cleanup) or is "recovered" by ad hoc code specific to that one pipeline. An automatic rollback-plus-dead-letter layer turns that into a consistent, auditable recovery path: the system either reaches a known-good state automatically or surfaces the failure to a human with full context, in both cases without the team writing bespoke recovery logic per pipeline.
**Measure**: (1) percentage of mid-run failures recovered to a consistent state automatically, without manual intervention, on a pilot team's pipeline, before vs. after adoption; (2) count of inconsistent half-applied states discovered in production, before vs. after; (3) time from failure to either automatic recovery or a dead-lettered, actionable report for human review.

## Why Now
LangGraph/CrewAI/Google ADK checkpointing primitives only reached broad, maintained, multi-backend support in 2026 (per `gh search` results showing active MySQL/DynamoDB/Firestore checkpoint-saver backends) — giving this project a mature save/restore substrate to build the missing rollback-and-dead-letter decision layer on top of, which didn't exist reliably before this year.

## Skill Angle
Given a description of a pipeline's steps and which ones have side effects, flag which steps are safe to automatically roll back (idempotent or cleanly reversible), which need a compensating action instead of a rollback (e.g., issuing a refund rather than "un-sending" a payment), and recommend checkpoint placement so no step straddles an irreversible action without a checkpoint immediately before it. Useful as a design-time review before committing to the full recovery runtime.

## MVP Sketch
Build a rollback-and-dead-letter wrapper around LangGraph's checkpointer for a 3-agent pipeline modeled on the Latenode example (extract → analyze → write-to-CRM); register each step's side-effect type; inject failures after each step and confirm the system either rolls back cleanly or routes to the dead-letter queue, versus a baseline with no recovery layer left in an inconsistent state. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- The Diagrid critique's framing suggests a framework vendor (LangGraph, CrewAI) could ship native fallback routing directly, which would undercut a standalone project's reason to exist — differentiation must come from cross-framework portability and the explicit side-effect registry, not just "rollback for LangGraph."
- Rollback is fundamentally unsafe for non-idempotent external side effects (an email can't be unsent) — the side-effect registry is load-bearing; skipping it risks the project papering over unsafe "rollbacks" that just hide a real problem.
- COCO's asynchronous-oversight approach is a closely adjacent academic mitigation worth evaluating as a foundation rather than building the rollback engine from scratch.
- Distinguishing "transient, worth retrying" from "permanent, needs a human" failures reliably, without a bespoke classifier per pipeline, is the hardest open design question.
