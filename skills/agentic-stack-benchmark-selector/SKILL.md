---
name: agentic-stack-benchmark-selector
description: Builds a scenario-specific, evidence-cited decision record for picking an agentic framework/SDK (LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, Microsoft Agent Framework, etc.) tied to a team's own task and constraints, instead of a generic popularity listicle. Use when someone asks "which agent framework should we use", is mid-bake-off between 2+ frameworks, or is about to pick a stack for a new agent project.
---

# Agentic Stack Benchmark Selector

## When to use this
Someone is choosing a framework/model/tool-calling stack for a new or existing agent project and says something like "should we use LangGraph or CrewAI", "what agent framework fits our use case", or is about to start a multi-week informal bake-off between frameworks. Use this before they pick based on a blog listicle, a Reddit/HN opinion thread, or whichever framework a teammate happened to use last.

Do not use this for picking a base LLM/model (that's a separate decision), and do not use it for choosing among orchestration *patterns* (hierarchical vs. peer-to-peer) within a framework already chosen — that's a narrower, different decision.

## Inputs
**Data source**: Connected — the parent idea for this skill describes it as reading from a dedicated project's own published, continuously-updated benchmark-results dataset (a harness that runs a team's task scenarios against each framework's live SDK and measures real setup time, token cost, and task success/latency). **That connector does not exist yet** — the benchmark-running project is a separate, unbuilt piece of infrastructure, not something this skill can query today. Until it ships, this skill runs as a standalone advisory and requires, manually from the user:

1. **1–3 representative task scenarios** in plain language (e.g., "a support-ticket triage agent that reads an inbox, classifies urgency, and either auto-replies or escalates to a human queue" — not "an agent that does stuff").
2. **Hard constraints**, ranked if possible: latency budget, expected tool/step count, self-hosting or data-residency requirement, existing language/runtime (Python-only shop? TypeScript?), team size/experience with agent frameworks, and any model vendor lock-in already decided.
3. Optionally, a candidate list to restrict to (default candidate set if omitted: LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, Microsoft Agent Framework).

If scenario or constraints are missing, stop and ask for them — never substitute a generic placeholder scenario.

## Procedure
1. **Confirm inputs.** Restate the scenario(s) and constraints back to the user in one short paragraph before proceeding, so a vague ask gets sharpened first.
2. **Set the candidate list** — the default five unless the user restricted it, dropping any candidate that's flatly incompatible with a hard constraint (e.g., drop a cloud-only SDK if self-hosting is mandatory) and saying why it was dropped.
3. **For each remaining candidate, run a targeted search** (web search tool, or the user's own knowledge of recent docs/changelogs if no search tool is available) for evidence specific to what the scenario(s) demand: state/workflow management fit, multi-step tool-calling reliability, multi-agent coordination support if the scenario needs it, deployment/self-hosting story, current maturity (GA vs. beta vs. unmaintained), and any dated, credible comparison or migration-pain report. Every claim used in scoring must trace to a specific, dated source (docs page, changelog, GitHub repo activity, a named comparison article) — not general reputation.
4. **Score each candidate per scenario** on a 1–5 fit scale against the user's ranked constraints, with a one-line justification per score citing the evidence from step 3. If two candidates tie, say so rather than forcing a false tiebreak.
5. **Flag evidence gaps** explicitly: if a candidate has thin, old (>9 months for a fast-moving framework), or conflicting evidence for a given scenario, mark that score low-confidence rather than presenting it with the same certainty as a well-evidenced score.
6. **Pick a primary recommendation and a runner-up**, stating the single constraint that would flip the pick to the runner-up (e.g., "if self-hosting becomes mandatory, switch to X").
7. **Name the biggest risk** of the recommended pick for this specific scenario (lock-in, immaturity, team learning curve) — never present a pick as risk-free.
8. **Close with a re-evaluation trigger**: a concrete event (framework reaches GA, team scenario changes, a named upcoming migration) that should cause the user to re-run this process rather than treating today's pick as permanent.

## Output format
A single markdown "Stack Decision Record" with these sections, in order:
1. **Scenarios & Constraints Captured** — the confirmed restatement from step 1.
2. **Candidates Considered** — list, with any dropped candidates and the one-line reason.
3. **Scoring Matrix** — a table: rows = candidates, columns = each scenario, cells = score (1–5) + one-line evidence citation (source name/date). A final column = constraint-weighted total.
4. **Recommendation** — primary pick, one paragraph tying it to the scenario and constraints, plus the runner-up and its trigger condition.
5. **Biggest Risk** — 1–2 sentences, specific to this pick and this team's scenario, not generic.
6. **Confidence & Staleness Notes** — which scores are low-confidence and why.
7. **Re-evaluation Trigger** — the concrete event that should prompt redoing this process.

## Guardrails
- Never invent a benchmark number (token cost, latency, success rate) as if it came from a measured test run — no such run happened in this skill. Every score is evidence-assisted judgment; label it that way explicitly in the output's header line (e.g., "Heuristic, evidence-cited scoring — not a measured benchmark run").
- Never recommend a framework without at least one scenario-specific piece of dated evidence per surviving candidate. A generic "X is popular/well-documented" is not evidence.
- Never silently substitute a generic example scenario when the user hasn't supplied one — stop and ask instead.
- Never pad or guess a score for a candidate when the search in step 3 turned up nothing relevant — mark it "insufficient evidence" rather than inventing a plausible-sounding number.
- Never present the output as permanent — the re-evaluation trigger is mandatory, not optional, because every candidate framework is actively evolving.
- Never drop a user-specified constraint silently; if a constraint can't be evaluated from available evidence, say so in the Confidence section rather than quietly ignoring it.
