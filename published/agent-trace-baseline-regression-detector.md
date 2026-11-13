Agents don't usually fail loudly. A tool starts retrying a little more than it used to. Answers get a little longer, a little more expensive. Nobody's error dashboard moves, because nothing is actually erroring — it's just quietly worse. By the time a user complains, the regression has been live for days, and nobody can say which deploy caused it.

## The Gap

On 2026-10-29, a Show HN post titled "Apgar – Catch agent regressions without an LLM judge" (github.com/oimo-ai/apgar) described exactly this problem: diff production-trace metrics — tool-error rate, retry/loop counts, call volume, answer length, cost, latency — between a release and its prior baseline, and flag the drift deterministically, with zero LLM calls in the detection path. The post itself only pulled 3 points, and the repo sits at 9 stars, 2 forks, single maintainer. That's not nothing, but it's not an adopted standard either.

It's also not a one-off complaint. Two days earlier in the same research window, a second, independent digest pass turned up the same argument surfacing twice more: an existing open-source project called EvalView running deterministic regression checks against golden baselines (with LLM-as-judge demoted to an optional add-on, not the primary signal), and a blog post at agentdbg-web.pages.dev — "Why your agent needs a regression gate" — making the identical anti-LLM-judge case independently. Three unconnected sources, converging on the same shape of answer, and still nothing that's actually maintained and adopted at scale. A broader GitHub sweep for "agent regression testing" turns up a long tail of small, fragmented attempts — Trajectly (now archived), agentest, agent-ci, ai-eval-forge — and a June 2026 arXiv paper proposing a layered, LLM-free testing framework. Every one of them treats this as a side project or a research sketch, not infrastructure a team can depend on.

That's the actual gap: not "has anyone thought of this" — multiple people clearly have — but "has anyone built and maintained the thing," and the honest answer right now is no.

## The Project

A baseline-diff service, not a one-shot script. It ingests OTel- or Langfuse-tagged spans per release version, snapshots five or six core metrics per release window — tool-error rate, retry/loop counts, call volume, answer length, cost, latency — and runs a statistical drift check (CUSUM or a z-score test) against the trailing baseline. Nothing in the detection path calls an LLM. When a metric breaches its threshold, it posts a concrete, named report — "release N regressed tool-error rate by 34% versus baseline" — to the team's alert channel, instead of waiting for a support ticket to do the detecting for you.

The pieces are deliberately small: an OTel-compatible span ingester, a per-release metric snapshotter, the drift-detection engine itself, an alert/report formatter, and a lightweight dashboard for eyeballing release N against release N-1. None of this requires a model capability that didn't exist six months ago — it requires someone to actually finish building and maintaining it, which is the part every prior attempt stopped short of.

## Tangible Impact

**Population**: Engineering teams operating production LLM agents that ship prompt or model changes at least weekly without a dedicated eval engineer — per LangChain's State of AI Agents survey (1,300+ professionals, Dec 2024), roughly 51% of respondent companies already run agents in production; the realistic target is the thousands of teams, mostly under ~50 engineers, that are past that adoption curve but haven't yet built their own eval tooling.

**Mechanism**: Today a quiet regression has no alert path at all — it surfaces only when a user complains or a support ticket lands, often days later. A deploy-triggered baseline diff turns that into a same-day, named-metric report: on-call gets a concrete signal instead of a vibe, and the team gets a rollback trigger before user impact compounds.

**Measure**: median time from deploy to regression detection dropping from days (user complaint) to under 2 hours on pilot teams; the share of "silent" regressions — no crash, no error-rate spike — caught before user impact, rising from near-zero to a majority; and the number of rollback decisions per month backed by an actual metric-diff report rather than anecdote, tracked per pilot team.

## Why Now

OTel's GenAI semantic conventions and tracing backends like Langfuse matured enough in 2026 that per-span metrics — tool-error rate, retry counts — are available without bespoke instrumentation. Apgar's own emergence on 2026-10-29 is proof the pattern is tractable with today's tooling; nothing about this waits on a future model capability, only on someone building the maintained version.

## Risks & Open Questions

- Apgar, EvalView, or one of the fragmented GitHub attempts could mature quickly and absorb this niche — direct early-stage competitors already exist, not hypothetical ones.
- Picking drift thresholds that avoid alert fatigue on noisy, low-volume services is genuinely unsolved, and could kill adoption on its own regardless of how good the detection math is.
- Teams without release-tagged traces can't use this without an instrumentation pass first — that's a real adoption tax, not a footnote.
- This sits right next to golden-eval-set drift detection: this project is judge-free and deploy-triggered, that one is traffic-vs-eval-set and periodic. Worth confirming in practice they stay genuinely distinct products rather than converging into the same tool with two names.

Surfaced from `research/2026-11-11-llm-evaluation-observability.md`, pattern `P1` — corroborated by a second, independent research pass in `research/2026-11-13-llm-evaluation-observability.md`, pattern `P2`.
