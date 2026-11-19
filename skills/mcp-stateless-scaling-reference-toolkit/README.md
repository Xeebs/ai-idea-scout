# MCP Stateless-Scaling Readiness Review

A self-contained prompt template. Paste this whole thing into any AI chat
tool (no Claude Code install required) along with your MCP server's repo URL
or source files, and it will run the review itself.

## What this is for

You run a remote MCP server for internal AI-agent tooling and you're asking
one of: "can we run more than one instance behind our load balancer," "can
we turn off sticky sessions / session affinity," "a pod got killed mid-session
and the client broke," or "we want to autoscale/rolling-deploy this and I'm
not sure it'll survive."

This is a **scaling and infrastructure review** — it does not care which MCP
protocol revision your server speaks, and it will not tell you to rip out
server-side session state in favor of client-held opaque handles (that's a
different, protocol-version-compliance problem with its own tooling). It
assumes you'll keep holding server-side session state and answers a narrower
question: *where* should that state live so any instance can serve any
request.

## What to hand over

1. A link to the repo (or the specific files that set up the server
   transport/connection handling — the file that constructs
   `StreamableHTTPServerTransport`, `createMcpHandler`, `FastMCP(...)`, or an
   equivalent, plus anything that imports a per-connection object from it).
2. The language/framework, if not obvious (TypeScript MCP SDK, Python
   `mcp`/`FastMCP`, Go `go-sdk`, etc.).
3. Optionally, your load-balancer config (is session affinity/stickiness
   currently on?) — not required, just sharpens the review.

**Data source**: Connected when run inside a tool with GitHub access (reads
the repo directly); Manual fallback — paste the transport-setup file and
anything that imports a per-connection object from it. Don't paste the whole
repo; the review only needs the session-lifecycle code path.

## Procedure (what the AI should do with your input)

1. **Find the transport/session-lifecycle code** — the file(s) that
   construct the server transport and anything that imports a per-connection
   or per-session object from it.

2. **Flag in-process state**, categorized as:
   - *Connection-keyed maps/dicts* — a `Map`/`dict`/`sync.Map` keyed by a
     session or connection ID, held as a module-level or closure variable.
   - *Per-connection singleton objects* — something built once per
     WebSocket/SSE/HTTP session and mutated across multiple requests (OAuth
     token caches, in-flight multi-step tool-call state, rate-limit
     counters, per-tenant config cached in memory).
   - *Sticky-affinity assumptions* — code with no re-hydration path if a
     lookup misses, or infra config (`ip_hash`, ALB stickiness cookies)
     assuming one process sees every request for a session.
   - *Unbounded in-memory caches* with no TTL or externalization plan.
   Request-scoped locals, env-loaded constants, and genuinely stateless
   per-request computation are **not** flagged — flagging those is noise.

3. **Recommend a store per flagged spot**, using this rule:
   - Small, short-lived, latency-sensitive data (token caches, rate-limit
     counters, pending interim tool-call state with a TTL of minutes) →
     **Redis** (or equivalent), with an explicit TTL matching the data's
     natural expiry.
   - Larger, needs durability across a full outage, multi-region, or has
     audit/compliance needs → **DynamoDB** (or equivalent managed store).
   - Local dev/CI/single-instance deploys where externalizing is pure
     overhead → an **in-memory dev-mode stub**, explicitly marked
     "do not use beyond one instance."
   Every recommendation gets a one-line reason tied to the data's actual
   size/latency/durability shape — never a bare "externalize this."

4. **Check for sticky-routing infra config** (nginx/Envoy/ALB/k8s ingress
   annotations) and state explicitly whether it's safe to remove yet — only
   once *every* flagged spot above has an externalization plan. Removing
   stickiness before that causes silent data loss, not a visible error.

5. **State confidence explicitly** — static analysis is heuristic; name any
   part of the codebase the review couldn't fully trace (dependency
   injection, an unfamiliar framework) rather than implying full coverage.

## Output format

A single markdown report, in this order:

1. **Verdict**: `STATELESS-READY`, `NEEDS-MIGRATION (<n> spots)`, or
   `NOT ASSESSABLE (<reason>)`.
2. **Findings table**: `File:Line | Pattern | Risk if scaled | Recommended
   store | Why`.
3. **Sticky-routing config**: what was found and whether removing it is
   safe yet.
4. **Prioritized migration plan**: findings ordered by severity, each a
   concrete task (e.g. "Externalize the OAuth token cache in
   `src/auth/session.ts:42` to Redis with a 15-minute TTL matching the
   token's own expiry").
5. **Confidence notes**: what couldn't be fully verified.

## Guardrails

- Never give a clean `STATELESS-READY` verdict from a partial scan.
- Never recommend removing sticky-session infra in the same report that
  still lists open findings.
- Never invent a file path, line number, or snippet that wasn't actually
  read from the repo.
- Never confuse this with MCP protocol-version conformance work (the
  `2026-07-28` stateless spec revision, `server/discover`, Multi Round-Trip
  Requests, removing `initialize`) — that's a separate, already-tooled
  problem. This review is purely about where session *data* lives once you
  add more instances, independent of protocol revision.
- Never recommend a store without a reason tied to the data's actual shape.
