---
name: multiagent-cross-framework-coordination-benchmark
description: Recommends which multi-agent coordination benchmark scenarios to run before/after an architecture change (new agent, topology switch, agent split), and how to interpret the resulting score delta. Use when a team on AutoGen, CrewAI, or LangGraph is deciding whether a proposed coordination change is worth shipping, before they build a bespoke test harness.
---

# Multi-Agent Coordination Benchmark Scenario Advisor

## When to use this
A team running a multi-agent system on AutoGen, CrewAI, or LangGraph is considering a coordination-architecture change — adding a specialist agent, switching from a mesh/group-chat topology to a hierarchical/supervisor one, splitting one monolithic agent into two, or changing how agents hand off tasks — and wants to know, before building a bespoke test harness, which specific test scenarios would actually reveal whether the change helped or hurt, and how to read the resulting numbers once they run them. Reach for this the moment someone says "we're thinking about restructuring our agents, how do we know if it's actually better?" rather than after they've already spent days improvising a one-off eval.

This skill is the one-shot advisory half of a larger idea (a converged cross-framework benchmark harness with live framework adapters). It does not run anything or execute code against a live system — it tells the team what to run and how to read it. Running the full harness is the PROJECT half, not this skill.

## Inputs
**Data source**: Manual — the user describes, in plain text, (1) their current framework (AutoGen, CrewAI, or LangGraph), (2) their current topology in a sentence or two (e.g. "three agents in a round-robin group chat" or "one supervisor dispatching to two workers"), (3) their task domain in one sentence (e.g. "customer support ticket triage and drafting," "multi-step code review and patching"), and (4) the specific change under consideration (e.g. "adding a dedicated QA/verifier agent before the final answer is returned"). No file upload, API call, or connector is used — everything the skill reasons about is typed into the conversation.

If the user has already run any benchmark (from MASBENCH, CooperBench, OrchBench, DPBench, ALEM, or their own harness) and has before/after numbers, they can paste those too — the skill will fold them into its interpretation step rather than only recommending scenarios in the abstract.

## Procedure
1. **Classify the change type.** Map the user's described change into one of four buckets, because each implies a different failure mode to test for:
   - *Adding a specialist agent* → risk is redundant/wasted turns and increased message overhead, not necessarily task success.
   - *Topology switch (mesh → hierarchical, or reverse)* → risk is bottlenecking at the coordinator (hierarchical) vs. communication explosion (mesh).
   - *Splitting a monolithic agent* → risk is information loss at the handoff boundary and failure-recovery when the split introduces a new point of miscommunication.
   - *Changing handoff/routing logic* → risk is task misrouting and recovery-after-failure rate specifically at the handoff step.
2. **Classify the task domain's coordination shape.** Ask (or infer from the one-sentence domain description): is the underlying work parallelizable (independent sub-tasks that could run concurrently) or sequential (each step strictly depends on the prior one)? This matters because multi-agent coordination changes tend to help parallelizable work and can measurably hurt sequential work — a scenario recommendation that ignores this will point the team at the wrong test.
3. **Recommend 2-4 specific scenario types** (not graded against one single benchmark the team may not have access to — describe the scenario *shape* so the team can either pull a matching task from a public source like MASBENCH/CooperBench/OrchBench or construct an equivalent one with their own data) that would most directly surface the risk identified in step 1, filtered by the coordination shape from step 2. For each recommended scenario, state explicitly which of the four scorecard metrics it is designed to move: task success rate, message/communication overhead, redundant-turn rate, recovery-after-failure rate.
4. **Specify the before/after protocol**: run the *same* scenario against the current architecture (baseline) and the proposed architecture (candidate), holding the task set, model, and prompts constant — the only variable that changes is the coordination structure under test. State this explicitly to the user; a before/after comparison that also changes the model or prompts is not a valid signal.
5. **If the user supplies actual before/after numbers**, interpret the delta: name which metric(s) moved, in which direction, and whether that direction supports or contradicts the hypothesis behind the proposed change (e.g. "redundant-turn rate dropped 40% but task success rate also dropped 12% — the specialist agent reduced wasted work but is introducing a new failure point; recommend testing the failure-recovery scenario specifically before shipping"). If the user has no numbers yet, skip this step and end at the recommended protocol.
6. **Name the specific risk of over-interpreting a single scenario run**: one scenario, one run, is not proof — flag that the recommendation is directional, and that the team should treat a single before/after comparison as a go/no-go signal for further testing, not a final verdict, especially for consequential architecture decisions.

## Output format
A short structured response with four sections, in this order:
1. **Change classification** — one line naming which of the four change-type buckets applies and the task's parallelizable/sequential classification.
2. **Recommended scenarios** — a numbered list of 2-4 scenario types, each with: the scenario shape in one sentence, which metric it targets, and (if a public source benchmark has a matching task family) which one to pull from.
3. **Before/after protocol** — 2-3 sentences stating exactly what must be held constant and what must vary between the baseline and candidate runs.
4. **Interpretation** — either the delta interpretation (if numbers were supplied) or a one-line note that this step applies once results are in, plus the single-run-is-not-proof caveat.

Keep the whole response under ~300 words — this is a fast pre-commit advisory check, not a report.

## Guardrails
- Never claim to have run a benchmark, executed code, or queried a live AutoGen/CrewAI/LangGraph system — this skill only reasons from what the user describes or pastes; it has no connector and no execution capability.
- Never recommend a scenario without naming which of the four scorecard metrics (task success, message overhead, redundant-turn rate, recovery-after-failure rate) it targets — an untargeted recommendation is just generic advice.
- Never treat a single before/after number pair as conclusive proof the change helped or hurt — always flag it as directional and recommend a second scenario or a larger run before a consequential architecture decision ships.
- Never silently assume the task domain is parallelizable or sequential — if the user's one-sentence domain description doesn't make this clear, ask, since the recommendation is wrong in opposite ways for the two cases.
- Never recommend changing the model or prompts as part of the "before/after" comparison — that confounds the result; the only thing that may vary between baseline and candidate runs is the coordination structure.
