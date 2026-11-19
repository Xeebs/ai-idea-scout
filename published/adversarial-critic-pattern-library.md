# Critique Mode: A Benchmarked, Reusable Adversarial Producer-Critic Pattern Library

Every multi-agent framework ships a happy-path assumption: agents cooperate. One plans, one writes, one reviews, everyone's pulling the same direction. But plenty of builders have quietly found that making one of those agents *adversarial* — explicitly trying to find what's wrong with the output rather than help finish it — catches more. Nobody's packaged that as a thing you can just turn on and measure. It's a pattern everyone seems to be hand-rolling, alone, from scratch, every time.

## The Gap

The clearest tell is small but telling: a post on r/AI_Agents (thread `1hsnbgf`, "building complex multi-agent systems") describes a builder running two parallel multi-agent systems side by side — one collaborative, one adversarial — and asking the community what others were experimenting with. That's not someone pointing at an existing tool. That's someone running their own private experiment because there wasn't an off-the-shelf way to do it, and wondering out loud if anyone else had solved this better.

They probably hadn't, or at least not in a form anyone could hand them. A broader search turns up real pieces of this pattern, just never assembled: Anthropic has documented a generator/evaluator (GAN-inspired) building block as a reasoning pattern, and there's an academic paper (AdversarialMAS) formalizing generator/critic/revision agents as a structure. On the implementation side, `dsifry/metaswarm` — a maintained, 430-star orchestration framework — includes adversarial review, but buried as one of eighteen agents in a general-purpose system, not something you reach for on its own. `ejentum/agent-teams` tried a narrower, dedicated version, picked up 11 stars, and hasn't been pushed since May 2026. A GitHub search for the exact pattern by name came back empty.

So the honest read — and the one the gap analysis actually landed on — is PARTIAL, not OPEN. This isn't virgin territory. Real implementations exist. They're just fragmented, narrow, or welded into something much bigger than the pattern itself. That's the gap: not "nobody's built this" but "nobody's offered it as a dedicated, benchmarked, selectable mode you can drop into whatever framework you're already using."

## The Project

Critique Mode is a framework-agnostic library implementing the producer → critic → revise loop as a first-class, configurable mode you select — not a feature you inherit by buying into an eighteen-agent framework. It ships adapters for the orchestration tools people are already using (LangGraph, CrewAI, the OpenAI Agents SDK), configurable critic personas and adversarial-intensity levels, and — this is the part that doesn't exist anywhere yet — a shared benchmark comparing adversarial-mode pipelines against collaborative-only pipelines on the same tasks, measuring defect/error catch rate against what it actually costs you in tokens, latency, and extra rounds.

That benchmark is the centerpiece, not an afterthought. The r/AI_Agents post wasn't really asking "does adversarial work" — it was asking "is it worth it, and compared to what." Right now the honest answer is "nobody knows, go measure it yourself." Critique Mode turns that into a reusable, swappable mode with empirical catch-rate-vs-cost numbers already attached, instead of every team quietly running the same experiment in isolation.

Components: a composable producer/critic/revise node portable across major orchestration frameworks; configurable critic aggressiveness and persona; a shared benchmark task set (code review with known injected bugs, content fact-checking with known planted errors) with catch-rate and cost instrumentation built in from day one.

## Tangible Impact

**Population**: Small teams building multi-agent content, code, or decision pipelines who are weighing whether to add an adversarial review stage — the builder behind the cited r/AI_Agents post, plus the broader population already hand-rolling or inheriting this pattern ad hoc, represented by metaswarm's 430 stars (adversarial review buried in a general framework) and agent-teams' 11 stars (a narrow, now-stale standalone attempt).
**Mechanism**: Today, adding an adversarial critic stage means either hand-rolling the producer/critic/revise loop from scratch per project, or inheriting it as a non-removable feature buried inside a much larger general-purpose framework. A dedicated, benchmarked library turns "should we add adversarial review and is it worth the extra cost" from a one-off experiment into a reusable, swappable mode with empirical catch-rate-vs-cost numbers attached.
**Measure**: (1) Defect/error catch rate of adversarial mode vs. collaborative-only mode on the shared benchmark task set. (2) Added cost (tokens, latency, extra LLM calls) per additional defect caught, so teams can compute their own breakeven point. (3) Number of teams switching from a hand-rolled adversarial loop to the library within a pilot window.

## Try It

A companion skill, `skills/adversarial-critic-pattern-library/`, already exists — and it's deliberately scoped narrower than the full runtime library above. Per its `SKILL.md`: "One-shot design aid that decides whether a described agent pipeline should add an adversarial producer-critic-revise stage, picks how aggressive it should be, and drafts the critic agent's persona and prompt — for someone weighing whether to bolt adversarial review onto a pipeline they already have, before building or adopting any runtime library for it."

In practice: describe your pipeline (what it produces, its current stages, what's at stake if a bad output slips through, and whether a human already reviews everything), and it walks through a stakes/complexity classification, recommends ADD / DON'T ADD / ADD WITH GATING, picks an aggressiveness level, and drafts a ready-to-use critic-agent system prompt — severity scale, calibration guardrail, and termination condition included. It explicitly refuses to invent a catch-rate number; that part still has to come from running the benchmark above on your own data.

To use it: either paste the `README.md` into any AI chat tool (ChatGPT, Claude, Copilot) and describe your pipeline directly in the conversation, or — if you're running Claude Code — drop the `adversarial-critic-pattern-library/` folder into `~/.claude/skills/` and it activates automatically the next time you ask something like "should we add an adversarial review stage to this."

One honest caveat, straight from the idea file's own risk list: `dsifry/metaswarm` could extract its adversarial-review agent into its own standalone, dedicated mode at any point and absorb this niche outright — it already has the stars and the maintenance momentum to do it. And the core bet — that a generic framework-level pattern beats one well-written critic prompt — is itself an open question the benchmark is designed to actually answer, not assume.

Surfaced from `research/2026-11-12-multi-agent-architectures.md`, pattern `P3`.
