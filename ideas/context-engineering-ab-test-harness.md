# Does It Even Help: A Head-to-Head Empirical Harness for Context-Engineering Changes

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-13-context-engineering-memory.md · P4
- **Maturity verdict**: PARTIAL — Factory.ai published a context-compression evaluation methodology but never released it as an open, externally-runnable benchmark; a "tokdiet" proxy author ran a one-off 66-task A/B; an academic study tested five compaction strategies across frontier models on one fixed OpenCode scaffold. All are team-specific or non-reusable — no shared, adopted eval harness exists.
- **Format**: BOTH — the comparison-run harness is PROJECT-shaped (it must actually execute an agent twice against a task suite and collect metrics); reviewing a team's current context-engineering setup and drafting the A/B design (hypothesis, task sample, metrics) is a separable one-shot task.
- **Data Sources**: CONNECTED — drives the team's own agent framework/runtime directly (e.g. a CLI harness around Claude Code `-p`, Codex `exec`, LangGraph, or a generic OpenAI/Anthropic-compatible agent loop) to run the same task twice, once with and once without the proposed context-engineering change, and optionally pulls baseline cost/latency numbers from already-instrumented production traces (OTel/LangSmith/Langfuse) for calibration. These agent-CLI and OTel hook points already exist and are mature; no new connector needs to be built. The task suite itself is MANUAL — the team supplies 10-20 representative task prompts with pass/fail criteria, since no generic benchmark can substitute for a team's own workload.

## The Gap
The digest surfaces two directly contradicting sources: a fast.io guide recommending compaction/offloading as a default win, and a counterpoint practitioner finding that with prompt caching, "keeping everything is often cheaper, faster, and better at remembering than summarizing," with default compaction settings sometimes costing more than doing nothing. Fragmented prior art (Factory.ai's unreleased methodology, a 66-task proxy benchmark, one academic study pinned to a single scaffold) confirms real attempts exist, but no team-reusable, externally-runnable harness has been adopted — each team re-runs its own one-off A/B from scratch, if it runs one at all.

## The Project
A lightweight CLI harness that wraps a team's own agent framework and runs their own task suite twice — once with a proposed context-engineering change (compaction, tool-output capping, summarization threshold, offloading policy) active, once without — and reports task success rate, total tokens, and wall-clock latency for both runs side by side. The centerpiece is the comparison protocol itself: deterministic re-runs where feasible, paired statistical significance testing on noisy LLM outputs, and a standard report format so "does this help on MY workload" stops being answered by someone else's blog post.

Components: adapter layer for running a task suite against a pluggable agent target (Claude Code, Codex CLI, LangGraph, generic HTTP agent loop); a task-suite schema (prompt, setup, pass/fail check); a paired-run executor with configurable repeat count for noise averaging; a report generator (success-rate delta, cost delta, significance test); an optional OTel-trace importer for baseline calibration against real production cost.

## Tangible Impact
**Population**: Engineering teams running production or near-production agent systems who are deciding whether to adopt, keep, or disable a compaction/context-offloading strategy — directly the cohort represented by fast.io's guide readers and the counterpoint practitioner's audience, who today have no way to settle the "does this help or hurt for us" question except reading conflicting blog posts or running an ad hoc, throwaway test.
**Mechanism**: Today a team either defaults to whatever their framework ships (often a fixed compaction threshold) or copies a strategy from a blog post written against someone else's workload; a head-to-head harness run on the team's own task suite replaces that guess with a measured number specific to their agent, their tasks, and their cost structure, so a net-negative default gets caught before it ships rather than discovered as a vague sense that "the agent got worse."
**Measure**: (1) Task success-rate delta (with vs. without the change) across the team's own task suite, with a significance test given LLM output noise. (2) Cost/latency delta (total tokens, wall-clock time) for the same paired runs. (3) Adoption signal — how many teams run the harness before shipping a context-engineering change, versus the status quo of zero teams doing so found in the digest's search.

## Why Now
The digest's own 30-day window contains two mutually contradicting practitioner claims about the same default behavior (compaction), each argued from a different one-off measurement — this is exactly the moment a shared, reusable way to measure "does it help for you" becomes valuable, and today's agent CLIs (Claude Code, Codex) now expose the headless/scriptable hooks needed to drive repeatable comparison runs that didn't exist in a stable form a year ago.

## MVP Sketch
A Python CLI that takes a task-suite YAML (10-20 prompts + pass/fail checks), a target agent command template, and a context-engineering config toggle; runs each task N times with the toggle on and off via subprocess calls to the agent CLI, scores pass/fail with a cheap-model judge against the stated criteria, and prints a comparison table (success rate, tokens, latency, p-value). Experiment: validate the harness itself by reproducing the fast.io vs. counterpoint disagreement on a shared task suite and showing the harness correctly flags which claim holds for which workload shape. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- LLM output noise makes small success-rate deltas hard to trust without enough repeat runs, which directly raises the harness's own token cost — the tool that measures cost efficiency could itself be expensive to run well.
- A team's 10-20 manually-curated tasks may not represent their real production task distribution, so a "passes the harness" result could still mislead if the suite is unrepresentative.
- Any framework vendor (Anthropic, LangChain) could ship this kind of before/after comparison natively inside their own CLI, which would commoditize the adapter layer quickly.
- The academic study found compaction usually doesn't hurt *measured* scores but misses constraint-preservation failures (see this digest's P3) — a harness that only tracks success rate and cost could still miss that specific failure class unless its pass/fail checks are written to catch it.
