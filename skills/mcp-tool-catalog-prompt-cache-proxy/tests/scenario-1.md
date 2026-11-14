# Scenario 1 — Claude Code session, 4 turns, stable tool set, confirmed re-billing

## Setup

A developer runs a 4-turn Claude Code session with 3 connected MCP servers (filesystem, GitHub, Postgres) providing 22 tools combined, roughly 21,000 tokens of tool-definition JSON. They export per-turn usage from the Anthropic API responses (via Claude Code's debug log) because the session felt expensive for a task that barely touched any new context. They provide the Anthropic Messages API usage object for each of 4 consecutive turns, plus confirmation that no MCP server was added, removed, or reconfigured during the session.

## Input provided to the skill

**Provider**: Anthropic (Messages API)

**Tool set**: 3 MCP servers (filesystem, GitHub, Postgres), 22 tools total, unchanged across all 4 turns (confirmed by the user).

**Per-turn usage objects** (redacted of everything except usage):

```
Turn 1: {"input_tokens": 21840, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 310}
Turn 2: {"input_tokens": 22190, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 480}
Turn 3: {"input_tokens": 22510, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 265}
Turn 4: {"input_tokens": 22870, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 390}
```

**Request trace excerpt** (turn 2's outgoing `tools` array, truncated): no `cache_control` field present anywhere in the array or on any individual tool entry.

## Pass criteria

The diagnostic output must:
1. Classify the tool block as `STABLE` across all 4 turns (user confirmed no server/tool changes, and `input_tokens` grows only by the small amount expected from accumulating conversation history, not by re-deriving a different tool set).
2. Note that `cache_read_input_tokens` is 0 on every turn including turns 2–4, despite a stable tool block — this is the direct evidence of re-billing.
3. Note the absence of any `cache_control` field in the trace as the root cause.
4. Reach a **Verdict** of `CONFIRMED`.
5. Produce an evidence table with all 4 turns and the `~` marker only on any estimated (not directly given) figures — none of the given usage numbers should be marked `~` since they were measured, not estimated.
6. State the estimated impact as "most of the ~21-22k token tool block could move from fresh-billed to cache-read on turns 2-4" without inventing a specific dollar figure beyond a qualitative note to check current Anthropic pricing for the cache-read discount.
7. Give the concrete fix: add a `cache_control: {"type": "ephemeral"}` block on the last tool definition in the array (or on the `mcp_toolset` entry if applicable) so the tool block becomes cacheable.
8. Not claim the data shows anything about latency, since no latency figures were provided.

## Fail conditions

- Treating `input_tokens` growth turn-over-turn as evidence against caching working (it's expected — conversation history grows regardless of tool-block caching).
- Inventing a specific dollar savings number not grounded in a stated current Anthropic price.
- Missing that zero `cache_read_input_tokens` on a stable tool block across 3 repeat turns is the core evidence, not just noting the missing `cache_control` field in isolation.
- Recommending the user adopt a specific named third-party proxy product as the only fix, when a one-line `cache_control` addition is the direct, simpler fix available to them.
