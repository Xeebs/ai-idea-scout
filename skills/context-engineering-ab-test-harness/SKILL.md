---
name: context-engineering-ab-test-harness
description: Designs a rigorous before/after test plan for a proposed context-engineering change (compaction, summarization, tool-output capping, offloading) to an agent system, so a team can measure whether it actually helps their workload instead of guessing from a blog post. Use when a team is about to adopt, keep, or disable a context-management strategy and has no measurement plan yet.
---

# Context-Engineering A/B Test Design Reviewer

## When to use this
A team is running (or building) a production or near-production LLM agent and is deciding whether to turn on, keep, or disable a context-engineering change — compaction, a summarization threshold, tool-output truncation/capping, or an offload-to-filesystem/memory policy. They are currently relying on a framework default, a blog post ("compaction is a win" / "keeping everything is cheaper"), or gut feel, and have not run a controlled comparison on their own workload. Use this skill the moment someone says something like "should we turn on compaction," "will this summarization threshold hurt quality," or "I don't trust our default context settings but I don't know how to test it."

This skill produces the **test plan**, not the test run. It does not execute an agent, call any API, or generate real success/cost numbers — it designs the comparison a human or a separate harness will actually run.

## Inputs
**Data source**: Manual — the user pastes/describes (a) their current context-engineering setup (what compaction/offloading/capping behavior is active today, if any, and which agent framework/CLI it runs on — e.g. Claude Code, Codex CLI, LangGraph, a custom loop), (b) the specific proposed change they want to test, and (c) their own task suite: 10-20 representative task prompts with pass/fail criteria, or a rough description of their workload if they haven't written the suite yet. Optionally they also paste existing cost/latency baseline numbers already pulled from an instrumented production system (OTel, LangSmith, Langfuse) for calibration — but these are pasted figures, not a live connector; this skill never queries a trace store itself. Running the actual comparison against a live agent framework or OTel connector is a separate, PROJECT-shaped harness (execution, not design) — out of scope here.

If the user has no task suite at all, this skill helps them draft a first-pass one (see Procedure step 3) rather than refusing to proceed.

## Procedure
1. **Pin down the change under test.** Ask (or infer from what's given) exactly what differs between "baseline" and "treatment": e.g. "baseline = no compaction, treatment = auto-summarize every 20 turns at 50% context fill." If the user describes something vague ("try compaction"), push for the specific trigger condition and mechanism before proceeding — a fuzzy treatment definition produces an untestable hypothesis.
2. **Write a falsifiable hypothesis** in the form: "If we [specific change], then [specific metric] will [increase/decrease/stay flat] by roughly [magnitude or direction], because [mechanism]." State it even when the user hasn't — this is what turns a vague intuition into something a test can actually confirm or kill.
3. **Build or critique the task sample.**
   - If the user supplied tasks: check for (a) count — flag if fewer than 10, recommend 10-20; (b) diversity — do the tasks span long-horizon/multi-turn work, tool-heavy work, and short single-shot work, or are they all one shape; (c) pass/fail criteria sharpness — reject vague criteria like "looks good" and rewrite each as a checkable condition (specific output, specific tool call made, specific constraint honored).
   - If the user has no tasks: draft 10-15 candidate task prompts from their stated workload description, each with a concrete pass/fail check, and flag them as a first draft the team must validate against real usage before trusting results from them.
   - Explicitly add at least 2-3 tasks designed to catch the failure class the proposed change specifically threatens — e.g. for compaction/summarization, tasks that require recalling a constraint, decision, or file path stated early and needed late (constraint-preservation failures are the documented blind spot of success-rate-only evals).
4. **Define the metrics**, always including all of: (a) task success-rate delta (baseline vs. treatment), (b) total-token and cost delta, (c) wall-clock latency delta, (d) at least one recoverability/constraint-preservation check from step 3, not just aggregate pass/fail. Note that "tokens per completed task" (not tokens per request) is the correct cost metric when a missed detail forces retries or re-fetching.
5. **Specify the statistical plan.** Recommend a repeat-run count (minimum 5, more for noisy tasks) to average over LLM output noise; name a concrete significance test appropriate to the metric (paired test / McNemar's-style comparison for binary pass-fail across matched tasks, a simple bootstrap or t-test for token/latency deltas); state the sample size needed to detect the magnitude of effect named in the hypothesis, even as a rough rule of thumb, so the user knows whether their 10-20 task suite can even resolve the question.
6. **Write the execution handoff.** Produce a short checklist for whoever actually runs the comparison (a human running it manually, or a separate automated harness): what to hold fixed, what to toggle, how many repeats, where to log results.
7. **Flag risks explicitly** — at minimum: (a) whether the task sample is likely representative of real production traffic, (b) the cost of the repeat runs needed for statistical confidence, (c) whether a framework vendor default could change underneath this test, (d) any failure class the chosen metrics still can't catch.

## Output format
A single markdown "A/B Test Design Brief" with these sections in order:
1. **Hypothesis** — the one-sentence falsifiable statement from step 2.
2. **Baseline vs. Treatment** — exact definition of each condition.
3. **Task Sample** — the list of tasks (existing, critiqued, or newly drafted) each with its pass/fail check, annotated with which ones specifically probe the failure class from step 3.
4. **Metrics** — the full metric list from step 4, each with how it's computed.
5. **Statistical Plan** — repeat count, test method, and a one-line note on whether the sample size can resolve the hypothesized effect size.
6. **Execution Checklist** — the handoff list from step 6, written for someone else to follow.
7. **Risks & Caveats** — the step 7 list.

## Guardrails
- Never fabricate or imply real success-rate, cost, or latency numbers — this skill designs a test; it has not run one. Every number in the output is a plan parameter (repeat count, sample size), never a result.
- Never accept a vague treatment definition ("try compaction") without pushing for the specific trigger/threshold — an untestable hypothesis produces an unusable test plan.
- Never produce a metrics list that is success-rate-only — always include a cost/latency delta and at least one constraint-preservation or recoverability check, since success-rate alone is the documented blind spot in existing ad hoc A/Bs on this topic.
- Never recommend compaction/offloading/capping as a universal default, or recommend against it — community evidence on this topic directly contradicts itself (keep-everything vs. compact-by-default), so this skill stays neutral and only designs the measurement, never the conclusion.
- Never silently proceed with fewer than ~10 tasks or no pass/fail criteria without explicitly flagging the risk in the output's Risks & Caveats section.
- Never claim this skill executes the comparison, calls an agent CLI, or reads a live OTel/trace connector — if the user wants that, tell them this is a design-only skill and the execution step requires a separate script/harness or manual run.
