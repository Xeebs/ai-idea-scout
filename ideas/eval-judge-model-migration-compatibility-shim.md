# Judge Swap: A Compatibility Shim for Migrating Eval Frameworks Between LLM-as-Judge Models

- **Status**: EXPLORING (promoted 2026-11-13 cycle 57: evidence density — ≥2 independent threads, PostHog's live GitHub PR #133640 corroborated independently by tianpan.co's "The Eval Harness Whose Judge Model Was Upgraded Silently" and "Model Migration Bills You Twice," all describing the same judge-model-swap compatibility gap)
- **Date**: 2026-11-13
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-13-llm-evaluation-observability.md · P6
- **Maturity verdict**: PARTIAL — WebSearch found only reactive, narrow fixes and advice, not a general solution: PostHog's own PR (`PostHog/posthog#133640`) patches this one symptom (a saved reasoning-effort level breaking a judge-model switch) after the fact; blog posts (`tianpan.co`'s "The Eval Harness Whose Judge Model Was Upgraded Silently" and "Model Migration Bills You Twice") recommend manually pinning judge snapshot IDs and re-running against a frozen judge, but describe this as a known workaround, not a feature any eval framework (promptfoo, deepeval) ships natively. No framework was found that advertises graceful judge-model migration as designed-for.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the shim sits in front of the LLM provider APIs (OpenAI, Anthropic, etc.) that eval frameworks already call to run judge scoring, and reads each provider's public models/capabilities metadata (e.g. an API's `/models` endpoint) to know which parameters a given judge model actually supports. The provider SDKs themselves are mature, already-integrated connectors; the capability-compatibility matrix this idea builds on top of them does not exist today and is hand-maintained as part of the build.

## The Gap

A live GitHub PR, `PostHog/posthog#133640` ("fix(aio): drop a saved reasoning level when an eval switches models," 2026-11-11, 3 reactions, 5 comments), documents agents switching an eval's LLM judge to a different model via API/MCP and getting a 400 error because the eval still carries an incompatible saved reasoning-effort level from the prior judge — the UI path already handled this but API callers didn't. Two corroborating blog posts (`tianpan.co`'s "The Eval Harness Whose Judge Model Was Upgraded Silently" and "Model Migration Bills You Twice") describe teams manually pinning judge snapshot IDs and re-running against a frozen judge as a known pain point, not something any framework handles for them. This is a bug being patched reactively in a shipping product, not a solved abstraction — judge-model portability is still being discovered one breakage at a time.

## The Project

A thin middleware library that any eval framework (or custom harness) wraps its judge-model API calls in. It maintains a small, versioned capability matrix per provider/model (which parameters — reasoning effort, response format, max tokens, temperature bounds — a given model actually accepts), strips or remaps incompatible saved settings automatically when a judge model is swapped, and raises a clear, structured warning ("this eval's saved `reasoning_effort: high` isn't supported by `gpt-X`; dropped") instead of a bare 400 error. A second piece addresses the "silently upgraded" half of the problem: an opt-in judge-snapshot pinning mode that detects when a provider has silently moved a default alias (e.g. "latest") to a new underlying model and alerts before scores silently shift.

Core components: (1) a provider-capability matrix, updated via each provider's own models-metadata endpoint where available, hand-curated otherwise; (2) a request-normalizing wrapper that strips/remaps incompatible params at call time; (3) a judge-snapshot pin-and-detect mode comparing a frozen judge ID's behavior against the live default over time; (4) adapters for promptfoo and deepeval's existing judge-configuration format, so adoption doesn't require a rewrite.

## Tangible Impact

**Population**: teams running CI-integrated LLM-as-judge eval pipelines (promptfoo and deepeval together cross 46,000+ combined GitHub stars, per the gap-analyst's own P3 verdict notes in this digest, giving a concrete lower bound on the number of teams running this exact pattern) who periodically swap or upgrade the judge model — a routine, recurring operation, not an edge case, as providers deprecate and replace models every few months.

**Mechanism**: converts a judge-model swap from a breakage discovered via a runtime 400 error or silently-shifted scores (as in the PostHog PR and the "Model Migration Bills You Twice" post) into a planned, warned-about, automatically-remapped operation — removing the need for every team to independently rediscover and hand-patch the same class of incompatibility.

**Measure**: number of distinct provider-parameter incompatibilities caught and auto-remapped without a runtime error (backtested against PostHog's own documented case and a constructed test matrix of 5-10 provider/model pairs); time for a team to swap judge models end-to-end (target: a config change, not an engineering PR, mirroring the idea's own differentiation from PostHog's reactive patch); number of silent default-model-alias upgrades detected before they shift scores undetected.

## Why Now

The PostHog PR is a live bug in a maintained, shipping product from inside this digest's 30-day window, and the gap-analyst confirmed no framework handles this natively — meaning the next provider model deprecation cycle (which happens on a roughly quarterly cadence across OpenAI/Anthropic/Google) will reproduce this exact breakage across every team running promptfoo or deepeval in CI, making this a recurring, predictable pain point rather than a one-off.

## Skill Angle

A Claude Code skill, separable from the runtime shim, that audits a team's existing eval config before they attempt a judge-model swap. **Trigger**: a developer says "I'm switching my eval judge from model X to model Y" or is about to edit a promptfoo/deepeval judge config. **Inputs**: the current judge configuration (pasted YAML/JSON), the target model's name, and — if available — that model's provider documentation page or capability list pasted in. **Output**: a migration diff listing exactly which saved settings are incompatible with the target model, what to change or drop, and a suggested pinned-snapshot ID to use for reproducibility. This differs from the project: the project is the always-on request-normalizing middleware; the skill is a one-shot pre-migration audit a team can run even without installing the shim, useful as a lighter-weight first step.

## MVP Sketch

Two to three weeks, 1-2 people: build the capability matrix and normalizing wrapper for just OpenAI and Anthropic's judge-relevant parameters (reasoning effort, response format, max tokens), ship a promptfoo adapter first (largest install base per P3's verdict notes), and validate by reproducing the exact PostHog PR scenario end-to-end — swap a judge model with an incompatible saved reasoning level and confirm the shim catches and remaps it instead of raising a 400.

## Risks & Open Questions

- Strongest reason this might already be solved: if promptfoo or deepeval simply upstream-merge their own version of this normalization in response to enough user reports, this becomes redundant — worth checking both projects' open issues before committing to a standalone build.
- Capability matrices for every provider/model pair require ongoing maintenance as providers ship new models; staleness risk if not automated against provider metadata endpoints where those exist.
- Open question: how many providers actually expose machine-readable capability metadata (vs. requiring hand-curated docs-scraping), which directly bounds how automatable the matrix can be.
- Open question: whether silent default-alias upgrades (the "upgraded silently" half of the gap) are detectable at all without the provider explicitly versioning aliases — may require treating this as a monitoring/alerting feature rather than a preventable one.
