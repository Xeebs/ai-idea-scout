# Catalog Cache: A Drop-In Prompt-Cache Breakpoint Proxy for MCP Tool Definitions

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-13-tool-use-mcp-ecosystem-3.md · P2
- **Maturity verdict**: PARTIAL — the OpenAI Agents SDK ships a `cache_tools_list` flag that caches the `list_tools()` call itself but is lost whenever the server instance is recreated and doesn't touch per-turn prompt-token reload; a live, open GitHub issue against Claude Code ("Tool catalog (~24k tokens) sent uncached on every API request — cache_control breakpoint missing") shows the dominant client hasn't fixed this, with a third-party reverse proxy cited as the only workaround. GitHub search for `MCP tool cache` / `MCP schema cache session` found only two near-zero-star personal repos — a real, narrow, addressable gap distinct from the tool-count/retrieval problem (which is SATURATED by existing filtering/routing products).
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the standard MCP `tools/list` response from every connected server (part of the base MCP spec, already mature) and writes a `cache_control` breakpoint into the outgoing request using the LLM provider's own prompt-caching API (Anthropic's Messages API `cache_control` field, OpenAI's automatic prompt caching) — both mature, documented, shipping APIs; no new connector needs to be built, only the glue that uses them correctly for this specific payload shape. The Skill Angle is MANUAL — the user pastes a request/response trace or token-usage export from their agent host showing the tool-definitions block repeating each turn.

## The Gap

getunblocked.com's "MCP Tool Overload" states plainly that MCP tool-schema JSON "is not cached across model calls inside the agent loop, so the full schema list reloads every turn," and a live, still-open Claude Code GitHub issue names the exact mechanism: a ~24k-token tool catalog sent uncached on every single API request because no `cache_control` breakpoint is set after it. This is distinct from the (saturated) tool-count/retrieval problem — even a perfectly curated, small tool list still gets re-billed and reprocessed at full price every turn if it isn't cached, and no maintained client or library closes that specific reload-per-turn mechanism today.

## The Project

A transparent reverse proxy that sits between an MCP-using agent host and the LLM provider's API. It inspects each outgoing request, locates the static tool-definitions block (the serialized MCP `tools/list` output merged across connected servers), and inserts the provider's prompt-cache breakpoint immediately after it — so a session where the tool set hasn't changed since the last turn hits the provider's cache instead of reprocessing the full block. Because some hosts recreate the MCP server connection (and therefore the in-memory tool list) on every run, losing the cache key stability the OpenAI Agents SDK's own flag needs, the proxy also canonicalizes and persists a stable serialization of the merged tool catalog across a session, re-keying the cache only when a connected server's `tools/list` actually changes (detected via a hash diff, the same signal a drift auditor would use). Components: a transparent MCP-aware request interceptor, a canonical tool-list serializer/hasher, a per-provider cache-breakpoint adapter (Anthropic/OpenAI today, extensible), and a reporting layer that reads the provider's own `cache_creation`/`cache_read` token counts back from the API response to show real savings.

## Tangible Impact

**Population**: Developers and teams running long, multi-turn MCP-tool-heavy agent sessions on metered per-input-token billing — concretely, the Claude Code users behind the open "tool catalog sent uncached" issue, and by extension any agent-host user wiring up more than a handful of MCP servers (the registry's 20,000–30,000 listed servers make a 10+ tool, multi-server session the normal power-user setup) into a session that runs more than a few turns.
**Mechanism**: Today every turn re-sends and re-bills the full tool-definitions block at full input-token price even when nothing about the available tools has changed; the proxy makes that block cache-eligible and keeps its cache key stable across the session, so the provider serves the cached prefix (typically billed at a fraction of fresh input-token price) instead of reprocessing it, cutting both cost and per-turn latency.
**Measure**: (1) % of input tokens served from cache vs. billed fresh per turn, read directly from the provider's own `cache_read`/`cache_creation` usage fields, across a fixed multi-turn test session. (2) Dollar cost per session before vs. after, holding the task and tool set constant. (3) Median per-turn latency before vs. after, since a cache hit also skips reprocessing time, not just cost.

## Why Now

Prompt caching (`cache_control` breakpoints) is a mature, already-shipping API on both major providers, and the exact gap — nobody wiring it correctly to the MCP tool-definitions block specifically — is named as currently unfixed in a live, open GitHub issue against the dominant MCP client; the fix requires no new model capability, only correctly using an API that already exists.

## Skill Angle

A "diagnose my tool-catalog cache" skill: hand it a pasted request/response trace or a token-usage export from an agent session, and it checks whether the tool-definitions block is being re-billed as fresh input tokens on every turn, estimates the dollar/latency savings a cache breakpoint would capture for that specific session, and returns a concrete fix (where to place the breakpoint, or a pointer to adopting the proxy). This differs from the project by being a one-time diagnostic a developer runs against their own logs, not an always-on proxy sitting in the request path.

## MVP Sketch

2–3 weeks, 1 person: a lightweight HTTP reverse proxy (Node or Python) that passes MCP client↔host traffic through unmodified except for injecting the cache breakpoint and stabilizing the serialized tool list, targeting Anthropic's API first. Experiment: run the same 10-turn task twice against a 5-server, ~60-tool MCP setup — once through a stock client, once through the proxy — and compare billed input tokens and per-turn latency using the provider's own usage fields as ground truth.

## Risks & Open Questions

- The clearest fix is for Anthropic/OpenAI or the dominant client to ship this natively (it's an open client-side issue, not a model limitation) — if Claude Code closes that GitHub issue with a built-in fix, the proxy's value collapses to legacy/third-party hosts.
- Any tool-set change (server added/removed, description edited) invalidates the cache for that turn, so benefit scales with session length and tool-set stability — short sessions or rapidly-reconfigured toolsets see little gain.
- Sitting as a man-in-the-middle on API traffic touches credentials/auth headers, which raises its own trust bar for adoption versus a client-native fix.
- Savings depend on provider-specific cache pricing and TTL behavior, which can change without notice — the reporting layer needs to track real provider usage fields rather than assuming a fixed discount rate.
