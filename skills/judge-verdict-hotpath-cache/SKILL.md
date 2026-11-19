---
name: judge-verdict-hotpath-cache
description: Reviews a team's existing synchronous LLM-as-judge gate (content moderation, action approval, response-quality check) and produces a cache-key strategy, TTL/invalidation design, and a hit-rate-ceiling estimate — a one-shot design review before they build or buy a caching layer, not the cache itself.
---

# Off the Hot Path: Judge-Verdict Caching Strategy Review

## When to use this
Reach for this when a team says something shaped like "our LLM-as-judge gate runs synchronously on every request and it's eating our latency/token budget — should we cache verdicts?" or "we want to cache judge verdicts but we're not sure how to key the cache or when to invalidate it." It applies specifically to a judge call that sits *synchronously* on a request's serving path (the request blocks waiting for the verdict) — not an offline/batch eval pipeline, and not an async post-hoc judge that doesn't block anything (that's a different problem — see "What this skill does not do" below).

This is a one-time design review producing a written strategy, not a running cache. It does not write the caching middleware, does not measure real latency, and does not know the team's actual traffic distribution unless they supply it.

## Inputs
**Data source**: Manual — the user pastes a description or code snippet of their current synchronous judge-gate call: what triggers it, what fields of the input actually vary, how often the judge's prompt/model/config changes, and (ideally) a rough sense of how repetitive real traffic is. There is no connector or API this reads from; nothing is fetched automatically, and no real judge model is called during this review.

Required:
1. **The gate call itself** — a code snippet, pseudocode, or plain description of what triggers the judge call and what gets passed to it (full request payload? a subset of fields?).
2. **What varies across calls** — which fields of the input change request-to-request (e.g., free-text user message, a fixed set of enum-like action types, a mix of both).
3. **How often the judge changes** — how frequently the judge's prompt, model, or scoring rubric is updated (e.g., "we tweak the prompt every couple weeks," "basically frozen since launch," "we A/B test judge prompts weekly").

Strongly recommended (skip only if unavailable, and say so in the output):
4. **Repeat-input signal** — any existing sense of how often the *same or near-identical* input recurs (e.g., "about 20% of moderation requests are the same handful of canned responses," "every request is a unique user message, basically no repeats," server logs showing duplicate request bodies).
5. **Time-sensitivity of the verdict** — whether the correct verdict for a given input could change over time independent of the judge itself (e.g., "is this claim still accurate as of today," vs. a verdict that's purely a function of the input content and will never change).
6. **Latency/cost budget** — the target p95/p99 latency or token-cost ceiling that's motivating this, if any.

## Procedure
1. **Validate input sufficiency.** Confirm items 1–3 are present. If "what varies" (item 2) is missing or too vague to classify, ask for it rather than guessing — the entire cache-key recommendation depends on it. If item 3 is missing, state explicitly that invalidation-trigger guidance will be qualitative only.
2. **Separate verdict-relevant fields from noise.** From the gate call description, identify which fields of the input could plausibly change what the judge decides (content being judged, the action being approved, relevant context) versus fields that are purely bookkeeping and never affect the verdict (request IDs, timestamps unrelated to time-sensitivity, user session metadata, formatting/whitespace differences). List both groups explicitly — this is the basis for the cache key, and getting it wrong (including a noise field in the key) is the single biggest cause of a cache that never hits.
3. **Flag time-sensitivity.** If the user indicated (or the gate's described purpose implies) the verdict depends on real-world state that changes independent of the input text (fact-checking, "is this still in stock," policy that changes by date), name that explicitly as a caching blocker for that subset of traffic and recommend a short TTL (hours, not days) or excluding that category from caching entirely. Never assume time-sensitivity where the user hasn't indicated it — ask if genuinely ambiguous.
4. **Recommend a cache-key mode.** Using the verdict-relevant fields from step 2:
   - If those fields are structured/enum-like (fixed action types, categorical fields, short canonical strings) → recommend **exact-match keying** on the normalized relevant fields (after stripping noise fields and normalizing whitespace/case where safe). This is always the first-choice recommendation — it carries no risk of serving a wrong verdict for a dissimilar input.
   - If those fields are substantially free text where near-duplicate phrasing is common (the same intent worded differently) → recommend **similarity-based keying** (embedding lookup against prior judged inputs above a similarity threshold) as a second phase, explicitly flagged as higher-risk: it can serve a cached verdict for an input that resembles but isn't equivalent to a prior one. Recommend exact-match as the always-on first layer even when similarity-based is added, with a conservative similarity threshold the user should tune against their own false-cache-hit tolerance.
   - Never recommend similarity-based keying as the *only* mode for a safety-critical gate (content moderation, abuse detection) without explicitly calling out the risk in writing.
5. **Recommend TTL and invalidation trigger.** TTL should be driven by (a) time-sensitivity from step 3, and (b) the judge-change cadence from input 3 — if the judge changes every N weeks, cached verdicts older than that are already suspect regardless of time-sensitivity. Always recommend tagging every cached verdict with a version identifier for the judge's prompt/model/config at the time it was produced, and invalidating (not just expiring) all entries tagged with an old version the moment the judge changes — this is the one piece of guidance that generalizes regardless of traffic pattern, because silently serving a verdict from a judge config that no longer exists is the main way this kind of cache goes wrong in production.
6. **Estimate a hit-rate ceiling.** If repeat-input signal (input 4) was supplied, use it directly to state a hit-rate ceiling range (e.g., "if ~20% of inputs are exact or near-duplicates, exact-match caching alone has a ceiling around 15-20%; similarity-based keying could raise that ceiling but the actual achieved rate depends on the similarity threshold chosen"). If no repeat-input signal was supplied, do not invent a number — say explicitly that no hit-rate estimate is possible without a sample of real traffic, and recommend the smallest concrete next step: log a sample of real request bodies for a day and measure the duplicate/near-duplicate rate before committing to similarity-based keying.
7. **Name the backend scope, not the implementation.** State whether an in-memory cache is sufficient (single-process gate, modest traffic) or a shared backend (Redis/SQLite-equivalent) is needed (multi-process or distributed gate) based on what the user described about their deployment — but do not write the caching code itself; that is a separate build.
8. **Assemble the final report** in the Output format below.

## Output format
A single markdown report with exactly these sections, in this order:

```
# Judge-Verdict Caching Strategy Review

**Confidence**: [full / limited — note why if limited, e.g. "no repeat-input signal provided, hit-rate ceiling withheld" or "judge-change cadence not provided, invalidation guidance is qualitative only"]

## 1. What You Described
- Gate call: [one-line restatement of the trigger/call]
- Verdict-relevant fields: [list]
- Noise fields (excluded from the key): [list]
- Judge change cadence: [as stated, or "not provided"]
- Time-sensitivity: [flagged subset, or "none indicated"]

## 2. Cache-Key Recommendation
[Exact-match / exact-match-first-with-similarity-phase-2 / similarity-based-with-explicit-risk-flag — with the specific fields that form the key, normalized how]

## 3. TTL and Invalidation
- Recommended TTL: [value or range, with reasoning]
- Invalidation trigger: [version-tag-on-judge-change, always recommended]
- Time-sensitive carve-out: [if any]

## 4. Hit-Rate Ceiling
[Concrete range from supplied repeat-input signal, or explicit "cannot estimate without a traffic sample" plus the one next step to get one]

## 5. Backend Scope
[In-memory sufficient / shared backend needed, with the one-line reason]

## 6. What This Review Does Not Cover
[Explicit: this is not the running cache, no real latency was measured, no judge model was called, numbers are estimates/ceilings not measurements]
```

## Guardrails
- Never invent a hit-rate percentage without the user's own repeat-input signal or traffic sample — state the ceiling is unknown and name the concrete step to measure it instead.
- Never recommend similarity-based (embedding) keying as the sole or default mode for a safety-critical judge gate (content moderation, abuse/fraud detection) without an explicit written risk flag about serving a cached verdict for a non-equivalent input.
- Never omit the judge-version invalidation recommendation — a TTL alone without version tagging is the exact failure mode (silently serving a verdict from a retired judge config) that makes this cache riskier than a generic HTTP cache.
- Never write or hand back actual caching middleware code — this skill produces a strategy document, not an implementation; if the user wants the implementation, say that's a separate build this review feeds into.
- Never assume a field is "noise" (safe to exclude from the cache key) without the user's confirmation that it doesn't affect the verdict — when genuinely ambiguous, ask rather than guess, since an under-inclusive key (too loose) is the main way a cache silently serves wrong verdicts.
- Never claim any latency number as measured — this review produces no timing data; every latency reference is the user's own stated figure or an explicit qualitative characterization.
