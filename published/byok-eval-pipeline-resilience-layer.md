# Key Guard: A Resilience Layer for BYOK LLM-Judge Eval Pipelines

A single rate-limit burst from OpenAI, Azure OpenAI, Anthropic, or Gemini shouldn't be able to erase a day's worth of evaluation runs — but on most BYOK eval setups today, it can. The fix isn't a smarter retry library; those already exist and work fine. The missing piece is what happens to the *evaluation*, not the API call, once the key gets rate-limited: right now, nothing happens except silent data loss and a manual cleanup chore.

## The Gap

The evidence for this is concrete and recent: GitHub `PostHog/posthog` PR #128370 ("fix(aio): retry byok 429s from first-party providers," 2026-11-03, 7 comments) describes teams running their own API keys through an eval platform losing every LLM-judge evaluation on that key after a burst of 429s — recovery requires re-validating the key and then manually re-enabling each affected evaluation one at a time. The PR itself only patches custom-endpoint retries; it explicitly leaves first-party providers (OpenAI, Azure OpenAI, Anthropic, Gemini) exposed to the same failure.

This isn't a case of nobody having solved rate-limit handling. Generic 429/backoff tooling is mature — Python's `tenacity` and `backoff` libraries, LangSmith's built-in SDK retry with `Retry-After` honoring, and multi-provider failover tools like `llmfuse` all handle the mechanics of retrying a rate-limited call. What none of them address is the eval-pipeline-shaped consequence: when a key gets fully exhausted mid-run, the evaluation itself needs to park in a recoverable state and resume automatically once the key is healthy again — not silently fail and wait for a human to notice. That specific recovery UX gap, as PostHog's own bug report frames it, doesn't appear solved anywhere else.

## The Project

Key Guard is a provider-agnostic middleware library that sits between an eval platform's judge-calling code and the BYOK provider SDKs. When a 429 hits, it queues the failed judge call along with its original evaluation context and backs off exponentially, honoring `Retry-After` headers. If the key is fully exhausted rather than just rate-limited, the affected evaluation runs get parked in a "pending-recovery" state instead of being marked failed outright. Once the key passes a health check again, those parked runs auto-resume and re-enable — no manual key re-validation, no clicking through each evaluation one at a time.

It ships as a drop-in Python/TypeScript wrapper around a platform's existing judge-execution layer, backed by a small persistent queue (SQLite or Redis) so recovery state survives a process restart mid-incident rather than evaporating with it.

## Tangible Impact

**Population**: engineering teams operating LLM-as-judge evaluation pipelines against their own OpenAI/Azure OpenAI/Anthropic/Gemini keys — the BYOK users of eval platforms like PostHog AI evals, Langfuse, and custom in-house CI eval runners; the digest evidence says this exact failure mode clusters as "most of the tool's validation errors" over a two-week window for at least one major platform.
**Mechanism**: today a 429 burst permanently loses every judge evaluation on that key until a human notices, re-validates it, and manually re-enables each affected evaluation; Key Guard turns that into an automatic park-and-resume cycle, so a transient rate-limit incident costs latency, not lost data or cleanup labor.
**Measure**: % of evaluation runs that complete successfully despite a mid-run 429 burst (baseline: 0%, since results are lost outright per PR #128370 without a resilience layer); human-minutes spent per month re-validating keys and re-enabling evaluations, before vs after; mean time to full recovery after a rate-limit incident, manual process vs automatic.

## Try It

A companion Claude Code skill exists at [`skills/byok-eval-pipeline-resilience-layer/`](../skills/byok-eval-pipeline-resilience-layer/): it "audits the code/config a team uses to call its LLM-judge provider (OpenAI/Azure OpenAI/Anthropic/Gemini) in an eval pipeline, and pinpoints exactly where a 429/rate-limit burst causes silent evaluation data loss versus where it's actually recoverable. Use when someone is debugging 'we lost eval results after a rate-limit spike' or designing/reviewing a BYOK eval pipeline's judge-calling path before it ships."

This is a one-shot design review, not the always-on middleware itself — hand it a description or code snippet of how your pipeline currently calls its judge provider, and it tells you exactly which step causes silent data loss and what park/resume pattern to add. Two ways to use it: paste the contents of `skills/byok-eval-pipeline-resilience-layer/README.md` into any AI chat tool along with your pipeline code, or drop the whole `byok-eval-pipeline-resilience-layer/` folder into `~/.claude/skills/` if you're running Claude Code.

Worth knowing going in, per the idea's own risk notes: if a platform decides generic backoff wired around existing calls is "good enough," the fuller park/resume semantics here may be more than they're willing to adopt — and if PostHog's internal fix generalizes well enough, other platforms may each patch this one-off rather than reach for a shared library. The gap is real as of this writing, but it's narrow, and the path of least resistance for any one platform is still a local patch rather than external adoption.

---

Surfaced from `research/2026-11-12-llm-evaluation-observability.md`, pattern `P3`.
