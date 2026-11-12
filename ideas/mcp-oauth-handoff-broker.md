# Relay: A Cross-Host OAuth Broker for MCP Server Sign-In

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-11-tool-use-mcp-ecosystem.md · P1
- **Maturity verdict**: OPEN — GitHub search for `MCP OAuth` turned up only server-side auth infra (casdoor 14.8k★, mcp-oauth-gateway 60★, mcp-gateway 92★, giantswarm/mcp-oauth 16★), none addressing host-side UI failing to surface the sign-in URL. WebSearch found a live cluster of open/unresolved reports across different hosts (Cursor forum, Claude Desktop/claudeissues.com) spanning Feb–Nov 2026 with no shipped cross-host fix or shared library.
- **Format**: BOTH

## The Gap

`openai/codex` issue #57093 (2026-10-26, 13 reactions, 4 comments) names two distinct unresolved OAuth-surfacing failures in one host alone: the sign-in URL for a plugin MCP server never appears, stalling installation mid-flow. WebSearch turned up the same symptom independently reported against Cursor ("Authenticate button missing, browser never opens") and Claude Desktop ("auth URL surfaced but browser auto-open silently disabled", "infinite about:blank loop") — three unrelated hosts, three unresolved threads, no shared fix.

## The Project

A local broker daemon that performs the OAuth handshake itself instead of trusting each host's sign-in UI. It reads an MCP server's auth manifest, drives the OAuth redirect/device flow directly (own browser-open logic, own stable local callback listener), stores the resulting token in the OS keychain, and hands the host an already-authenticated local MCP proxy endpoint — so a host's buggy URL-surfacing code is never in the critical path. Components: an auth-manifest parser per MCP server, a host-agnostic OAuth client, a keychain-backed token store, and thin per-host adapters that register the proxy endpoint in each host's own MCP config format.

## Tangible Impact

**Population**: Developers installing OAuth-gated MCP servers (anything wrapping a SaaS API — Gmail, Slack, Notion, GitHub) across desktop agent hosts. The official MCP Registry listed roughly 20,000–30,000 servers by Sept 2026; a meaningful share require OAuth, and the failure has now surfaced independently in at least three major hosts (Codex, Cursor, Claude Desktop) within one month — this is not a one-host bug.
**Mechanism**: Today a buggy host silently stalls installation with no recourse but digging through logs. Routing the handshake through a broker that doesn't depend on any host's sign-in UI turns a stuck, unrecoverable install into a reliable one regardless of which host's bug is in play that week.
**Measure**: % of attempted OAuth MCP installs reaching a working authenticated state without manual log-digging; median time-to-first-successful-tool-call after adding an OAuth server; reduction in "auth URL never appears" style reports on forums/issue trackers for adopting hosts.

## Why Now

The registry is now large and official (20k–30k servers, Linux Foundation-governed), many gated by OAuth, while three independent hosts have each shipped their own unresolved sign-in bug in the last month with no shared library anyone has built yet to fix it once.

## Skill Angle

A "diagnose my stuck MCP sign-in" skill: the user hands over the host name, the stuck server's config, and whatever logs they have. The skill matches the symptoms against known failure fingerprints (URL never surfaced, auto-open disabled, infinite `about:blank` loop, missing auth button) and returns a specific diagnosis plus manual remediation steps (e.g., extract the URL from verbose logs, disable an auto-open flag, force device-code flow) — useful standalone, without the broker running, and differs from the project by being a one-shot triage rather than a persistent fix.

## MVP Sketch

2–4 weeks, 1–2 people: build the broker for 2–3 popular OAuth-gated servers (Notion, Google, GitHub) against two hosts (Claude Desktop, Cursor). Experiment: measure successful-connect rate and time-to-first-tool-call through the broker versus each host's native (broken) flow.

## Risks & Open Questions

- Hosts may each patch their own bug before a cross-host broker gains adoption, eroding the case for a shared fix.
- Brokering tokens for third-party servers is itself a security-sensitive position — must enforce least-privilege scopes and never persist beyond the keychain.
- Each host exposes MCP config differently, so every new host needs its own thin adapter — adoption cost scales with host count.
- This is a workaround for host bugs, not a root fix; if the MCP spec itself standardizes sign-in UX, the broker's value shrinks.
