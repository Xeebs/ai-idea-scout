---
name: council-agent-merge-gate-recovery
description: Audits a council-of-agents delivery pipeline's merge-gate and recovery logic for three specific failure modes — cross-seat status inference, unintercepted out-of-band early merges, and ambiguous timeout/empty-response recovery — and produces a concrete remediation plan. Use when a team running multiple agents that independently produce competing/complementary work (PRs, drafts, analyses) that gets gated and merged as a set reports a confusing panel-wide failure, an early/duplicate merge, or wants a pre-adoption review of their gate design.
---

# Council Agent Merge-Gate & Recovery Auditor

## When to use this
Reach for this skill when someone describes (or pastes code/config for) a "council of agents" delivery setup — multiple agents independently producing work against the same ticket/task that a gating layer merges as a set — and any of the following is true:
- They report that one member's silent/empty/timeout response caused the whole panel to be marked failed, even though other members actually succeeded.
- A member merged, pushed, or finalized its output before the gate reviewed it, and the recovery/rollback logic afterward behaved confusingly (duplicated status, wrong seat retried, lost track of which seat actually failed).
- They are designing or about to adopt a council-of-agents merge gate and want a pre-flight audit before building it, rather than discovering these three failure modes in production.

This is a one-off audit/design-review skill, not a running system — it reads what the user hands it and returns a report. It does not connect to the user's repo, CI, or orchestration framework and does not execute or modify anything.

## Inputs
**Data source**: Manual — the user pastes (a) the actual merge-gate/orchestration code or config that decides when the council's combined output gets merged and how each member's status is tracked, and (b) a plain-language description of their council setup (how many seats/members, what platform — GitHub PRs, a task queue, an orchestration framework's own task-state API) and, if auditing a specific incident, what happened (what was logged, what the user observed).

Minimum viable input: the merge-gate/status-tracking code or config alone. An incident description sharpens the audit but is optional — without one, the skill runs a pre-flight review instead of a root-cause analysis.

## Procedure
1. **Locate the status model** in the pasted code/config. Determine: is each council seat tracked under its own key (e.g., a dict/table keyed by seat ID, each with its own pending/running/succeeded/failed/empty state), or is there a single shared panel-wide flag/counter/boolean that multiple seats write to or that gets read as "nothing failed yet"? Quote the exact variable/field responsible.
2. **Locate the merge trigger condition.** Find the exact boolean/condition that permits merge. Check specifically: does it require an explicit terminal verdict from *every* seat, or does it merge on an "any succeeded" / "no visible error" / absence-of-failure default? Quote the condition.
3. **Check for early-merge interception.** Search the pasted material for any check, hook, or webhook listener that detects a seat finalizing/merging/pushing *outside* the gate's own merge step (e.g., a direct push, a member calling its own merge API). If none is present in what was pasted, say so explicitly — do not assume it exists elsewhere.
4. **Check timeout/empty-response handling.** Find what happens when a seat times out or returns an empty/null response. Trace whether that seat's failure state can overwrite, get conflated with, or get read as representative of any other seat's state (shared object mutation, a single aggregate error flag, a loop that breaks on first failure and never records the rest). Quote the relevant lines.
5. **Score each of the three failure modes** as one of:
   - `CONFIRMED` — the pasted material contains the exact pattern (quote it).
   - `LIKELY` — a structural risk exists (e.g., per-seat tracking exists but the merge condition still reads an aggregate flag) even if not yet triggered.
   - `NOT PRESENT` — the pasted material already handles this correctly (quote the protective pattern).
   - `CANNOT DETERMINE` — the pasted material doesn't cover this path; say exactly what additional code/config would be needed to check.
6. **If an incident description was given**, map it to exactly one of the three failure modes and trace the causal path through the pasted code: which line's behavior produced the reported symptom.
7. **Write the remediation plan** — one item per `CONFIRMED` or `LIKELY` finding, each naming the exact location (function/variable/line) and the specific change (e.g., "replace the shared `panel_ready` boolean with a `seat_status: dict[seat_id, Verdict]`, initialized to `PENDING`, written only by that seat's own callback"). Never propose a shared/aggregate status field as part of any fix.
8. **Write the recovery policy table** — for timeout, empty-response, and detected-early-merge, state a recommended action (retry-same-seat with a configurable retry count, escalate-to-human, revert-and-requeue-that-seat-only) and the specific config knob name the user's system would need to expose to make it configurable.

## Output format
A single markdown report with four sections, in this order:
1. **Verdict table** — three rows (one per failure mode), columns: Failure Mode | Verdict (CONFIRMED/LIKELY/NOT PRESENT/CANNOT DETERMINE) | Evidence (quoted snippet or "not covered in pasted material").
2. **Incident trace** (only if an incident was described) — one paragraph connecting the reported symptom to the specific line(s) responsible.
3. **Remediation plan** — numbered list, one concrete code/config change per CONFIRMED/LIKELY finding, each with a "before" quote and an "after" sketch.
4. **Recovery policy table** — rows: Seat Event (timeout / empty response / early merge detected) | Recommended Policy | Config Knob Name | Note on when to prefer escalate-to-human over retry.

## Guardrails
- Never mark a failure mode `CONFIRMED` without quoting the exact snippet from what the user pasted — if the relevant code wasn't shown, use `CANNOT DETERMINE` and say what's missing. Do not infer unseen code as a fact.
- Never recommend a shared/aggregate status variable as any part of a fix — every remediation for the cross-seat-inference mode must land on a per-seat-keyed state.
- Never claim to perform, execute, or test the remediation — this skill produces a plan for the user's own system; it has no access to their repo, CI, or runtime, and never pretends otherwise.
- If recommending interception/reversion of an out-of-band early merge, always flag explicitly that reverting a merge already landed on a shared branch is a real, operationally risky git operation (not a sandboxed rollback) — never present it as a casual fix.
- If the user's underlying agent framework collapses all seats into one aggregate response *before* the pasted code even runs (no per-seat visibility is possible at this layer), say so plainly: the fix needs upstream instrumentation in the framework or orchestration layer, not just a gate-logic change, and don't propose a gate-level fix that can't actually work given that constraint.
- Do not pad the report with failure modes outside the three in scope (cross-seat inference, early-merge interception, timeout/empty recovery policy) — if the user asks about something else in their pipeline, say it's out of scope for this audit rather than improvising a verdict on it.
