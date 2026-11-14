# Scenario 2 — custom agent harness, MCP connection recreated per turn, misconfigured cache-key stability

## Setup

A team built a custom Python agent loop that connects to 5 MCP servers to answer multi-turn analytics questions. To keep things simple, their harness calls `tools/list` and rebuilds the in-memory tool catalog fresh at the start of every single turn (rather than once per session), even though the underlying servers and tools never actually change mid-session. They've added a `cache_control` breakpoint on the last tool in the array (following a blog post), but their dashboard still shows `cache_creation_input_tokens` firing on nearly every turn instead of `cache_read_input_tokens`. They paste 3 turns of usage data plus a one-line description of their harness's tool-loading behavior.

## Input provided to the skill

**Provider**: Anthropic (Messages API)

**Tool set**: 5 MCP servers, ~40 tools, confirmed unchanged at the server/tool level across the session. User notes: "our harness calls `tools/list` on every turn and rebuilds the `tools` array from scratch before sending the request — we do have `cache_control` on the last tool."

**Per-turn usage objects**:

```
Turn 1: {"input_tokens": 980, "cache_creation_input_tokens": 31200, "cache_read_input_tokens": 0, "output_tokens": 220}
Turn 2: {"input_tokens": 1140, "cache_creation_input_tokens": 31180, "cache_read_input_tokens": 0, "output_tokens": 300}
Turn 3: {"input_tokens": 1050, "cache_creation_input_tokens": 31310, "cache_read_input_tokens": 0, "output_tokens": 275}
```

No latency data provided.

## Pass criteria

The diagnostic output must:
1. Recognize that a `cache_control` breakpoint IS present (user stated so), distinguishing this from scenario 1's root cause.
2. Recognize the real signal: `cache_creation_input_tokens` is being paid on every turn (not just the first) at nearly the same size (~31k) as the tool block, while `cache_read_input_tokens` stays at 0 — meaning a *new* cache entry is being written each turn instead of the previous one being read, even though the breakpoint exists and the underlying tools haven't changed.
3. Correctly attribute this to cache-key instability caused by rebuilding the tool catalog from scratch each turn (e.g., non-deterministic key/property ordering from `tools/list` responses, or a timestamp/session-id baked into the serialization) rather than concluding "no breakpoint" (which would be wrong here) or "tool set changed" (also wrong — the user confirmed the underlying tools are unchanged).
4. Reach a **Verdict** of `MISCONFIGURED`, not `CONFIRMED` or `NOT AN ISSUE`.
5. Give the concrete fix: persist a canonicalized (stable key ordering, no embedded session-specific values), hashed serialization of the merged tool catalog once per session, and only re-serialize/re-key when a hash diff shows the underlying `tools/list` output actually changed — rather than rebuilding and resending it fresh every turn.
6. Note in the caveat line that confirming the exact non-determinism source (ordering vs. an embedded value) would require seeing the raw serialized `tools` array from two consecutive turns byte-for-byte, which wasn't provided.
7. Not report a latency estimate, since none was given.

## Fail conditions

- Concluding "add a `cache_control` breakpoint" as the fix when the user already stated one exists — this scenario tests whether the skill reads given context instead of pattern-matching to scenario 1's fix.
- Misreading `cache_creation_input_tokens` > 0 as proof caching is working (cache creation is a write, not a hit — repeated writes with zero reads is still the core problem).
- Classifying this as `CONFIRMED` (that verdict is reserved for "no breakpoint at all" per scenario 1) instead of the more precise `MISCONFIGURED`.
