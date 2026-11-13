# Promote Gate: A Packaged Shadow-Test → Canary-Rollout Orchestrator for Prompt and Model Changes

Every team shipping a production LLM feature eventually learns the same lesson the hard way: a prompt tweak that looks fine in a quick manual check can quietly tank answer quality for a slice of real users, and by the time anyone notices, it's already live. The fix — shadow-test the candidate against real traffic before anyone sees it, then canary a small slice, then promote — is well known. What's missing is a tool that actually does it.

## The Gap

One practitioner, writing at tianpan.co, has published at least four separate 2026 posts walking through the identical three-stage playbook: Offline Eval → Shadow Test → Canary Rollout. Each post re-explains, from scratch, why generic feature-flag or canary infrastructure doesn't transfer cleanly to LLM changes — an LLM rollout needs prompt-and-model version pairing on every logged event and a judge-based quality comparison, not just an error-rate threshold. A vendor post at featbit.co arrives at the same three-stage framing independently, with no coordination between the two sources. That's two separate threads converging on the same conclusion: this is advice everyone keeps re-explaining, not a tool anyone has shipped.

It's not that nobody has tried to solve adjacent problems. LaunchDarkly's AI Configs ships "Online Evaluations" — judge-scored accuracy/relevance/toxicity checks feeding guarded rollouts — and Statsig has an "AI Evals" product doing prompt/model versioning with automated grading. Both are real, shipped features from well-resourced vendors. But both are explicitly beta or early-access, with conflicting availability claims even within their own docs (Statsig stopped accepting new beta customers as of June 2026; LaunchDarkly's own pages describe the same feature as both "closed beta" and "early access"). Neither documents a native shadow-mode feature specifically — generating a candidate's output against real traffic without ever serving it. A GitHub search for shadow or canary LLM rollout tooling came back empty except for a zero-star simulator repo. The playbook is public and repeated; the packaged version of it isn't.

## The Project

The orchestrator sits in front of a team's existing LLM gateway and automates the three stages end to end. First, it runs an offline eval on the candidate prompt or model version against a held-out set, before anything touches live traffic. Second, it shadow-tests the candidate: a configurable sample rate of real production requests gets duplicated and routed to the candidate, which generates output that is scored by a judge against the currently-live version's output on the same inputs — but that output never reaches a real user. Third, once the shadow comparison clears a configured threshold, it promotes the candidate to a small canary traffic slice, with automatic rollback if canary metrics regress. Every event, in every stage, is tagged with the exact prompt-and-model version pair that produced it, so an audit or a rollback always has an unambiguous target to point at.

The pieces: a gateway-layer traffic duplicator for shadow mode with zero user-facing latency or cost impact, a judge-based shadow-comparison scorer, a configurable promote/rollback threshold engine, a version-pairing event tagger, and a dashboard showing a rollout's current stage and live comparison scores. It's designed to sit on top of infrastructure that already exists and is already widely adopted — an LLM gateway proxy like LiteLLM for the traffic duplication, and an observability/eval backend like Langfuse (or a custom judge call) for the comparison scoring — rather than asking a team to stand up new infrastructure just to get a safety net.

## Tangible Impact

**Population**: Engineering teams shipping prompt or model version changes to a production LLM feature at least weekly without a dedicated platform/SRE team to hand-build rollout safety tooling — the same audience the tianpan.co posts are written for (a practitioner repeatedly hitting this at real companies), realistically overlapping heavily with the "teams past the prototype stage, before building in-house eval tooling" population from LangChain's 2024 survey (~51% of surveyed companies running agents in production).

**Mechanism**: Today, safely rolling out a prompt/model change means either manually wiring shadow traffic duplication and judge comparison from scratch each time (the exact repeated advice tianpan.co keeps re-explaining), or skipping the safety step and canarying blind with only generic error-rate monitoring that doesn't catch a quality regression a judge would. The orchestrator turns a from-scratch manual playbook into a repeatable, configured pipeline, so a prompt change that would silently degrade answer quality gets caught in shadow mode before any real user sees it, instead of after a canary slice already did.

**Measure**: (1) percentage of prompt/model changes that go through shadow testing before any live traffic exposure, from the current largely-skipped baseline to a majority on pilot teams; (2) number of regressions caught in shadow mode versus discovered post-canary or post-full-rollout, on a pilot team's rollout history; (3) time to safely roll out a prompt/model change end-to-end (offline eval through full promotion), compared against the hand-wired baseline tianpan.co's posts describe.

## Try It

A companion Claude Code skill, `skills/llm-shadow-canary-rollout-orchestrator/`, already exists: **"Drafts a shadow-test-then-canary rollout plan (sample rate, duration, judge-comparison gate, canary ramp, rollback triggers) for a specific prompt or model version change before it ships to production."** It's the planning half of this idea, not the running orchestrator — it takes your described change, traffic volume, and feature context and hands back a concrete, numbered rollout plan (risk tier, shadow sample size with the arithmetic shown, judge-comparison gate, canary ramp schedule, rollback triggers), rather than running anything itself.

To use it: either paste the `README.md` from that folder into any AI chat tool along with your change details, or — if you use Claude Code — drop the whole `llm-shadow-canary-rollout-orchestrator/` folder into `~/.claude/skills/` so Claude reaches for it automatically the next time you describe a prompt or model change you're about to ship.

Worth knowing going in: the plan the skill produces leans on an LLM judge to gate promotion, and that judge inherits the known reliability issues of LLM-as-judge comparisons — position bias, format sensitivity — so the skill builds in a mandatory judge-reliability caveat and recommends a human spot-check of judge verdicts for higher-risk changes. It's a safety net with a known soft spot, not an infallible gate.

---

Surfaced from `research/2026-11-12-llm-evaluation-observability-ii.md`, pattern `P8`.
