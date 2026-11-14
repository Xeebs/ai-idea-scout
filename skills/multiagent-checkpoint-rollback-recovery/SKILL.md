---
name: multiagent-checkpoint-rollback-recovery
description: Reviews a described multi-agent/multi-step pipeline's steps for which ones are safe to automatically roll back, which need a compensating action instead, and where checkpoints must sit so a mid-run failure never re-fires an irreversible side effect (an email, a charge, a webhook). Use before building or hardening a recovery/retry layer on top of a checkpointing framework (LangGraph, CrewAI, Google ADK, or a hand-rolled one).
---

# Rollback Safety Review: Checkpoint Placement for Side-Effecting Pipelines

## When to use this
Trigger this when someone describes a sequential multi-agent or multi-step pipeline (3+ steps, at least one of which has a real-world side effect — a DB write, an email/SMS send, a payment, a webhook call, a third-party API call) and asks a version of:
- "Where should we put checkpoints so a failure doesn't leave things half-done?"
- "Is it safe to automatically roll back to the last checkpoint if step 4 fails?"
- "We got double-charged/double-emailed on a retry — how do we stop that?"
- "We're about to wire up LangGraph/CrewAI/Google ADK checkpointing — what do we need to handle ourselves on top of it?"

This is a one-shot **design review**, done before or alongside building the actual recovery runtime. It does not execute, monitor, or roll back anything itself — it tells you which steps are safe for a recovery layer to auto-roll-back, which need a human-defined compensating action, and exactly where checkpoints need to sit. Do not use this for estimating error rates or deciding whether adding a verification/review step improves accuracy — that is a different question (see the sibling skill `multiagent-compounding-error-checkpoint-optimizer` for that).

## Inputs
**Data source**: Manual — the user pastes a description of their pipeline's steps, in order, and for each step what (if anything) it does outside the pipeline's own internal/scratch state (writes to a shared DB, calls an external API, sends a notification, charges a payment, triggers a downstream system). No connector is read; this skill works from the user's own description, not from live code or logs.

Required:
1. **Ordered step list** with a one-line description of each (e.g. "1. extract: pull structured fields from raw doc. 2. analyze: classify sentiment. 3. write-to-crm: create a CRM record. 4. notify: email the account owner.").
2. **Side-effect note per step**, as much as the user knows: does this step write only to pipeline-internal/scratch state (no external effect), write to a shared system that could be overwritten safely on retry, create/charge/send something external, or call a third party that fires immediately and can't be recalled.

Optional:
3. Which checkpointing framework (if any) is already in use (LangGraph checkpointer, CrewAI, Google ADK, a custom key-value store, or "none yet").
4. Any existing idempotency keys, dedup logic, or compensating actions already wired up (e.g. "the CRM write uses an upsert on customer ID" or "we have a refund endpoint").

If a step's side effect isn't stated, do not guess — ask, or if asked to proceed anyway, default that step to the worst case (irreversible) and say so explicitly in the output.

## Procedure
1. **Parse the pipeline** into an ordered step list. If fewer than 3 steps, or if no step has any external side effect, tell the user there's nothing to checkpoint-review here and stop.
2. **Classify each step's side-effect type**, using only what the user stated (never inferred from the step's name alone):
   - **NONE** — pure computation/transform on pipeline-internal state; re-running it changes nothing externally.
   - **IDEMPOTENT** — writes externally but safely re-runnable with the same result (e.g. an upsert keyed on a stable ID, overwriting the same file/record).
   - **NON-IDEMPOTENT REVERSIBLE** — creates or changes external state that a *defined* compensating action can undo (e.g. a CRM record that can be deleted, a payment that can be refunded via a named refund path).
   - **IRREVERSIBLE** — fires something external that cannot be recalled once sent (an email, SMS, push notification, webhook to a third party, a payment settled with no refund path, any "message already left the building" action).
   - **UNSPECIFIED** — the user didn't say; flag it and default to treating it as IRREVERSIBLE until confirmed otherwise.
3. **Determine rollback safety per step** from the classification:
   - NONE or IDEMPOTENT → safe for a recovery layer to automatically roll back / retry without special handling.
   - NON-IDEMPOTENT REVERSIBLE → automatic rollback must trigger the compensating action, not just revert pipeline-internal state. If the user named one, record it; if not, flag "compensating action undefined — do not auto-rollback until one is defined."
   - IRREVERSIBLE or UNSPECIFIED → never auto-rollback. The only safe moves are (a) prevent it from firing twice on retry via an idempotency key/dedup guard, and (b) make sure a checkpoint exists immediately *before* this step so a retry resumes before it, not after.
4. **Recommend checkpoint placement**: a checkpoint is required immediately before every NON-IDEMPOTENT REVERSIBLE or IRREVERSIBLE/UNSPECIFIED step. Checkpoints between two NONE/IDEMPOTENT steps are optional (cheap insurance, not safety-critical).
5. **Flag straddling risk**: any two IRREVERSIBLE or NON-IDEMPOTENT REVERSIBLE steps with no checkpoint between them, or any such step with no checkpoint immediately before it. This is the specific failure mode where a retry re-fires an already-sent side effect — call it out by step name, don't bury it in a general caveat.
6. **State what's still missing**, explicitly: any UNSPECIFIED step the user needs to classify, any REVERSIBLE step with no named compensating action, and whether an idempotency-key/dedup mechanism exists for the IRREVERSIBLE steps (ask if not stated).

## Output format
A single report, in this order:
1. **Pipeline as understood** — numbered step list, restated.
2. **Per-step classification table** — columns: Step | Side-effect type | Rollback safety (auto-safe / needs compensating action / never auto-rollback) | Compensating action (named, or "undefined") | Checkpoint required immediately before this step? (yes/no/optional).
3. **Straddling risks** — named step pairs/sequences with no checkpoint protecting an irreversible or reversible-but-costly action, in plain language ("step 4 (send invoice email) has no checkpoint before it — a retry after a step 3 failure could re-send the email").
4. **Recommended checkpoint placements** — ordered list of exact insertion points ("before step 3: write-to-crm" / "before step 4: notify"), each tagged required or optional.
5. **Open items** — every UNSPECIFIED step, every undefined compensating action, and whether idempotency keys/dedup exist for irreversible steps — phrased as questions back to the user, not assumptions.

## Guardrails
- Never classify a step's side effect from its name alone (e.g. never assume "write-to-crm" is safely idempotent) — only use what the user explicitly stated; anything unstated is UNSPECIFIED and defaults to the irreversible/no-auto-rollback treatment.
- Never recommend automatic rollback for a NON-IDEMPOTENT REVERSIBLE or IRREVERSIBLE step — reversible ones need their compensating action to run, irreversible ones can't be rolled back at all, only guarded against re-firing.
- Never invent a compensating action (e.g. assuming a refund endpoint exists) — if the user didn't name one, report it as undefined and ask, don't fabricate a plausible-sounding one.
- Never claim this review enforces anything at runtime — it is a design-time checklist to hand to whoever builds or configures the actual checkpointing/recovery layer (LangGraph, CrewAI, Google ADK, or custom), not a substitute for it.
- Never conflate this with error-rate/accuracy checkpoint placement (deciding where an extra review step reduces failures) — this skill is exclusively about side-effect reversibility and safe retry/rollback boundaries.
