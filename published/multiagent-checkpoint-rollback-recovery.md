# Last Good State: Checkpoint-and-Rollback Recovery for Mid-Run Multi-Agent Failures

A three-agent pipeline fails on step two. Agent one already wrote its output. Agent three is waiting. What state is the system actually in right now — and who is responsible for deciding what happens next? For most teams running production multi-agent pipelines today, the honest answer is: whoever is on call, improvising, because nobody built that decision into the system.

## The Gap

A builder on the Latenode community forum described exactly this, for a three-agent customer-analysis pipeline: "If agent two fails partway through processing agent one's output, you're left in an inconsistent state. Recovery logic is complex." Another practitioner in the same thread described their fix — checkpoint shared state after each step, manually roll back to the last checkpoint on failure. It works, but it's hand-rolled, specific to that one pipeline, and would need to be rebuilt from scratch for the next one.

The gap isn't that checkpointing doesn't exist — it does, and it's matured fast. LangGraph, CrewAI, and Google ADK all now ship maintained, multi-backend checkpoint-saver primitives (MySQL, DynamoDB, Firestore backends are all actively supported). The gap is what happens *after* a checkpoint is taken and a step still fails. A February 2026 Diagrid engineering post names this directly: "checkpoints are not durable execution — why LangGraph, CrewAI, Google ADK and others fall short for production agent workflows," pointing out that none of them ship automatic fallback routing or a dead-letter queue. The frameworks save your position. They don't tell you what to do when the next move breaks.

So every team ends up re-deriving the same three decisions by hand: roll back or push forward, how to tell a transient failure from a permanent one, and where to send a failure nobody can auto-recover from. That's the "recovery logic is complex" complaint, restated from the framework's side of the fence.

## The Project

The idea is a recovery middleware layered on top of an existing framework's checkpoint primitive, not a replacement for it. On a step failure, it rolls shared state back to the last consistent checkpoint instead of leaving a half-applied output sitting there; it classifies the failure as transient or likely-permanent against a configurable policy; and it routes anything it can't safely resolve to a dead-letter queue for a human to look at — rather than crash-looping or quietly corrupting downstream state.

The piece that keeps this honest is a side-effect registry. Every step in a pipeline declares, up front, whether its action is idempotent and safely re-runnable, non-idempotent but reversible via some compensating action, or external-and-irreversible — an email already sent, a payment already charged. Rollback only ever gets attempted where it's actually safe; everywhere else, the system flags the risk instead of pretending to undo something it fundamentally can't.

The components: a checkpoint-wrapper adapter for one framework first (LangGraph, since that's where the maintained multi-backend checkpointer already lives); a rollback engine that restores state on failure; a dead-letter queue for exhausted retries; and the side-effect registry that gates whether any of this is even attempted.

## Tangible Impact

**Population**: Teams building production multi-step agent pipelines with real side effects — customer-analysis pipelines that write CRM records, document-processing chains that trigger downstream notifications, ops pipelines that call external APIs — already using LangGraph/CrewAI/Google ADK's checkpoint primitives but still hand-rolling the actual recovery decision, per the Latenode thread and the Diagrid critique's named list of frameworks.

**Mechanism**: Today a mid-run failure after a checkpoint either leaves shared state half-applied (requiring manual cleanup) or is "recovered" by ad hoc code specific to that one pipeline. An automatic rollback-plus-dead-letter layer turns that into a consistent, auditable recovery path: the system either reaches a known-good state automatically or surfaces the failure to a human with full context, in both cases without the team writing bespoke recovery logic per pipeline.

**Measure**: (1) percentage of mid-run failures recovered to a consistent state automatically, without manual intervention, on a pilot team's pipeline, before vs. after adoption; (2) count of inconsistent half-applied states discovered in production, before vs. after; (3) time from failure to either automatic recovery or a dead-lettered, actionable report for human review.

## Try It

A companion Claude Code skill, [`skills/multiagent-checkpoint-rollback-recovery/`](../skills/multiagent-checkpoint-rollback-recovery/), is already written — a narrower design-time review, not the full runtime: *"Reviews a described multi-agent/multi-step pipeline's steps for which ones are safe to automatically roll back, which need a compensating action instead, and where checkpoints must sit so a mid-run failure never re-fires an irreversible side effect (an email, a charge, a webhook). Use before building or hardening a recovery/retry layer on top of a checkpointing framework (LangGraph, CrewAI, Google ADK, or a hand-rolled one)."*

To use it: drop the `skills/multiagent-checkpoint-rollback-recovery/` folder into `~/.claude/skills/` if you're running Claude Code, then describe your pipeline's steps in order and what each one does outside the pipeline's own internal state. No Claude Code install? Paste the skill's `README.md` into any AI chat tool as a prompt template — it's written to stand alone. It takes your pipeline description and gives back a per-step rollback-safety table, flags any step that's missing a defined compensating action, and tells you exactly where a checkpoint has to sit so a retry never re-fires something irreversible.

## The Honest Risks

The strongest reason this might not need to exist as a standalone project: the Diagrid critique's own framing is a roadmap a framework vendor could just ship themselves. If LangGraph or CrewAI adds native fallback routing and a dead-letter queue next release, a lot of the runtime's reason to exist goes with it — differentiation has to come from cross-framework portability and the explicit side-effect registry, not from "rollback, but for LangGraph specifically."

Rollback is also fundamentally unsafe for the exact side effects that matter most — an email can't be unsent, a webhook can't be un-fired. The side-effect registry isn't a nice-to-have feature; skip it and the project quietly becomes something that papers over unsafe "rollbacks" instead of preventing them. And classifying a failure as transient-worth-retrying versus permanent-needs-a-human, without a bespoke classifier for every new pipeline, is still an open design question — the idea doesn't claim to have solved it, just to have named it as the hard part. COCO's asynchronous-oversight work (arXiv 2508.13815) is a closely adjacent academic approach worth evaluating as a starting point rather than building the rollback engine from nothing.

Surfaced from `research/2026-11-14-multi-agent-architectures.md`, pattern `P2`.
