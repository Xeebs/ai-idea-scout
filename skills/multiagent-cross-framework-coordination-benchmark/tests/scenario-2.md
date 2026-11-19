# Scenario 2: Topology switch on a LangGraph research pipeline, with before/after numbers already in hand

## Input (what the user hands the skill)

> I run a multi-agent system and I'm considering a coordination architecture change. Here's my setup:
>
> - Framework: LangGraph
> - Current topology: Four research agents operate as a mesh — each one can message any of the other three directly to share findings — collaboratively building a market research report from a set of source documents.
> - Task domain: Multi-source research synthesis. Each agent is assigned a disjoint subset of source documents to read and summarize; the final report requires merging all four summaries into one coherent document, so the subtasks are mostly independent until the merge step.
> - Proposed change: Switching to a hierarchical topology — one supervisor agent that collects each worker's summary and does the merge itself, instead of the four agents messaging each other directly.
>
> Before/after numbers I already have: On our internal 20-task eval set, the mesh topology (baseline) had a task success rate of 78% and an average of 34 inter-agent messages per task. The hierarchical topology (candidate) had a task success rate of 81% and an average of 11 inter-agent messages per task. We haven't measured redundant-turn rate or recovery-after-failure rate yet.

## Pass criteria

The output must:
- [ ] Classify the change as a "topology switch" (mesh → hierarchical) and name the correct risk bucket: communication explosion in mesh vs. potential bottlenecking at the coordinator in hierarchical.
- [ ] Correctly identify the task as mostly parallelizable (four agents reading disjoint sources independently) with a sequential merge step at the end — and note that this generally favors the coordination change reducing overhead without much downside, which is consistent with the supplied numbers.
- [ ] In the interpretation step, correctly read the supplied numbers: task success rate improved slightly (78% → 81%) AND message overhead dropped sharply (34 → 11 messages/task) — both metrics moved in the direction that supports the proposed change. The output must not claim a tradeoff or contradiction that isn't in the data.
- [ ] Still recommend measuring redundant-turn rate and/or recovery-after-failure rate (explicitly named as not yet measured in the input) before treating this as fully validated — e.g. check whether the supervisor becomes a bottleneck under failure/retry conditions.
- [ ] Include the single-run-is-not-proof / one-eval-set caveat even though the numbers look favorable —20 tasks is a real but limited sample.
- [ ] Not recommend changing the model or prompts as part of further testing.

## Fail conditions
- Misreads the numbers as a tradeoff (e.g. incorrectly claims success rate dropped, or claims the data is ambiguous when both metrics clearly favor the candidate).
- Fails to flag that redundant-turn rate and recovery-after-failure rate are still unmeasured gaps, given the user explicitly said so.
- Treats the 20-task eval result as conclusive proof rather than a positive but limited signal.
- Classifies the task domain as purely sequential (missing that the four research sub-tasks are independent before the merge).
