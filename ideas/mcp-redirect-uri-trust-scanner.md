# Trust Anchor: A Redirect-URI Validation Library and Public Scanner for MCP Authorization

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-12-tool-use-mcp-ecosystem.md · P3
- **Maturity verdict**: PARTIAL — the MCP spec's 2026-07-28 revision hardened general redirect-URI validation (exact pre-registered-URI matching, localhost-redirect warnings via SEP-837, SSRF considerations for Client ID Metadata Documents), but the spec explicitly leaves "trust" undefined for self-hosted servers doing dynamic client registration from anonymous clients. A related Claude Code issue was closed "not planned." The blog author's own test of 119 live MCP servers found 114 (96%) still accept arbitrary redirect URIs — the spec-level fix exists, the practical implementation gap does not.
- **Format**: BOTH

## The Gap

Hacker News, "Letting users trust their own MCP clients, without opening a phishing hole" (2026-11-04, 35 pts / 6 comments, streamvessel.com/blog/mcp-trusted-redirect-uris) names a live, unresolved security gap: MCP's OAuth-style authorization flow for self-hosted servers doing dynamic client registration has no defined trust mechanism, and the author's own scan of 119 live servers found 114 still accepting arbitrary redirect URIs — an open-redirect phishing vector a malicious actor could exploit to steal an authorization code. The spec revision addressed the general case but, by the post's own testing, the fix hasn't propagated into real server implementations.

## The Project

A two-part answer to the gap the post identifies but doesn't ship. First, a drop-in validation middleware/SDK patch for MCP server authors (Node and Python, the two dominant MCP server runtimes) that enforces exact pre-registered-redirect-URI matching plus the SEP-837 localhost warnings by default, so adopting it closes the vulnerability without the server author having to re-derive the spec's security considerations themselves. Second, a public, re-runnable scanner (modeled on the blog author's one-off 119-server test, but maintained and automated) that probes live MCP servers listed in the official registry for arbitrary-redirect-URI acceptance and other known authorization misconfigurations, publishing a scored, dated audit — the MCP-security equivalent of Qualys SSL Labs' public TLS grading — so server operators and downstream client authors can see exposure before relying on a server, not after a phishing incident.

## Tangible Impact

**Population**: Operators of the self-hosted and dynamically-registered MCP servers in the 20,000–30,000-server official registry (as of September 2026) that support OAuth-style client authorization — concretely, the 114 of 119 servers the blog author found vulnerable, and by extension the much larger unscanned population behind them — plus every end user who authorizes an MCP client against one of those servers and is thereby exposed to redirect-based authorization-code theft.
**Mechanism**: Today a server author has to independently read and correctly implement the spec's security-considerations section to avoid the vulnerability, and nothing tells a user or downstream integrator whether a given server did; the middleware collapses "correctly implement redirect-URI validation" into "install this dependency," and the public scanner turns an invisible, unverifiable security posture into a checkable, dated score before anyone authorizes against it.
**Measure**: Re-run of the 119-server-style scan at intervals, tracking the % of scanned servers accepting arbitrary redirect URIs over time (baseline: 96% vulnerable); number/% of registry-listed servers that adopt the middleware within 6 months of launch; red-team success rate of a scripted open-redirect phishing PoC against servers before vs. after middleware adoption.

## Why Now

The spec-level fix is only four months old (2026-07-28 revision) and real server implementations have measurably not caught up (114/119 still vulnerable per last month's independent test) — the window where a drop-in fix and a public scoreboard can move adoption before this becomes an exploited-in-the-wild incident is open now, not hypothetical.

## Skill Angle

An "audit this MCP server's auth flow" skill: hand it a server's source repo or its OAuth-related config/code, and it checks the implementation against the known vulnerability pattern (exact-match redirect-URI validation present or absent, localhost-redirect warning handling, dynamic-client-registration trust gaps) and returns a pass/warn/fail verdict with the specific missing check and a suggested code fix. This is usable standalone by a server author who wants a one-time review without adopting the middleware or waiting for the next scheduled public scan, and differs from the project by being a point-in-time code review rather than an always-on library or a continuously-run public scanner.

## MVP Sketch

2–4 weeks, 1–2 people: ship the Node/Python middleware implementing strict redirect-URI matching plus SEP-837 localhost handling, and a scanner script that re-runs the blog author's probe methodology against a sample of 50 registry-listed servers. Experiment: measure the vulnerable-rate on the sample (validating or updating the 96% baseline) and confirm the middleware, once installed in a test server, closes a scripted open-redirect PoC.

## Risks & Open Questions

- The official MCP Registry or a major host (Anthropic, a client vendor) could ship this validation as a built-in default before adoption spreads, erasing the gap the middleware targets.
- Publicly scoring live servers' security posture is itself sensitive — a scanner that surfaces vulnerable servers before they've patched could be read as a disclosure/vulnerability-research activity requiring a responsible-disclosure process, not a simple launch.
- Server authors who most need this (small, self-hosted, dynamically-registering) may be the least likely to discover or adopt a third-party middleware, limiting real-world uptake regardless of technical quality.
- If the next spec revision defines "trust" for dynamic registration directly (the gap the HN post flags as currently undefined), the middleware's value shrinks to "reference implementation of the spec" rather than filling an open gap.
