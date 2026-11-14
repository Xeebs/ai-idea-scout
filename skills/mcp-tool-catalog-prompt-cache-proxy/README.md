# MCP Tool-Catalog Cache Diagnostic

A paste-into-any-AI-chat-tool prompt that answers one specific question: is your MCP-tool-using agent session re-sending and re-billing its full tool-definitions block as fresh input tokens on every turn, instead of getting it served from the LLM provider's prompt cache? It reads your own request trace or token-usage export and tells you whether this is actually happening, how much it's costing you, and the exact fix.

This is not a general token-cost optimizer and not a "too many tools" audit — those are different, already-well-covered problems. This skill only looks at one narrow, specific mechanism: whether the static tool-definitions block your MCP servers advertise is cache-eligible and actually getting cached across turns.

## When to use this

Use this when:
- You're running a multi-turn agent session wired up to one or more MCP servers (Claude Code, a custom agent harness, any MCP host) and your per-session cost or latency looks higher than it should given how little actually changed between turns.
- You want to know, concretely, whether a missing cache breakpoint on the tool-definitions block is the cause before you go build or adopt a proxy to fix it.
- You've seen reports (e.g. the open Claude Code issue describing a ~24k-token tool catalog sent uncached every request) and want to check whether your own session has the same problem.

Don't use this for a single-turn session (nothing to compare), for a session where you already know the tool set changes every turn (a cache miss there is expected, not a bug), or as a catch-all token-cost review — it's scoped to this one mechanism.

## What you need to provide

This is a manual, paste-based diagnostic — nothing here reads a live connector. Give it:

1. **Which provider** you're using: Anthropic (Messages API) or OpenAI (Responses/Chat Completions API). The cache mechanics differ — Anthropic needs an explicit `cache_control` breakpoint; OpenAI's caching is automatic for unchanged prefixes ≥1024 tokens.
2. **At least two consecutive turns** of one of these, with any API keys, bearer tokens, or auth headers redacted first:
   - The raw outgoing request bodies showing the `tools` array (and, for Anthropic, any `cache_control` fields) for turn N and turn N+1; or
   - A token-usage log/export with, per turn, `input_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens` (Anthropic), or the `cached_tokens` field (OpenAI); or
   - A per-turn cost/latency export from your agent host, if it breaks out cached vs. fresh tokens.
3. Optional: how many MCP servers you have connected and roughly how many tools total, so the tool-block size estimate can be sanity-checked.

If you only have one turn, or a usage export with no cache-related fields at all, say so — the honest answer at that point is "insufficient data," not a guess.

## The procedure

1. **Find the tool-definitions block** in what you provided — the `tools` array/field — and note its approximate size.
2. **Compare it turn-over-turn.** Is it identical (ignoring harmless formatting differences) between turn N and turn N+1? Call this `STABLE` or `CHANGED`.
3. **Check for a cache breakpoint.** For Anthropic, look for a `cache_control` object on the last tool definition (or on the `mcp_toolset` entry, if your host uses one) — that's the only place a breakpoint there actually caches the tool block. For OpenAI, there's no explicit breakpoint; the check is whether the tool block is a consistent, unchanged leading prefix of the request.
4. **Read the actual usage fields.** If `cache_read_input_tokens` / `cached_tokens` is present and nonzero on turn N+1 for a `STABLE` tool block, caching is already working. If those fields are missing, zero, or `input_tokens` on turn N+1 looks just as large as turn N with nothing discounted, that confirms the tool block is being rebilled fresh every turn.
5. **Estimate the cost impact** using your real usage numbers, never invented ones. State the savings as "X% of input tokens could move from fresh-billed to cache-read" and flag that the exact dollar gap depends on the provider's current cache-read vs. fresh-input pricing — tell the reader to check the provider's current pricing page rather than trusting a hardcoded rate, since these change.
6. **Estimate latency impact** only if your data includes per-turn latency; a cache hit skips reprocessing time too, but don't guess this without data.
7. **Give the verdict and the exact fix:**
   - Tool block `CHANGED` turn-over-turn → this is an expected cache miss, not a bug. Name what likely changed (a server added/removed, a tool description edited) and point out the fix is tool-set stability, not a breakpoint.
   - Tool block `STABLE` with no cache hit on Anthropic → the fix is: add `cache_control: {"type": "ephemeral"}` on the last tool definition (or the `mcp_toolset` entry) so everything up to and including the tool block becomes cacheable.
   - Tool block `STABLE` with no cache hit on OpenAI → check that the tool definitions are serialized identically turn-over-turn and placed before any per-turn-variable content; automatic caching needs an unchanged prefix.
   - If the host appears to re-fetch/re-serialize the MCP tool list from scratch on every run (losing cache-key stability even though the underlying tools didn't actually change) → flag this as the likely root cause and recommend persisting a canonicalized, hashed serialization of the merged tool catalog across the session instead of re-deriving it per request.
8. If the real issue turns out to be tool count/selection rather than caching, say that plainly instead of forcing a caching verdict onto an unrelated problem.

## Output format

Produce exactly these sections:

1. **Verdict** — `CONFIRMED` (stable tool block, billed fresh every turn), `MISCONFIGURED` (a breakpoint exists but is misplaced, or the host loses cache-key stability across turns), `NOT AN ISSUE` (caching is already working), or `INSUFFICIENT DATA`.
2. **Evidence table** — one row per turn: `Turn | Tool-block stable? | input_tokens | cache_read_input_tokens | cache_creation_input_tokens`, marking any estimated (not directly measured) number with `~`.
3. **Estimated impact** — the % of input tokens that could shift from fresh to cached, with a qualitative dollar-savings note telling the reader to confirm against current provider pricing; latency savings only if latency data was actually given.
4. **Concrete fix** — the exact, named change from step 7 — specific enough to implement without re-reading the rest of the report.
5. **Caveat line** — one sentence on what data was missing, if any, and what a fuller trace would additionally confirm.

## Guardrails

- Never present an estimated dollar figure as a measured one — always separate "measured from your own usage fields" from "approximate, verify against current pricing."
- Never invent `cache_read_input_tokens` / `cached_tokens` values that weren't given — if those fields are absent, say the data can't confirm or deny caching rather than inferring it from totals alone (beyond a clearly labeled estimate).
- Never call a tool-block change across turns a "bug" — that's correct, expected cache-invalidation behavior, not a defect.
- Never push a specific third-party proxy product as "the fix" when the real fix is a one-line breakpoint or serialization change you can make yourself — only mention a proxy-based approach as an option for people who can't touch the client/host code directly.
- Never produce a verdict from a single turn of data, or from a trace with visible credentials — ask for a second turn, or ask the user to redact auth headers before continuing.
