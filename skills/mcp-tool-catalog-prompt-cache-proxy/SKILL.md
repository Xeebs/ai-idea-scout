---
name: mcp-tool-catalog-prompt-cache-proxy
description: Diagnoses whether an MCP-tool-using agent session is re-billing its full tool-definitions block as fresh input tokens on every turn instead of hitting the provider's prompt cache, from a pasted request trace or usage export, and names the exact fix. Use when per-turn token cost or latency on an MCP-heavy agent session looks higher than it should.
---

# MCP Tool-Catalog Cache Diagnostic

## When to use this
A developer or team is running a multi-turn agent session wired up to one or more MCP servers (Claude Code, a custom agent loop, or any MCP-using host) and suspects — from a cost bill, a token-usage dashboard, or just "this session feels expensive for how little changed" — that the tool-definitions block (the serialized `tools/list` output merged across connected MCP servers) is being resent and rebilled at full input-token price every single turn instead of being served from the provider's prompt cache. This is the one-time diagnostic a developer runs against their own logs before deciding whether to fix their cache breakpoint placement or adopt a proxy that does it for them.

Do not use this for a single-turn session (there is nothing to compare turn-over-turn), for a session where the tool set is known to change every turn (cache misses there are expected, not a bug), or as a general token-cost optimizer unrelated to MCP tool catalogs — it only looks at the tool-definitions block's caching behavior.

## Inputs
**Data source**: Manual — the user pastes a request/response trace or a token-usage export from their agent host. Nothing here is read from a live connector; this is a one-time log/export the user already has or can generate.

To run this skill, provide:
1. **Provider**: Anthropic (Messages API) or OpenAI (Responses/Chat Completions API) — the cache mechanics and pricing structure differ.
2. **At least 2 consecutive turns** of one of the following, with any API keys/auth headers/bearer tokens redacted before pasting:
   - The raw outgoing request bodies (showing the `tools` array and, for Anthropic, any `cache_control` fields), ideally for turn N and turn N+1 of the same session; or
   - A token-usage export/log showing, per turn, `input_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens` (Anthropic) or the equivalent `cached_tokens` field (OpenAI usage object); or
   - A cost/latency export from the agent host itself (e.g., Claude Code's per-turn token report) if it breaks out cached vs. fresh tokens.
3. Optional but useful: how many MCP servers are connected and roughly how many tools total, to sanity-check the tool-block size estimate.

If the user can only provide a single turn, or usage data with no cache fields at all, say so and return a verdict of `INSUFFICIENT DATA` rather than guessing.

## Procedure
1. **Locate the tool-definitions block.** In a request trace, this is the `tools` array (Anthropic) or `tools` field (OpenAI) — identify it and note its approximate size. If only a usage export is given, treat the `input_tokens` figure on the first turn as the proxy for the full prompt size and reason from the cache fields instead.
2. **Diff the tool block across turns.** Compare the tool definitions turn-over-turn (ignore whitespace/key-ordering differences that don't change semantics). Classify as `STABLE` (identical tool set and descriptions) or `CHANGED` (a server was added/removed, a tool's schema/description edited, or ordering changed in a way that would break a cache prefix).
3. **Check for a cache breakpoint.** For Anthropic traces, look for a `cache_control` object attached to the last tool in the `tools` array (or on the `mcp_toolset` entry if the host uses one) — this is where the breakpoint must sit for the tool block to be cacheable at all. For OpenAI traces, note that automatic prompt caching applies to prefixes ≥1024 tokens with no explicit breakpoint needed, so the check instead is whether the tool block is consistently the leading, unchanged prefix of the request.
4. **Read the usage fields.** If `cache_read_input_tokens` (Anthropic) or `cached_tokens` (OpenAI) is present and > 0 on turn N+1 for a `STABLE` tool block, the cache is working — skip to step 7 with a `NOT AN ISSUE` lean. If those fields are absent, zero, or the full `input_tokens` count each turn roughly equals the tool-block size plus message size (i.e., nothing is being discounted), that confirms re-billing.
5. **Estimate the cost impact.** Using the actual `input_tokens`/`cache_read_input_tokens` figures when present (never invented numbers): compute tokens billed fresh per turn that could have been cache reads, multiply by the gap between the provider's current fresh-input and cache-read price (state this gap qualitatively — e.g. "cache reads are billed at a fraction of fresh input price" — and tell the user to confirm the exact current multiplier on the provider's pricing page rather than hardcoding a rate that can change). If only character/token counts are available with no usage fields, label the estimate explicitly as approximate (chars ÷ 4 heuristic) rather than presenting it as measured.
6. **Estimate latency impact**, only if the trace/export includes per-turn latency — a cache hit also skips reprocessing time. If no latency data is given, omit this rather than guessing.
7. **Determine the verdict** (see Output format) and write the concrete fix:
   - If `CHANGED` tool block: this turn's cache miss is expected behavior, not a bug — name which server/tool changed if identifiable, and note the fix is tool-set stability, not a breakpoint.
   - If `STABLE` tool block with no breakpoint/cache_read: name the exact fix — for Anthropic, "add a `cache_control: {\"type\": \"ephemeral\"}` block on the last tool definition (or the `mcp_toolset` entry) so the provider caches everything up to and including the tool block"; for OpenAI, "ensure the tool definitions are serialized identically and placed before any per-turn-variable content, since automatic caching requires an unchanged prefix."
   - If the host recreates the MCP connection each run (tool list re-fetched from scratch, losing a stable serialization even though the underlying tools didn't change): flag this as the likely root cause and recommend persisting a canonicalized, hashed serialization of the merged tool catalog across the session rather than re-deriving it per request.
8. Never conflate this with the separate, already-saturated "too many tools" problem — if the user's issue is tool count/selection rather than caching, say that plainly and point them elsewhere instead of forcing a caching verdict.

## Output format
A short diagnostic report with exactly these sections:
1. **Verdict** — one of `CONFIRMED` (tool block stable but billed fresh every turn), `MISCONFIGURED` (breakpoint present but misplaced, or host loses cache key stability across turns), `NOT AN ISSUE` (caching already working), or `INSUFFICIENT DATA`.
2. **Evidence table** — one row per turn provided: `Turn | Tool-block stable? | input_tokens | cache_read_input_tokens | cache_creation_input_tokens`. Mark any estimated (non-measured) figures with `~`.
3. **Estimated impact** — % of input tokens that could move from fresh-billed to cache-read, and (only if usage/pricing basis is solid) a qualitative dollar-savings statement with an explicit note to confirm against current provider pricing. Latency savings only if latency data was provided.
4. **Concrete fix** — the exact, named change (breakpoint placement, serialization stability, or "no fix needed/expected miss") from step 7, specific enough to act on without rereading the report.
5. **Caveat line** — one sentence stating what data was missing, if any, and what a fuller trace would let you confirm.

## Guardrails
- Never report a dollar figure as measured when it was derived from an estimate — always distinguish "measured from your usage fields" from "approximate, verify against current pricing."
- Never invent or assume `cache_read_input_tokens`/`cached_tokens` values that weren't in the provided data — if those fields are absent, say the data can't confirm or deny caching, don't infer it from token totals alone beyond a labeled approximation.
- Never call a turn-over-turn tool-block change a "bug" — a changed tool set invalidating the cache is correct, expected provider behavior, not a defect to fix.
- Never recommend a specific third-party proxy product by name as "the fix" when the underlying fix is a one-line breakpoint or serialization change the user can make themselves — name the proxy approach only as an option for users who can't touch the client/host code directly.
- Never proceed on a single turn of data or a trace with credentials still visible — ask for a second turn, or flag unredacted auth headers and ask the user to redact before continuing.
