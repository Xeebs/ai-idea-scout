# Agent Execution-State Store ("Postgres for reasoning runs")

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-06-10-agentic-ai-autonomous-agents.md · P1
- **Maturity verdict**: PARTIAL — Adjacent durable-execution engines are mature (conductor-oss/conductor 31.9k★, rivet-dev/rivet 5.6k★, dbos-inc, TanStack/workflow) and LangGraph Postgres checkpointers cover resume, but they treat runs as workflows, not queryable branching-reasoning objects. Purpose-built "agent-state DB" attempts on GitHub are tiny (luminarydearx/Plasma-Agent 1★, aicubetechnology/qilbeeDB 20★, stale), so the specific store remains unexecuted.
- **Format**: PROJECT — the value is a persisted, queryable store; nothing here is a one-shot prompt task.

## The Gap
Builders on r/AI_Agents (2026-06-06, "Standard databases are breaking my AI agents") report hitting a wall with state management: everyone bolts agent execution state onto Redis, NoSQL, or flat files behind a vector DB, none of which model branching reasoning loops, checkpoints, or step-level debuggability. An adjacent HN thread ("Multi-Agent is a snake oil") argues orchestration gets all the attention while state handling stays unsolved. Durable-execution engines persist *workflows*; nothing treats an agent run as a first-class, queryable, resumable object.

## The Project
A storage layer — likely a Postgres extension plus schema and thin SDK rather than a new database engine — where the core entity is the **run**: a tree of steps (LLM call, tool call, decision branch) with full inputs/outputs, token costs, and checkpoint snapshots. The novel pattern is queryability over reasoning structure: `SELECT` all runs that branched at a given decision node, diff two branches of the same run, resume any run from any checkpoint, and garbage-collect dead branches by policy. Adapters for LangGraph and CrewAI replace their default checkpointers so adoption is a config change, not a rewrite.

Components: run/step/branch schema + Postgres extension functions; checkpoint/resume API; LangGraph + CrewAI checkpointer adapters; a query CLI ("show me every run that failed after step type X").

## Tangible Impact
**Population**: On-call and platform engineers maintaining production agents built on LangGraph/CrewAI — LangChain's State of AI Agents survey (1,300+ professionals, Dec 2024) found ~51% of respondents' companies already run agents in production, and CrewAI claims 100k+ certified developers; the directly affected group is plausibly the low tens of thousands of engineers who carry pagers for these systems.
**Mechanism**: Today a failed multi-step run means grepping logs across Redis keys and flat files to reconstruct what the agent was thinking; the store makes the run itself the queryable artifact, so diagnosis becomes a query and recovery becomes a checkpoint resume instead of a full re-run (with its token bill).
**Measure**: (1) Median time-to-diagnose a failed production run drops from hours of log archaeology to <10 minutes of querying, measured in pilot teams. (2) Tokens spent on re-running failed jobs drop ≥50% via checkpoint resume. (3) ≥3 pilot teams replace their Redis/flat-file state layer in the 90 days after MVP.

## Why Now
The source thread is from 2026-06-06 and frames the duct-tape as universal; durable-execution engines all pushed releases in June 2026, proving demand for run persistence, while leaving the reasoning-as-data niche open. LangGraph's checkpointer interface makes drop-in adoption feasible today — no model-capability prerequisite.

## MVP Sketch
A Postgres schema + Python SDK implementing the LangGraph checkpointer interface, recording the full step tree, plus five canned queries (failed-branch listing, run diff, cost rollup, resume, branch GC). Stack: Postgres, SQLAlchemy, a 200-line LangGraph adapter. Experiment: take one real flaky agent from a pilot team, and show a failure diagnosed by query in minutes that previously took a log-spelunking session — if querying run structure isn't visibly faster than logs, kill it. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- LangChain could ship richer queryable run storage in LangGraph Platform and absorb the niche overnight — the strongest already-solved risk.
- Observability vendors (LangSmith, Braintrust) store traces; the bet that teams want this *in their own Postgres* as operational state, not vendor telemetry, is unproven.
- Branching-reasoning schemas may be too framework-specific to generalize across LangGraph and CrewAI.
- One Reddit thread plus one HN aside is thin demand evidence; pilot interviews must precede heavy build-out.
