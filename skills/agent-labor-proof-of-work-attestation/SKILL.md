---
name: agent-labor-proof-of-work-attestation
description: Assesses whether a pasted agent execution log/trace and task claim give sufficient evidence that an AI agent actually performed claimed labor, before a payer releases payment or escrow. Use when a human or marketplace operator must decide whether to pay out on an agent's self-reported "task complete" claim.
---

# Agent Labor Evidence-Sufficiency Reviewer

## When to use this
A human (or a marketplace/escrow operator) is about to release payment, approve an invoice, or close out a bounty based on an AI agent's claim that it finished a task — and has an execution log/trace for that specific job, but no independent cryptographic proof it's genuine. Reach for this skill at that decision point, before money moves, not after.

This is explicitly NOT for an agent checking its own work mid-session before reporting "done" (that's a different, already-common pattern — see Guardrails). It is for a *third party* judging someone else's (or something else's) finished-work claim from the outside, using only what's on paper.

## Inputs
**Data source**: Manual — the user pastes (a) the agent's execution log/trace export for this specific job (whatever tool-call records, intermediate outputs, and timestamps the agent's framework produced) and (b) the original task description or acceptance criteria the agent was given. Nothing is fetched automatically; this skill only reasons over what is pasted. (Upgrade path: once a specific trace format from a named observability backend — e.g. Langfuse, LangSmith — or a specific agent-labor marketplace's receipt format is targeted, this could read traces directly instead of requiring paste; no such connector is wired up today, so paste is the honest starting point.)

Required for a usable result:
1. The task description or acceptance criteria the agent was asked to satisfy (even informal — "write and test a parser for X").
2. The execution log/trace: whatever the agent's framework logged — step list, tool calls, intermediate outputs, timestamps. A bare final-answer-only submission with no intermediate trace is a valid input too (it just scores as weak evidence — see Procedure step 4).

If either is missing entirely, say so and stop — do not infer acceptance criteria from nothing, and do not fabricate trace content that wasn't pasted.

## Procedure
1. **Extract acceptance criteria** from the task description: the concrete deliverable, format, and any stated constraints (deadline, must-pass tests, must-use-source, etc.). If the task description is vague, state the acceptance criteria you're assuming and flag them as inferred, not given.
2. **Walk the trace step by step.** For each step, note: what action/tool was claimed, what input it used, what output it produced, and the timestamp if present. Flag any step whose input doesn't trace back to a prior step's output or the original task (a logical gap in the chain).
3. **Check timestamp plausibility.** Flag steps where elapsed time is implausible for the claimed action (e.g., a "web search" step logged as 0 seconds, a multi-file refactor logged as happening in the same second as the task was assigned).
4. **Classify the evidence density**:
   - **Bare claim** — final output only, no intermediate steps shown at all.
   - **Self-narrated** — the agent describes what it did in prose, but no raw tool-call inputs/outputs are shown (only the agent's own summary of them).
   - **Partial trace** — some raw tool-call records shown, but gaps or missing steps between claimed start and final output.
   - **Full trace** — a step-by-step record from task receipt to final output, with raw (not paraphrased) intermediate inputs/outputs at each step.
5. **Cross-check the final output against the acceptance criteria from step 1.** Does the output actually satisfy what was asked, independent of whether the process looks genuine? A genuine-looking trace that produces a non-conforming output is still a failed claim.
6. **Compile red flags**: anything from steps 2–3, plus any sign the log could have been authored after the fact to match a known-good output (e.g., suspiciously round timestamps, steps that reference tool names/outputs not consistent with any known framework, a trace that is shorter than the task plausibly requires).
7. **Assign an Evidence Sufficiency Rating** — one of INSUFFICIENT / WEAK / MODERATE / STRONG — driven primarily by the evidence density classification (step 4) and the red-flag count (step 6). A "Bare claim" or "Self-narrated" trace with any red flags is INSUFFICIENT; a "Full trace" with no red flags and output meeting criteria is STRONG. Never rate STRONG for anything short of a full, raw, criteria-meeting trace.
8. **List the specific missing evidence** that would most improve the rating by one level — be concrete ("the raw API response for step 3 is missing, only the agent's paraphrase is shown," not "more evidence needed").
9. **Give a plain recommendation**: Pay / Hold and request specific evidence (list it) / Reject — framed as a risk read for the human to weigh, never a guarantee.

## Output format
A single structured report, in this order:
1. **Task Claim Summary** — one or two sentences restating what was claimed to be delivered.
2. **Acceptance Criteria** — bulleted, tagged `(stated)` or `(inferred)`.
3. **Evidence Walkthrough** — numbered steps from the trace, each with action / input / output / timestamp and any chain-gap or timestamp flag inline.
4. **Evidence Density Classification** — one of the four levels from step 4, with the one-line reason.
5. **Red Flags** — bulleted list, or "None found" if genuinely none.
6. **Output-vs-Criteria Check** — pass/fail per acceptance criterion.
7. **Evidence Sufficiency Rating** — INSUFFICIENT / WEAK / MODERATE / STRONG, with a one-line justification.
8. **Missing Evidence Checklist** — concrete items that would raise the rating.
9. **Recommendation** — Pay / Hold (with requested evidence listed) / Reject, with the reasoning in one sentence.

## Guardrails
- Never state or imply cryptographic certainty ("this proves the agent did the work"). This skill produces a plausibility read for a human decision-maker, not a cryptographic or legal proof — it is a weaker, complementary signal to actual signed/hash-chained receipts and re-execution, not a replacement for them.
- Never invent trace content, timestamps, or tool calls that were not in the pasted log. If the log is sparse, say the log is sparse — do not pad it with plausible-sounding detail.
- Never treat the agent's own prose narration of what it did as equivalent evidence to raw tool-call input/output. A log that is pure self-narration must be classified no higher than "Self-narrated," regardless of how detailed or confident it reads.
- Never make the final pay/reject decision unilaterally — always frame step 9 as a recommendation with stated reasoning, leaving the actual call to the human.
- Do not confuse this with an agent self-checking its own work before reporting "done" within its own session (a common existing pattern elsewhere) — this skill's trigger is a third party evaluating someone else's finished-work claim after the fact, from a paper trail alone.
- If the task description/acceptance criteria were not supplied at all, do not proceed by guessing what the task was — stop and ask for it.
