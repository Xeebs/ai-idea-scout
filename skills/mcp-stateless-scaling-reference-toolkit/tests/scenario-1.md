# Scenario 1 — TypeScript MCP server with an in-process OAuth cache and MRTR pending-state map

## Input

A team hands over this repo snippet (`src/transport.ts`) from their internal
remote MCP server, built on `@modelcontextprotocol/server`, currently running
behind an AWS ALB with sticky sessions enabled:

```ts
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/server";

// Keyed by Mcp-Session-Id. Holds the exchanged OAuth access token so we
// don't re-auth on every tool call.
const sessionTokenCache = new Map<string, { token: string; expiresAt: number }>();

// Keyed by Mcp-Session-Id. Holds in-flight multi-step tool calls waiting on
// a client follow-up (e.g. elicitation/create responses).
const pendingToolCalls = new Map<string, { toolName: string; partialArgs: unknown }>();

export function buildTransport(sessionId: string) {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: () => sessionId,
    onsessioninitialized: (id) => {
      sessionTokenCache.set(id, { token: "", expiresAt: 0 });
    },
  });

  transport.onclose = () => {
    sessionTokenCache.delete(sessionId);
    pendingToolCalls.delete(sessionId);
  };

  return transport;
}

export function getCachedToken(sessionId: string) {
  return sessionTokenCache.get(sessionId);
}

export function recordPendingCall(sessionId: string, toolName: string, partialArgs: unknown) {
  pendingToolCalls.set(sessionId, { toolName, partialArgs });
}
```

Deploy config excerpt (`infra/alb.tf`):
```
stickiness {
  enabled = true
  type    = "lb_cookie"
  cookie_duration = 3600
}
```

The team asks: "We want to run 3 instances behind the ALB so a deploy doesn't
drop every open session. What breaks, and what do we actually need to do?"

## Pass criteria

- [ ] Flags `sessionTokenCache` as a connection-keyed map holding OAuth token
      state, with the correct file reference (`src/transport.ts`, the `Map`
      declaration line and the `getCachedToken`/`onsessioninitialized` usage
      lines).
- [ ] Flags `pendingToolCalls` as a connection-keyed map holding in-flight
      multi-step tool-call state, correctly identified as higher risk than
      the token cache (a cache miss here silently drops a client's in-flight
      request rather than just forcing a re-auth).
- [ ] Recommends Redis with a short TTL for `pendingToolCalls` (short-lived,
      latency-sensitive) and Redis with a TTL matching token expiry for
      `sessionTokenCache` — not DynamoDB for either, since neither needs
      multi-hour durability per the scenario's own data.
- [ ] Identifies the `stickiness` block in `infra/alb.tf` and explicitly
      states it is **not yet safe to remove** because both maps still need
      externalization plans.
- [ ] Verdict is `NEEDS-MIGRATION (2 spots)`, not `STATELESS-READY`.
- [ ] Does not invent any additional file or line not present in the input.
- [ ] Does not drift into protocol-version-conformance advice (no mention of
      `server/discover`, `initialize` removal, or MRTR compliance as if that
      were the task) — the ask here is scaling, not the 2026-07-28 spec.

## Fail criteria

- [ ] A bare "externalize everything to Redis" with no per-spot reasoning.
- [ ] Recommending stickiness removal before both maps have a plan.
- [ ] Treating the `onsessioninitialized`/`onclose` lifecycle hooks
      themselves as the problem (they aren't — the problem is what they
      mutate: in-process maps).
