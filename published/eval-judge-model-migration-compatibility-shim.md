# Judge Swap: A Compatibility Shim for Migrating Eval Frameworks Between LLM-as-Judge Models

Swapping which model grades your evals should be a config change. Right now it's a bug hunt. A team changes their LLM-as-judge from one model to another — because the old one got deprecated, because the new one scores better, because it's cheaper — and the eval either throws a 400 error from a saved setting the new judge doesn't recognize, or worse, it runs fine and quietly returns different scores because nobody noticed the provider repointed a "latest" alias underneath them. Either way, the team is debugging an infrastructure failure when they thought they were just updating a model name.

## The Gap

This isn't a hypothetical. A live GitHub PR — `PostHog/posthog#133640`, "fix(aio): drop a saved reasoning level when an eval switches models" (2026-11-11, 3 reactions, 5 comments) — shows exactly this breakage happening inside a maintained, shipping product: an eval switched its judge model via API/MCP and got a 400 error because the eval still carried an incompatible saved reasoning-effort level from the old judge. The UI path for this had already been patched; the API path hadn't. Two independent blog posts from the same window — tianpan.co's "The Eval Harness Whose Judge Model Was Upgraded Silently" and "Model Migration Bills You Twice" — describe teams working around the same category of problem by hand: manually pinning judge snapshot IDs and re-running against a frozen judge to avoid scores shifting under them without warning.

What ties these together is that none of it is a feature. PostHog's fix patches one symptom after the fact. The blog posts describe a workaround, not something promptfoo or deepeval — the two most widely-deployed eval frameworks — ship natively. Nobody searched for "graceful judge-model migration" and found a framework that advertises it as designed-for, because none does. Judge-model portability is still being discovered the hard way, one breakage at a time, by whichever team happens to hit it next.

## The Project

The fix is a thin middleware layer that sits between an eval framework and the judge-model API calls it already makes. It maintains a small, versioned capability matrix per provider and model — which parameters a given model actually accepts: reasoning effort, response format, max-token keys, temperature bounds — pulled from each provider's own models-metadata endpoint where one exists, hand-curated where it doesn't. When a judge model gets swapped, the shim strips or remaps whatever settings don't carry over, and raises a structured, specific warning ("this eval's saved `reasoning_effort: high` isn't supported by `gpt-X`; dropped") instead of letting a bare 400 error reach the team.

A second piece handles the other half of the gap — the silent one. An opt-in judge-snapshot pinning mode detects when a provider has quietly moved a default alias like "latest" onto a new underlying model, and flags it before scores start shifting for reasons nobody can trace back to a cause.

The four pieces: a provider-capability matrix, kept current via each provider's models-metadata endpoint where available; a request-normalizing wrapper that strips and remaps incompatible parameters at call time; a judge-snapshot pin-and-detect mode that compares a frozen judge's behavior against the live default over time; and adapters for promptfoo and deepeval's existing judge-configuration formats, so adopting this doesn't mean rewriting an eval pipeline.

## Tangible Impact

**Population**: teams running CI-integrated LLM-as-judge eval pipelines (promptfoo and deepeval together cross 46,000+ combined GitHub stars, per the gap-analyst's own P3 verdict notes in this digest, giving a concrete lower bound on the number of teams running this exact pattern) who periodically swap or upgrade the judge model — a routine, recurring operation, not an edge case, as providers deprecate and replace models every few months.

**Mechanism**: converts a judge-model swap from a breakage discovered via a runtime 400 error or silently-shifted scores (as in the PostHog PR and the "Model Migration Bills You Twice" post) into a planned, warned-about, automatically-remapped operation — removing the need for every team to independently rediscover and hand-patch the same class of incompatibility.

**Measure**: number of distinct provider-parameter incompatibilities caught and auto-remapped without a runtime error (backtested against PostHog's own documented case and a constructed test matrix of 5-10 provider/model pairs); time for a team to swap judge models end-to-end (target: a config change, not an engineering PR, mirroring the idea's own differentiation from PostHog's reactive patch); number of silent default-model-alias upgrades detected before they shift scores undetected.

## Try It

A companion skill, [`eval-judge-model-migration-compatibility-shim`](../skills/eval-judge-model-migration-compatibility-shim/), covers the lighter-weight, no-install version of this: *"Audits an LLM-as-judge eval config (promptfoo, deepeval, or custom) before swapping the judge model to a different one, flagging every saved parameter that will break, needs renaming, or needs re-ranging — and warning if either model ID is an unpinned alias that could silently shift scores later."*

To use it: paste your current judge configuration — the provider/model fields and every saved request parameter (reasoning effort, response format, token-limit keys, temperature, top_p, any provider-specific flags) — along with the target model's name into any AI chat tool, using the skill's `README.md` as the prompt template. For Claude Code, drop the `skills/eval-judge-model-migration-compatibility-shim/` folder into `~/.claude/skills/` and invoke it directly. The skill is a one-shot pre-migration audit you can run even without adopting the shim; the project above is the always-on, request-normalizing version that runs on every call, not just before a planned swap.

## Worth Knowing

The honest risk here is that promptfoo or deepeval could simply absorb this fix themselves. If either project upstream-merges its own version of this normalization in response to enough user bug reports — which is exactly the kind of fix that gets added reactively once enough people hit it — a standalone shim becomes redundant overnight. That's worth checking against both projects' open issues before committing real build time. There's also a harder structural risk underneath the capability matrix: how much of it can even be automated depends on how many providers expose machine-readable capability metadata versus requiring hand-scraped docs, and staleness is a permanent tax if that automation gap is wide. And the "silently upgraded" half of the problem may not be preventable at all, only detectable after the fact — if a provider doesn't explicitly version its aliases, there's no signal to catch before a score shift happens, which would make this a monitoring feature rather than the guardrail it's pitched as.

Surfaced from `research/2026-11-13-llm-evaluation-observability.md`, pattern `P6`.
