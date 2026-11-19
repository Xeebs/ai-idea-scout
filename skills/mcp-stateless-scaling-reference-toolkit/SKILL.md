---
name: mcp-stateless-scaling-reference-toolkit
description: Reviews a remote MCP server's source for in-process session state that will break when the server is scaled to more than one instance behind an ordinary load balancer, and drafts a prioritized migration plan naming which external store (Redis, DynamoDB, or an in-memory dev stub) fits each flagged spot. Use when a team asks "can we run more than one instance of this MCP server," "do we still need sticky sessions / session affinity," or "why does this break on failover/rolling deploy."
---

# MCP Stateless-Scaling Readiness Review

## When to use this

Reach for this skill the moment someone asks whether their self-hosted remote
MCP server can be horizontally scaled — "can we put a second instance behind
the load balancer," "can we turn off sticky sessions on the ALB/nginx config,"
"a pod got killed mid-session and the client broke," or "we're about to
autoscale/rolling-deploy this and I'm not sure it'll survive." This is a
**scaling and infrastructure review**, not a protocol-version compliance
check: it does not care which MCP protocol revision the server speaks, and it
does not tell you to rip out server-side session state in favor of
client-held opaque handles. It assumes the server will keep holding
server-side session state and asks a narrower, more common question: *where*
should that state live so any instance can serve any request.

Do not use this for: auditing MCP protocol-version conformance (handshake,
`server/discover`, Multi Round-Trip Requests) — that is a different problem
with its own tooling; or for client-side MCP usage questions.

## Inputs

**Data source**: Connected — reads the target team's own MCP server repository via the GitHub API (mature, existing connector: `gh repo view` / `gh api repos/<owner>/<repo>/contents` or an equivalent repo-read tool) to statically identify session-state handling. No manual paste of source is required beyond pointing at the repo. If the user's repo is private and no GitHub API access is configured in the current session, fall back to asking them to paste the specific files that handle connection/session lifecycle (the transport setup file and anything that imports it) — do not ask them to paste the entire repo.

Beyond the repo pointer, the user should hand over:
1. The repo URL or `owner/repo`, plus the branch/ref if not the default.
2. Which language/framework the server uses, if not obvious from the repo (TypeScript `@modelcontextprotocol/server`, Python `mcp`/`FastMCP`, Go `go-sdk`, etc.) — the heuristics below are language-aware.
3. Optionally, their current load-balancer config (sticky/affinity on or off) — sharpens the urgency framing but isn't required to run the review.

## Procedure

1. **Locate the transport/session-lifecycle code.** Search the repo for the file(s) that construct the server transport (`StreamableHTTPServerTransport`, `createMcpHandler`, `FastMCP(...)`, a custom Express/Fastify/Flask handler wrapping the SDK) and anything that imports a per-connection or per-session object from it.

2. **Flag in-process state patterns**, grep-style, language-aware. For each hit, record file:line, a short description, and which category it falls into:
   - **Connection-keyed maps/dicts** — `Map<sessionId, …>`, `dict[session_id]`, `sync.Map` keyed by a connection or session identifier, held as a module-level or closure variable.
   - **Per-connection singleton objects** — an object constructed once per WebSocket/SSE/HTTP-session and mutated across multiple requests (OAuth token caches, in-flight Multi Round-Trip "pending input" state, rate-limit counters, per-tenant config loaded once and cached in memory).
   - **Sticky-affinity assumptions** — code or comments that assume "this process will see every request for this session" (e.g. no re-hydration path if the map lookup misses), or infra config (nginx `ip_hash`, ALB stickiness cookie) referenced in deploy files.
   - **In-memory caches with no TTL/externalization** used for anything beyond pure request-scoped computation.
   Do **not** flag: request-scoped locals, module-level constants/config loaded from env/files, or genuinely stateless per-request derived data — flagging those produces noise that undermines trust in the report.

3. **For each flagged spot, recommend a store**, using this decision rule:
   - Small, short-lived, latency-sensitive (OAuth token cache, rate-limit counters, pending-MRTR-interim-state with a TTL measured in minutes) → **Redis** (or equivalent in-memory KV) with an explicit TTL matching the data's natural expiry.
   - Larger, needs durability across a full outage, multi-region, or has audit/compliance requirements (persisted per-tenant session records, anything a client might reasonably expect to survive a multi-hour outage) → **DynamoDB** (or equivalent managed document/KV store).
   - Local dev / CI / a single-instance deploy where externalizing would be pure overhead → **in-memory dev-mode stub** behind the same adapter interface, explicitly flagged as "do not use beyond one instance."
   Name the store choice and a one-line reason per spot — never just "externalize this," which leaves the actual engineering decision undone.

4. **Check for sticky-routing infra config** in the repo (nginx/Envoy/ALB/k8s ingress annotations) if present, and call out explicitly whether removing it is safe yet (i.e., only after every flagged spot above has an externalization plan — removing stickiness before that will cause silent data loss, not just an error).

5. **Write the report** (see Output format). Order findings by severity: anything that would cause silent wrong-tenant data leakage or lost in-flight tool calls on a cache miss ranks above anything that merely degrades performance.

6. **State confidence explicitly.** Static analysis on arbitrary source is heuristic — note which parts of the codebase you could not fully trace (e.g. state passed through a dependency-injection framework, or a language/framework the heuristics above don't cover well) rather than implying full coverage.

## Output format

A single markdown report with these sections, in this order:

1. **Verdict** — one line: `STATELESS-READY`, `NEEDS-MIGRATION (<n> spots)`, or `NOT ASSESSABLE (<reason>)`.
2. **Findings table** — columns: `File:Line | Pattern | Risk if scaled | Recommended store | Why`. One row per flagged spot from step 2–3.
3. **Sticky-routing config** — what was found (or "none found in repo — check infra config separately") and whether it's safe to remove yet.
4. **Prioritized migration plan** — a numbered list ordering the findings table by severity, each item phrased as a concrete task ("Externalize the OAuth token cache in `src/auth/session.ts:42` to Redis with a 15-minute TTL matching the token's own expiry").
5. **Confidence notes** — what the review could not fully verify.

## Guardrails

- Never claim a server is `STATELESS-READY` from a partial scan — if any file in the transport/session path couldn't be read or doesn't match a known framework's patterns, the verdict must be `NOT ASSESSABLE` or carry an explicit caveat, not a clean bill of health.
- Never recommend removing sticky-session infra config as part of the same report that still has open findings — that ordering causes silent data loss, not a visible error, which is the worst failure mode for this skill to cause.
- Never invent a file path, line number, or code snippet not actually present in the fetched repo contents — every finding must trace to a real read.
- Never conflate this with MCP protocol-version conformance (the `2026-07-28` stateless spec revision, `server/discover`, Multi Round-Trip Requests, removing `initialize`). That is a different, already-tooled problem (e.g. protocol-conformance checkers); this skill is about where session *data* physically lives when you add more instances, regardless of which protocol revision the server speaks.
- Never recommend a store without a one-line reason tied to the data's actual size/latency/durability shape — a bare "use Redis for everything" is not a migration plan.
