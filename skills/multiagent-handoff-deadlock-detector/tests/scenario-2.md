# Scenario 2 — CrewAI crew with a misconfigured circular task dependency, plus an unstated edge

## Input (what the user pastes)

> We're using CrewAI for a contract-review crew. Here's the task setup:
>
> - `extract_clauses_task`: assigned to **Extractor** agent. No `context` dependency — this is the entry point.
> - `risk_flag_task`: assigned to **RiskAnalyst** agent. `context=[extract_clauses_task, approval_task]` — it needs both the extracted clauses AND the approval task's output before it can run.
> - `approval_task`: assigned to **Approver** agent. `context=[risk_flag_task]` — it needs the risk flags before it can run.
> - `summary_task`: assigned to **Summarizer** agent. `context=[approval_task]`, `async_execution=True`.
>
> We're also not sure whether `extract_clauses_task` to `risk_flag_task` is meant to block or not — I think CrewAI's default sequential process makes every task wait for its listed context tasks, but I haven't checked whether `risk_flag_task` can partially start before `approval_task` finishes or has to wait for the full thing.
>
> Separately, is there anything wrong with risk_flag_task needing both extract_clauses_task and approval_task?

## Expected handling

The reviewer should build the graph: Extractor → RiskAnalyst (context dependency), Approver → RiskAnalyst (context dependency), RiskAnalyst → Approver (context dependency), Approver → Summarizer (context dependency, ASYNC per `async_execution=True`).

It must find:
1. **RiskAnalyst ↔ Approver** — a genuine circular dependency: `risk_flag_task` needs `approval_task`'s output, and `approval_task` needs `risk_flag_task`'s output. Neither can run first. This should be classified `DEADLOCK_RISK` (or flagged under the "mutual-dependency smell" path even without the user explicitly calling it a graph cycle) — this is CrewAI's default sequential process, so these context edges are BLOCKING by CrewAI's own default behavior, and there is no stated mechanism (no fallback task, no partial-data allowance, no timeout) that lets either task proceed without the other.
2. **Extractor → RiskAnalyst** edge: the user explicitly says they're unsure whether this blocks fully or partially. This edge's wait semantics should be marked `UNSTATED`, and since the deadlocked cycle doesn't actually depend on resolving this particular ambiguity (RiskAnalyst↔Approver is self-contained and already flaggable), the reviewer should still list it as an open question for completeness without using it as an excuse to downgrade the RiskAnalyst↔Approver finding to UNCERTAIN.

The breaking rule for RiskAnalyst↔Approver must name the specific fix: e.g., remove `approval_task` from `risk_flag_task`'s context (so Approver reviews the risk flags sequentially after RiskAnalyst produces them, not concurrently with a circular need), or restructure so Approver's review happens strictly after RiskAnalyst with no reverse dependency.

## Pass/fail criteria

- PASS requires: RiskAnalyst↔Approver correctly identified as a genuine circular dependency and flagged (DEADLOCK_RISK or equivalent "mutual-dependency smell" language from the SKILL.md), with a named, specific fix (e.g., removing one direction of the context dependency); the Extractor→RiskAnalyst edge correctly marked UNSTATED and listed as an open question rather than guessed at; Summarizer's `async_execution=True` edge correctly treated as ASYNC, not flagged as blocking risk.
- FAIL if: the circular `context=[...]` dependency between RiskAnalyst and Approver is missed or described only as "a bit unusual" without a clear DEADLOCK_RISK-equivalent flag and concrete fix; or if the reviewer invents a termination mechanism (e.g., assumes CrewAI "must have" a default timeout) that was never stated in the input; or if the UNSTATED Extractor→RiskAnalyst ambiguity is silently resolved one way or another instead of being surfaced as an open question.
