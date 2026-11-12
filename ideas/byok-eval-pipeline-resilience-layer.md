# Key Guard: A Resilience Layer for BYOK LLM-Judge Eval Pipelines

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability.md · P3
- **Maturity verdict**: PARTIAL — generic 429/backoff handling for LLM calls is well solved (Python `tenacity`/`backoff`, LangSmith's built-in SDK retry with `Retry-After` honoring, `llmfuse`'s multi-provider failover), but no product specifically addresses the BYOK-eval-platform failure mode of silently losing evaluation results and requiring manual key re-validation plus per-evaluation re-enable after a 429 burst. Building blocks exist; the specific eval-pipeline recovery UX gap does not appear solved elsewhere.
- **Format**: BOTH

## The Gap
GitHub `PostHog/posthog` PR #128370 (2026-11-03, 7 comments): "BYOK teams on OpenAI, Azure OpenAI, Anthropic or Gemini lose every LLM judge evaluation on a key after a burst of 429s. Recovery takes a key re-validation plus a re-enable on each evaluation. #123445 added retries for custom endpoints only." The referenced prior fix covered only custom endpoints, confirming first-party-provider retry/backoff for eval pipelines specifically was still missing as of this cycle — a narrow but concrete reliability gap in production eval infrastructure.

## The Project
A provider-agnostic middleware library ("Key Guard") that sits between an eval platform's judge-calling code and the BYOK provider SDKs (OpenAI, Azure OpenAI, Anthropic, Gemini). On a 429 it queues the failed judge call with its original eval context, backs off exponentially while honoring `Retry-After`, and — if the key is fully exhausted — parks the affected evaluation runs in a "pending-recovery" state instead of marking them failed. Once the key's health check passes again, parked runs auto-resume and re-enable with no manual re-validation or per-evaluation click-through required. Ships as a drop-in Python/TS wrapper around a platform's existing judge-execution layer, backed by a small persistent queue (SQLite/Redis) so recovery state survives a process restart mid-incident.

## Tangible Impact
**Population**: engineering teams operating LLM-as-judge evaluation pipelines against their own OpenAI/Azure OpenAI/Anthropic/Gemini keys — the BYOK users of eval platforms like PostHog AI evals, Langfuse, and custom in-house CI eval runners; the digest evidence says this exact failure mode clusters as "most of the tool's validation errors" over a two-week window for at least one major platform.
**Mechanism**: today a 429 burst permanently loses every judge evaluation on that key until a human notices, re-validates it, and manually re-enables each affected evaluation; Key Guard turns that into an automatic park-and-resume cycle, so a transient rate-limit incident costs latency, not lost data or cleanup labor.
**Measure**: % of evaluation runs that complete successfully despite a mid-run 429 burst (baseline: 0%, since results are lost outright per PR #128370 without a resilience layer); human-minutes spent per month re-validating keys and re-enabling evaluations, before vs after; mean time to full recovery after a rate-limit incident, manual process vs automatic.

## Why Now
LLM-as-judge eval volume scaled enough through 2026 that provider-side rate limits are now a routine operational hazard rather than an edge case — PostHog's own fix was prompted by this being a top bug bucket over a 14-day window — and the backoff/retry building blocks (tenacity, LangSmith's SDK retry) are mature enough that the missing piece is specifically the eval-pipeline-shaped recovery semantics (park/resume without manual re-enable), not the retry mechanics themselves.

## Skill Angle
An "audit my eval pipeline's rate-limit resilience" skill: given a description or code snippet of how a team currently calls its judge provider, it reviews the failure path and names exactly which step causes silent data loss on a 429 (no retry, no park state, requires manual re-enable), then proposes the specific park/resume pattern to add. This is a one-shot design review distinct from the project, which is the actual queue/middleware running continuously inside a live eval pipeline.

## MVP Sketch
2–4 weeks, 1–2 people: wrap one provider SDK (start with OpenAI), build the park/resume state machine on a SQLite-backed queue, and simulate a 429 burst against a toy eval pipeline running 50 judge calls. Validate: with Key Guard in front, all 50 evaluations eventually complete (just delayed); in a control run without it, the burst-affected calls are dropped outright.

## Risks & Open Questions
- If PostHog's narrow fix generalizes well internally, other platforms may each ship their own one-off patch rather than adopt a shared library — needs early traction with at least one platform beyond PostHog.
- Provider rate-limit behavior and error shapes differ enough (OpenAI vs Azure vs Anthropic vs Gemini) that true provider-agnosticism may require more per-provider glue code than the MVP scope assumes.
- A persistent queue introduces its own failure mode (queue corruption, lost state) that needs a tested recovery path or it just relocates the data-loss risk.
- Generic backoff libraries could be judged "good enough" if a platform wires retry logic around existing calls without needing full park/resume semantics — worth validating the gap is real friction, not unused-library adoption.
