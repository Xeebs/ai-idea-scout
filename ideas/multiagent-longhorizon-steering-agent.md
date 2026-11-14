# Course Correct: A Steering-Agent Middleware for Long-Horizon Goal Drift

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-14-multi-agent-architectures.md · P10
- **Maturity verdict**: PARTIAL (tie-break from OPEN per methodology) — The primary source, "Learning to Steer LLM Agents and Multi-Agent Systems" (arXiv 2610.22316), matches this pattern closely: an RL-trained supervisory steering agent with fast/slow intervention paths, evaluated on information-seeking search tasks. `gh search repos` found no public code/repo for it. A cluster of adjacent 2026 papers (DriCo coordination-drift framework, "Inherited Goal Drift," "The Horizon Gap") confirms this is an active research area, but no deployed product, benchmark adoption, or open-source implementation exists.
- **Format**: BOTH — the live supervisory monitoring-and-intervention layer is PROJECT-shaped infrastructure; reviewing an already-captured long-horizon run transcript for drift points is a separable one-shot analysis task.
- **Data Sources**: CONNECTED (project) — reads the running agent team's live tool-call and trace stream via the team's own existing instrumentation (the same OTel GenAI span substrate other ideas in this ledger read); this capture layer already exists maturely, this project adds the drift-monitoring-and-intervention logic on top. MANUAL (skill) — user pastes a transcript/log excerpt of a completed long-horizon run for drift-point review.

## The Gap
An October 2026 weekly AI-agent news roundup (aiagentstore.ai) cites "a steering-agent design that intervenes to prevent goal drift on long tasks... learns when and how to intervene (fast vs slow paths)" as improving long-horizon tool-using multi-agent runs, alongside a separately cited framework (ARIA) for repairing failed multi-agent runs at runtime. Tracing the primary source confirms a real research result — an RL-trained supervisory agent that chooses between cheap fast corrections and deeper slow re-planning to counter goal drift accumulating over long-horizon runs — but no public code, deployed product, or adopted benchmark exists for it; this remains an active research direction with zero accessible implementation.

## The Project
A steering-agent middleware that sits above a long-running multi-agent task and monitors the live tool-call/trace stream for signs of goal drift — the task's trajectory diverging from its original objective without anyone noticing because no single step looks obviously wrong. On detecting drift, it chooses between a fast, cheap intervention (a corrective prompt injected into the next step) and a slower, deeper intervention (triggering a full re-planning pass), rather than letting drift accumulate silently or over-correcting on every minor wobble. Unlike the source paper's RL-trained policy, the initial build uses a lighter heuristic-plus-learned-classifier approach so teams get the same corrective capability without first training their own steering policy from scratch.

Components: a drift-detection signal computed per step (task-relevance scoring against the original stated goal); a two-tier intervention policy (fast prompt-nudge vs. slow re-plan trigger) gated by drift severity and accumulated drift history; an intervention log so teams can audit when and why the system intervened; a pluggable hook for swapping the heuristic classifier for a trained RL policy later, following the source paper's design once reproduced.

## Tangible Impact
**Population**: Teams running long-horizon, tool-using multi-agent tasks — multi-day coding agents, autonomous research agents, long-running ops/support agent chains — a population distinct from the short single-exchange multi-agent populations this ledger's other ideas target (majority-vote verifiers, single-handoff tracers), specifically those whose tasks run long enough for incremental goal drift to accumulate unnoticed.
**Mechanism**: Today nothing watches a long-horizon run for incremental goal drift and distinguishes a quick nudge from a deep re-plan — drift accumulates silently until the run completes having missed its original objective, or a human notices mid-run and intervenes manually. A steering middleware catches drift earlier and routes to the cheapest sufficient correction, reducing both wasted compute on over-corrected minor wobbles and wasted runs that complete but miss the goal.
**Measure**: (1) task success rate on long-horizon benchmark tasks, measured as "completed the originally stated goal" rather than just "completed without crashing," before vs. after adding the steering layer; (2) frequency and relative cost of fast vs. slow interventions triggered per run; (3) reduction in runs that complete but are later judged to have drifted from the original goal, on a held-out evaluation set.

## Why Now
arXiv 2610.22316 demonstrated the fast/slow steering approach's feasibility on information-seeking tasks within the research window this digest covers, proving the pattern is tractable with current models and training techniques — but published with no code, leaving an open window for an accessible, lighter-weight implementation before anyone productizes the original RL-trained design.

## Skill Angle
Given a pasted transcript/log excerpt of a completed long-horizon agent run and its original stated goal, flag the specific steps where the trajectory measurably diverged from that goal, classify each flagged point as likely needing a fast nudge or a deeper re-plan had it been caught live, and note the evidence (specific actions/outputs) supporting each flag. Useful as a retrospective review before any live monitoring infrastructure is built.

## MVP Sketch
Implement a heuristic task-relevance drift scorer (e.g., periodic LLM-judged relevance-to-goal check, kept cheap and infrequent to avoid reintroducing judge-cost/bias problems) plus a simple severity-gated fast/slow intervention trigger; test on a long-horizon task suite (e.g., a multi-step research-task benchmark), comparing original-goal-completion rate with and without the steering layer. 3–4 weeks for 1–2 people, starting with the heuristic version and treating RL-policy training as a later upgrade, not part of the MVP.

## Risks & Open Questions
- The primary research prototype has no public code — reproducing its fast/slow mechanism from the paper's description alone risks missing design details that matter for real performance.
- Evaluated only on information-seeking tasks in the source paper; generalization to coding, ops, or other long-horizon task types is unproven and must be tested directly, not assumed.
- A periodic relevance-check drift detector risks becoming "yet another LLM judge," reintroducing the cost and calibration-bias problems this repo's own judge-calibration ideas already flag — the detector must be designed to run rarely/cheaply, not as a per-step judge call.
- Distinguishing genuine harmful goal drift from legitimate, correct plan evolution (the agent appropriately updating its approach based on new information mid-task) is a hard classification problem the project must solve convincingly, or it risks over-intervening on correct behavior.
