# Promote: One-Click Trace-to-Regression-Eval Promotion

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-14-llm-evaluation-observability.md · P1
- **Maturity verdict**: PARTIAL — PostHog's own `posthog/posthog` PR tried to nudge agents reading traces toward setting up an eval and "can't land" due to a prior regression removing MCP discovery-hint footers; a cluster of 0-star hobby repos (`wwb-bill/trace-to-eval`, `r-bug-r/trace-to-eval`, `AthenaTheOwl/trace-to-eval-harness`, `a-bhimava/agent-trace-to-evals`, Jul–Oct 2026) attack exactly this but are one-off and unmaintained; Confident AI auto-curates traces into eval datasets and Langfuse/LangSmith support linking a trace to a dataset example manually, but none offer the automatic "offer to promote while reading a trace" loop.
- **Format**: BOTH — the always-on promotion-prompt middleware is persistent infrastructure; reviewing one pasted failing trace and drafting a candidate eval case from it is a separable one-off task.
- **Data Sources**: CONNECTED — reads traces directly from the team's existing observability backend via its own API or MCP server (PostHog MCP, Langfuse's REST API, or LangSmith's SDK — all mature, already-shipped connectors) and writes the promoted case into the same backend's existing eval/dataset store through the same connector, so nothing is pasted that the tool could read itself.

## The Gap
PostHog's engineers noted "coding agents read a lot of LLM traces through the PostHog MCP, but rarely go on to set up an online evaluation for what they find" — and even PostHog itself couldn't land the fix due to an internal regression. An industry-wide stat cited in the same search ("89% of teams have agent observability instrumented, but only 52% run offline evaluations") shows this isn't one team's gap: a ~37-point drop-off between watching traces and converting findings into regression tests, with only unmaintained 0-star repos attempting automation.

## The Project
A middleware layer that sits on the read path of an existing trace viewer or MCP trace tool: whenever a trace is flagged, annotated, or marked as a failure by a human or an agent reading it, the layer offers (via the same UI or MCP response) to promote that exact trace — inputs, outputs, and the specific failure annotation — into a saved regression-eval case in the team's existing eval dataset, pre-filled with a draft assertion derived from the annotation. One click (or one MCP tool call) turns "I noticed this failed" into "this is now a test that runs every release," closing the 37-point gap PostHog's own stat names.

Components: a backend-agnostic "promote" adapter (PostHog, Langfuse, LangSmith to start); an annotation-to-assertion drafter that proposes a check type (exact match, judge-based, structural) from the failure note; a dedupe check against existing eval cases to avoid redundant promotions; a lightweight dashboard showing promotion rate over time per team.

## Tangible Impact
**Population**: Engineering teams running production LLM agents who already instrument observability (the cited 89%) but don't yet run systematic offline evals (the cited 52% gap) — concretely, the ~37% of instrumented teams stuck in "trace read once and discarded" mode, spanning any team using PostHog, Langfuse, or LangSmith today.
**Mechanism**: Today, a found failure requires a separate manual workflow (open the dataset UI, copy inputs/outputs, write an assertion) that competes with the next task, so most findings are never converted — the observed drop-off. A one-click promotion collapses that workflow to the moment the failure is already in front of someone, converting observation into regression coverage before the context is lost.
**Measure**: (1) promotion rate — fraction of flagged/annotated failing traces that become saved eval cases, before vs. after adoption, target moving materially above the industry's implied ~15% (52/89... treat directionally) baseline; (2) regression-catch rate — fraction of promoted cases that later fail again on a subsequent deploy, catching a real recurrence; (3) median time from "trace flagged" to "eval case exists," target under 2 minutes vs. today's open-ended manual gap.

## Why Now
PostHog's own November 2026 attempt proves demand is live inside at least one major vendor's roadmap right now, and MCP has matured into the standard way agents and engineers already read traces — meaning the promotion hook can be built as an MCP tool response addition rather than a new UI, making this newly cheap to ship without waiting on any vendor's own fix.

## Skill Angle
Trigger: an engineer pastes a specific failing trace (or the agent surfaces one via MCP) and says "this should be a test." Inputs: the trace's input/output pair and a short note on what went wrong. Output: a drafted eval case — assertion type, expected behavior, and a suggested dataset name/tag — formatted to paste directly into the team's eval tool (Langfuse, LangSmith, Confident AI, or a plain YAML/JSON eval-case format if none specified). This is the one-shot drafting task; the project is the always-on, backend-wired promotion loop that fires automatically on annotation.

## MVP Sketch
Build the Langfuse adapter only: a small service polling Langfuse's annotation-queue API for newly-flagged traces, drafting a candidate eval case via an LLM call, and writing it into a designated Langfuse dataset via the API. Experiment: seed 20 real or synthetic flagged traces, measure how many produce a usable draft eval case requiring only minor human edit vs. a rewrite from scratch. 2–3 weeks, 1 person.

## Risks & Open Questions
- Drafted assertions from a failure annotation alone may be too loose (overfit to one trace) or too strict (fail on benign variance) — needs a human-edit step before any case runs in CI, not blind auto-acceptance.
- PostHog's own stalled PR suggests platform-side integration points can be fragile/moving targets, so backend API stability is a real maintenance risk.
- If PostHog successfully lands its own native version soon, this project's differentiation narrows to cross-backend portability (Langfuse/LangSmith) rather than being first.
- Dedupe against near-identical existing eval cases needs real design — a naive promote-everything flow would bloat the eval suite's runtime without adding coverage.
