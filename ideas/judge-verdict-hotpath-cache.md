# Off the Hot Path: A Judge-Verdict Caching Layer for Synchronous LLM-as-Judge Gates

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-19-llm-evaluation-observability.md · P4
- **Maturity verdict**: PARTIAL — web search found no dedicated standalone library, but real adjacent implementations: the `swink-agent-eval` Rust crate ships a bounded (1024-entry default) in-memory + optional-disk judge-verdict cache with versioned keys; an Apple research paper (Krites, semantic caching) keeps judge calls off the synchronous serving path; Microsoft Azure AI Foundry documents judge-prompt restructuring for provider-side prefix caching (5-16% latency reduction). These are real but narrow/niche (one Rust crate, vendor blog guidance, a research paper) — no widely-adopted, generalized, portable library.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the Project wraps the team's own existing synchronous judge-gate call: it intercepts the judge invocation already happening on the request's hot path and keys a cache against the inputs that actually determine the verdict (not the raw request, which may vary irrelevantly). No new external data source is introduced. The Skill Angle is MANUAL — the user pastes a description or code snippet of their current hot-path judge-gate call for a one-shot caching-strategy review.

## The Gap
ThePlenkov/bro PR #747, "perf(hooks): cached gate verdict, judge off the hot path" (2026-10-28, 3 reactions/13 comments), fixed exactly this inside one project's internal hook pipeline. Three real but fragmented attempts at the underlying idea exist elsewhere (a narrow Rust crate, an Apple research paper on semantic caching, and Microsoft's prefix-caching guidance) — confirming the problem is recognized industry-wide, but no one has shipped a generalized, portable, multi-language library that any team running a synchronous LLM-judge gate can drop in.

## The Project
A provider-agnostic caching middleware that sits in front of any synchronous LLM-as-judge gate check (content moderation, action-approval, response-quality gating) and returns a cached verdict for inputs that are equivalent to a prior judged case, instead of re-invoking the judge on every request. Cache keys are derived from the fields that actually determine the verdict (not full raw request text, to maximize hit rate on semantically-equivalent inputs), with configurable exact-match or embedding-similarity-based lookup. Verdicts carry a TTL and a version tag tied to the judge's prompt/model version, so a judge-config change invalidates stale cache entries automatically rather than silently serving outdated verdicts. Ships as a small library with pluggable backends (in-memory, Redis, SQLite) so it scales from a single-process gate to a distributed service.

Components: the cache-key derivation function (exact and similarity-based modes); the versioned-verdict store with TTL and judge-version invalidation; backend adapters (in-memory/Redis/SQLite); a hit-rate/latency-savings reporting hook.

## Tangible Impact
**Population**: Engineering teams running an LLM-as-judge check synchronously on a request's serving path — content-moderation gates, action-approval checks in agent pipelines, and response-quality gates in chat products — where judge latency and cost sit directly in the user-facing critical path. ThePlenkov/bro's fix was prompted by exactly this pattern inside a live hook pipeline, and the three independent adjacent attempts (Rust crate, Apple paper, Microsoft guidance) confirm this recurs across both open-source and enterprise contexts.
**Mechanism**: Today, every request pays the judge's full latency and token cost even when an equivalent input was already judged recently; caching the verdict (with correct invalidation on judge-config change) removes that repeated cost for the subset of inputs that recur or cluster, directly cutting p95/p99 latency and per-request spend on the hot path.
**Measure**: p95/p99 latency reduction on the gated endpoint before vs after caching (target: meaningful reduction proportional to measured cache hit rate); cache hit rate on real production-shaped traffic; judge cost (tokens/calls) per 1,000 requests, before vs after; zero regressions in judge accuracy attributable to serving a stale verdict (validated via the version-tag invalidation test).

## Why Now
LLM-as-judge gates moved from offline eval into synchronous, user-facing serving paths in 2026 widely enough that at least four independent teams (the evidenced PR plus three adjacent attempts) hit the same latency/cost wall this year — the underlying caching mechanics (key derivation, TTL, invalidation) are well-understood from general web caching, but nobody has packaged the judge-specific version (verdict versioning tied to judge config, not just data) into a reusable library yet.

## Skill Angle
Trigger: a team has a synchronous LLM-judge gate check that's become a latency or cost bottleneck and wants a caching strategy before committing to a full integration. Inputs: a description or code snippet of the current gate-check call (what triggers it, what inputs vary, how often the judge/prompt changes). Output: a recommended cache-key strategy (exact vs similarity-based), a suggested TTL and invalidation trigger tied to judge-version changes, and an estimated hit-rate ceiling based on how repetitive the team's actual input distribution looks. This is a one-shot design review distinct from the project, which is the actual cache running continuously in the request path.

## MVP Sketch
2–3 weeks, 1–2 people: build the exact-match caching mode first (defer similarity-based lookup to a v2), with in-memory and Redis backends and judge-version-tagged invalidation. Validate by replaying a synthetic traffic sample with a known repeat-input rate (e.g., 30% semantically-identical requests) against a toy judge gate, confirming cached latency drops to near-zero for repeats while cold-path accuracy stays identical, and confirming a judge-prompt change correctly invalidates all affected entries on the next request.

## Risks & Open Questions
- A badly-chosen cache key (too loose) risks serving a wrong verdict for inputs that look similar but aren't equivalent — the exact-match-first MVP sidesteps this but limits hit rate; similarity-based lookup needs careful validation before it's trustworthy.
- Teams may consider generic HTTP/semantic caching layers "good enough" without judge-specific versioning — worth validating the invalidation-on-judge-change feature is the real differentiator, not unused complexity.
- Judge verdicts that depend on time-sensitive context (e.g., "is this still accurate as of today") are structurally uncacheable past a short TTL, narrowing the addressable gate types.
- If Microsoft/Azure's prefix-caching guidance or a major judge framework ships this natively soon, the project's niche shrinks to teams on frameworks that haven't adopted it yet.
