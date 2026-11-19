# Off the Hot Path: Judge-Verdict Caching Strategy Review

A self-contained prompt template for reviewing a team's synchronous LLM-as-judge gate and designing a caching strategy for it — before anyone builds the caching layer. Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.), fill in your own details where marked, and send it.

## When to use this

Use this when your team has an LLM-as-judge check that runs **synchronously** on a request's serving path — a content-moderation gate, an action-approval check in an agent pipeline, or a response-quality gate in a chat product — and judge latency or token cost has become a real bottleneck, and you're trying to figure out *how* to cache judge verdicts before committing engineering time to building it.

This does not apply to an async, post-hoc judge that evaluates traces after the fact without blocking anything — that's a different problem with different tooling.

This produces a one-time written strategy: a cache-key recommendation, a TTL/invalidation design, and a hit-rate-ceiling estimate. It does not produce the running cache itself, does not call any real model, and does not measure real latency — it's a design review you can hand to whoever builds the actual middleware.

## What to hand over

**Data source: Manual.** You paste your own description — nothing is fetched automatically from any API or connector. Specifically, provide:

1. **The gate call itself** — a code snippet, pseudocode, or plain description of what triggers your judge call and what gets passed into it (the whole request? a subset of fields?).
2. **What varies across calls** — which fields of the input actually change from request to request (e.g., free-text user messages, a fixed set of enum-like action types, or a mix).
3. **How often the judge changes** — how frequently you update the judge's prompt, model, or scoring rubric (e.g., "every couple weeks," "basically frozen," "we A/B test weekly").

Strongly recommended if you have it:

4. Any sense of how often the *same or near-identical* input recurs in real traffic.
5. Whether the correct verdict could change over time independent of the input content (e.g., a fact-check-style judge vs. a purely content-based one).
6. Your target latency or cost budget, if one exists.

## The prompt to paste

```
You are reviewing my team's synchronous LLM-as-judge gate and designing a
caching strategy for it. This is a one-time design review, not an
implementation — do not write caching code, do not call any real model,
and do not invent numbers you weren't given.

Here is our gate:

1. The gate call: <paste your code/pseudocode/description of the judge call
   and what triggers it>
2. What varies across calls: <describe which fields of the input change
   request to request>
3. How often the judge changes: <describe update cadence for the judge's
   prompt/model/rubric>
4. Repeat-input signal (if known): <any sense of duplicate/near-duplicate
   rate in real traffic, or "unknown">
5. Time-sensitivity (if known): <could the correct verdict change over time
   independent of the input content? or "no indication either way">
6. Latency/cost budget (if any): <target p95/p99 or cost ceiling, or "none
   stated">

Follow this procedure:

1. Check you have enough to work with. If what-varies (item 2) is too vague
   to classify, ask me rather than guessing.
2. Split the input into verdict-relevant fields (content, action, context
   that could change the decision) vs. noise fields (IDs, timestamps,
   formatting) that never affect the verdict. List both explicitly.
3. If the verdict could depend on real-world state that changes over time
   (fact-checking, "is this still true today"), flag that subset as a
   caching blocker needing a short TTL or exclusion — don't assume
   time-sensitivity I didn't indicate.
4. Recommend a cache-key mode:
   - If the relevant fields are structured/enum-like, recommend exact-match
     keying on normalized relevant fields. This is always the first
     recommendation.
   - If relevant fields are mostly free text with common near-duplicate
     phrasing, recommend similarity-based (embedding) keying as a second
     phase on top of exact-match, with an explicit, written risk flag that
     it can serve a cached verdict for a non-equivalent input — and never
     as the sole mode for a safety-critical gate (moderation, abuse/fraud)
     without that flag.
5. Recommend a TTL and an invalidation trigger. Always recommend tagging
   every cached verdict with a version identifier for the judge's exact
   prompt/model/config, and invalidating all entries under an old version
   the moment the judge changes — don't rely on TTL alone.
6. Estimate a hit-rate ceiling ONLY if I gave you repeat-input signal. If I
   didn't, say plainly that no estimate is possible and tell me the
   smallest concrete step to get one (e.g., log a day of real requests and
   measure duplicate/near-duplicate rate).
7. State whether an in-memory cache is enough or a shared backend
   (Redis/SQLite-equivalent) is needed, based on my deployment, without
   writing the implementation.
8. Write up the final report in this exact structure:

# Judge-Verdict Caching Strategy Review

**Confidence**: [full / limited, with the specific reason if limited]

## 1. What You Described
- Gate call: ...
- Verdict-relevant fields: ...
- Noise fields (excluded from the key): ...
- Judge change cadence: ...
- Time-sensitivity: ...

## 2. Cache-Key Recommendation
...

## 3. TTL and Invalidation
- Recommended TTL: ...
- Invalidation trigger: ...
- Time-sensitive carve-out: ...

## 4. Hit-Rate Ceiling
...

## 5. Backend Scope
...

## 6. What This Review Does Not Cover
[Explicit: not a running cache, no real latency measured, no judge model
called, numbers are estimates/ceilings, not measurements.]

Rules you must follow:
- Never invent a hit-rate percentage without my own repeat-input signal.
- Never recommend similarity-based keying alone for a safety-critical gate
  without the written risk flag.
- Never skip the judge-version invalidation recommendation.
- Never hand back caching implementation code — strategy only.
- Never claim a latency number is measured; only restate what I gave you
  or describe qualitatively.
```

## What you get back

A single markdown report in six sections (exactly as specified in the prompt above): what was described, the cache-key recommendation, TTL/invalidation design, a hit-rate ceiling (or an honest "unmeasurable yet" plus next step), backend scope, and an explicit list of what the review didn't cover. No code, no invented numbers, no claim of measured latency.

## What this is not

This is not the caching middleware itself — it's the design review that precedes building or buying one. If you want the actual library (pluggable backends, versioned verdict store, hit-rate reporting), that's a larger build this review's output feeds into, not something a single chat prompt produces.
