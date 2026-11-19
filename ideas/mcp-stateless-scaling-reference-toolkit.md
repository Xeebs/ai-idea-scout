# Stateless Standard: A Reference Architecture and Migration Toolkit for Horizontally-Scalable MCP Servers

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-19-tool-use-mcp-ecosystem.md · P7
- **Maturity verdict**: PARTIAL — `vitemcp/server` (25★, pushed yesterday, a TypeScript framework for building stateless MCP servers) plus individual production examples (KalvadTech's Redmine/Woodpecker servers, PeronGH's Cloudflare-Workers-based servers) show real adoption beyond newsletter talk, but no dominant reference architecture, adoption report, or sticky-vs-stateless benchmark exists — early and scattered.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the target team's own MCP server repository via the GitHub API (mature, existing connector) to statically identify session-state handling (in-memory maps, per-connection objects, sticky affinity assumptions) and produce a migration plan; no manual paste of source required beyond pointing at the repo.

## The Gap

dev.to's "AI Weekly: Coding Tool Shakeups and Stateless MCP" and its companion "Codex Goes Long, MCP Goes Stateless," plus portkey.ai's ecosystem roundup, all independently frame remote MCP servers moving away from sticky-session state as the direction the spec and community are heading — but coverage sits at the newsletter/summary level. The one dedicated framework (`vitemcp/server`) is 25 stars old and days-fresh; teams otherwise hand-roll session externalization themselves or default to sticky load-balancer config, with no reference architecture or comparative benchmark to copy from.

## The Project

A reference architecture plus migration toolkit for converting a sticky-session remote MCP server into a stateless one that scales behind an ordinary load balancer: a thin adapter library that externalizes per-connection session state to a pluggable store (Redis, DynamoDB, or an in-memory dev mode), a static-analysis pass over an existing server's source (via the GitHub API) that flags exactly where session state is currently held in-process, and a benchmark harness comparing throughput/latency/failover behavior of the sticky vs. stateless version of the same server under horizontal scale-out. The deliverable is not a new protocol extension — it's the missing "how do I actually migrate" artifact the newsletter coverage describes wanting but doesn't provide.

## Tangible Impact

**Population**: backend/platform engineers self-hosting remote MCP servers for internal AI-agent tooling at a scale where a single instance or sticky-session pool becomes a bottleneck — a population without a precise count in the digest, but bounded below by every team past `vitemcp`'s and KalvadTech's early-adopter stage who will hit the same scaling wall once they outgrow one instance.
**Mechanism**: Today, scaling a remote MCP server beyond one instance either requires sticky-session infrastructure (complicating autoscaling, multi-region failover, and rolling deploys) or a from-scratch session-externalization rewrite with no reference to copy. A drop-in adapter plus a migration report turns that rewrite into a scoped, measurable task instead of an open-ended architecture problem each team solves alone.
**Measure**: requests/sec throughput and p99 latency of the stateless migration vs. the original sticky version under an identical horizontal-scale-out load test; number of real servers successfully migrated using the toolkit without a manual rewrite; error/failover-time delta when an instance is killed mid-session, stateless vs. sticky.

## Why Now

The spec-direction discussion and the first dedicated framework both appeared within the last 30 days — early enough that no reference architecture has hardened yet, which is exactly the window where a benchmarked migration toolkit can become the thing teams copy instead of each re-deriving their own.

## Skill Angle

A "is my MCP server stateless-ready" review skill: given a repo URL (or pasted server source for a team without GitHub access configured), Claude statically walks the session-handling code, flags every in-process state assumption (connection-keyed maps, per-session objects never externalized), and drafts a prioritized migration plan naming which store (Redis/DynamoDB/etc.) fits each flagged spot. This is a one-shot design review usable standalone, distinct from the project's actual adapter library and benchmark harness.

## MVP Sketch

3–4 weeks, 1–2 people: build the Redis-backed adapter for one popular MCP server framework, a static-analysis script flagging in-process state via AST pattern matching, and a load-test harness (e.g. k6) hitting both versions of a sample server. Experiment: migrate one real open-source MCP server end to end, publish the before/after benchmark, and see whether the before/after numbers are compelling enough that other maintainers adopt the adapter.

## Risks & Open Questions

- If the MCP spec itself standardizes a stateless session model, this toolkit's adapter layer could be obsoleted by a built-in mechanism.
- Static analysis for "is this state in-process" is inherently heuristic across arbitrary server implementations/languages; false negatives on subtle state leaks are likely.
- Externalizing state to Redis/DynamoDB adds a new infrastructure dependency and latency cost that some lightweight servers may not want to pay.
- Only one dedicated framework and a handful of individual production examples exist — the toolkit may be solving a problem most teams haven't hit yet, which could blunt early adoption.
