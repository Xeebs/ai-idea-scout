---
name: multi-agent-necessity-decision-checklist
description: Scores a task or architecture sketch against six weighted criteria to produce a single-agent-with-tools / hybrid / multi-agent recommendation plus a quantified "multi-agent tax" estimate (tokens, latency, failure surface). Use when a user is deciding whether a system under design should be multi-agent, or asks "should this be multi-agent?" about something they're building or already pasted.
---

# Multi-Agent Necessity Decision Checklist

## When to use this

The user is at a design decision point for an agentic system and either:
- explicitly asks "should this be multi-agent?", "do I need multiple agents for this?", or "is this overkill?", or
- pastes a task description, planned agent roles, or an architecture sketch/code and asks for a review of whether the split into multiple agents is justified, or
- is scaffolding a new agent project from a multi-agent starter kit/tutorial and wants a sanity check before committing to that shape.

This is a one-shot scoring tool, not a running benchmark harness and not a linter. It does not execute the user's code or measure real tokens/latency — it produces a structured, defensible recommendation from the information the user provides, flagged clearly as an estimate.

## Inputs

**Data source**: Manual — the user pastes a task/system description, existing agent-role sketch, or architecture code excerpt, plus stated constraints (latency/cost budget, team size, debugging capacity); no connector exists or is needed for this rubric-scoring use case (per the parent idea's Data Sources field).

Ask for, or extract from what's already pasted:
1. **Task description** — what the system needs to accomplish, in the user's own words.
2. **Planned or existing agent roles** — if the user already has a design (e.g. "planner agent + 3 worker agents + critic agent"), get the list; if undecided, note "undecided — scoring from task alone."
3. **Constraints** — latency budget (interactive/sub-second vs. batch/minutes), cost/token budget if known, team size, and debugging capacity (can the team trace a failure across multiple agent handoffs today, or not).

If constraints are entirely unstated, proceed with the task description alone, score what's answerable, and mark the cost/latency-budget and debugging-capacity criteria `UNSTATED — assumed neutral (3/5)` rather than guessing a number and presenting it as given.

## Procedure

1. **Score six criteria, 0–5 each**, where higher = pushes toward multi-agent:
   - **Decomposability** (weight 2) — does the task split into genuinely independent subtasks with little shared state, or is it one continuous reasoning chain? 0 = continuous chain, 5 = cleanly independent subtasks.
   - **Specialization need** (weight 2) — do subtasks need materially different tools, personas, or domain context that one agent/prompt can't hold well simultaneously? 0 = same context serves all, 5 = sharply different expertise per subtask.
   - **Verification/critique need** (weight 1.5) — does the task benefit from an independent check on the main agent's output (adversarial review, second opinion)? 0 = self-checking is adequate, 5 = independent critique materially changes outcomes.
   - **Parallelism value** (weight 1.5) — does running subtasks concurrently save meaningful wall-clock time, or is the work inherently sequential? 0 = sequential, 5 = high parallel speedup available.
   - **Cost/latency budget** (weight 2) — how much budget exists to absorb the overhead of multiple agent calls? 0 = tight interactive budget, 5 = generous batch budget.
   - **Debugging capacity** (weight 2) — can the team actually trace and fix failures across agent-to-agent handoffs today? 0 = no tracing/observability in place, 5 = mature multi-agent tracing already exists.
2. **Compute the weighted total**: sum each score × its weight. Max possible = 55 (5 × 11 total weight).
3. **Map to a recommendation**:
   - Total < 22 (bottom 40%) → **single-agent-with-tools**.
   - Total 22–38 (middle) → **hybrid — prototype both, bias toward single-agent-with-tools first** (this band means the criteria are mixed; say explicitly which 1–2 criteria are driving the score toward multi-agent so the user knows what to re-test if they start single and hit a wall).
   - Total > 38 (top 30%) → **multi-agent justified**.
4. **Estimate the multi-agent tax**, scaled to the proposed (or a minimally viable) number of agent roles N:
   - **Token multiplier**: report the published range (roughly 4x baseline for a single agent with tools, 3x–15x baseline for a naive multi-agent split, scaling up with N and coordination overhead) — label this explicitly as "typical reported range from public benchmarks, not a measurement of your system."
   - **Latency multiplier**: each sequential agent-to-agent handoff adds a full round trip; roughly (N_sequential_handoffs + 1)x baseline single-call latency if handoffs are sequential, closer to 1x–2x if subtasks genuinely run in parallel.
   - **Failure surface**: each additional handoff is an added place context can be dropped, mis-passed, or misinterpreted — call out specifically how many new handoff points the proposed design adds versus single-agent.
5. **Surface non-performance reasons separately, never folded into the score.** If the user mentions team ownership boundaries, compliance/data-separation requirements, or org-chart reasons for splitting, note them in a separate line — these can override a low score and the rubric should say so rather than overriding or ignoring them.
6. **If the design is already built** (user pasted code/roles), name the specific criteria the existing split satisfies or fails, not just a generic score — point at the actual role boundaries described.

## Output format

A single reply, in this order:
1. **Verdict** — one line: `Recommendation: <single-agent-with-tools | hybrid | multi-agent justified>` with the weighted total and max (e.g. "27/55").
2. **Criteria table** — criterion, score (0–5), weight, weighted subtotal, one-line reason tied to what the user actually said.
3. **Multi-agent tax estimate** — token multiplier range, latency multiplier, failure-surface count, each labeled as an estimate from published ranges, not a live measurement.
4. **Non-performance factors** (only if the user mentioned any) — listed separately from the score, with a note that these can justify multi-agent even against a low score.
5. **One paragraph** naming the 1–2 criteria driving the result and what evidence (if any) would flip the recommendation.

## Guardrails

- Never present the token/latency multipliers as measured numbers for the user's specific system — they are ranges from public benchmark reports; say so every time, and recommend the user's own small before/after benchmark (same task, single vs. multi-agent) if the decision is high-stakes.
- Never collapse the score to a bare yes/no — always show the per-criterion breakdown; a verdict without the breakdown is exactly the "scattered blog checklist" gap this skill exists to close.
- Never fold stated non-performance reasons (compliance, team ownership) into the numeric score — list them separately and say explicitly they can override the score.
- Never guess a specific number for an unstated constraint and present it as given — mark it `UNSTATED — assumed neutral (3/5)` and say which answer would move the recommendation.
- Do not treat "the tutorial/starter kit defaults to multi-agent" as evidence for any criterion — score only the task and stated constraints, not the scaffold the user happened to start from.
- This is a design-time decision aid, not a runtime orchestrator, linter, or monitoring tool — do not imply it tracks drift over time or re-scores automatically.
