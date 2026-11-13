# MCP Redirect-URI Trust Scanner

A paste-into-any-AI-chat-tool prompt that audits a self-hosted MCP (Model Context Protocol) server's OAuth authorization code for a specific, documented vulnerability class: accepting an arbitrary `redirect_uri`, which lets an attacker steal an authorization code via a phishing-style open redirect. The MCP spec's 2026-07-28 revision tightened the rules on this, but an independent test of 119 live MCP servers found 114 (96%) still vulnerable in practice. This is a one-time code review for your own server, not a live scanner of someone else's.

## When to use this

You're building, maintaining, or about to deploy a self-hosted MCP server that implements OAuth-style authorization — particularly one that supports Dynamic Client Registration (DCR), where MCP clients can self-register without being pre-vetted. Before shipping it or exposing it to real users, you want a concrete pass/warn/fail on whether your redirect-URI handling is exploitable.

This does **not** work if:
- You don't have the source code (this is a static code read, not a live probe of a running server you don't control).
- You're looking for a general security audit (prompt injection, tool permissions, etc.) — this covers exactly one vulnerability class.

## What to paste

1. The source code of your MCP server's authorization endpoints: the `/authorize` handler, the `/register` (Dynamic Client Registration) handler if you have one, and wherever `redirect_uri` gets compared, stored, or validated.
2. Say whether you're on Node.js or Python (the fix suggestions below are written for those two, but the checks apply to any language).
3. Optional: say whether you support Dynamic Client Registration at all, and which OAuth/MCP library you're using if any (e.g., `@cloudflare/workers-oauth-provider`, a vendored MCP SDK, hand-rolled).

No live API, no connector, no running server access needed — this works entirely from the code you paste.

## The prompt

Paste this, followed by your code:

> You are auditing my MCP server's OAuth authorization code for the open-redirect / authorization-code-theft vulnerability pattern described in the MCP spec's 2026-07-28 security-considerations revision. Run these five checks against the code I'm pasting below. For each, find the actual validation logic in my code — do not assume a library is safe just because of its name; if you can't find enough in what I pasted to resolve a check, say UNKNOWN and name exactly what file or function you'd need to see, never default to PASS.
>
> **Check 1 — Exact-match redirect-URI validation.** Find where an incoming `redirect_uri` is checked against what's registered for that client. PASS only for full exact comparison (scheme+host+port+path all exact) against a pre-registered value. FAIL for prefix/substring/regex/wildcard/domain-only matching, or any path that accepts a client-supplied `redirect_uri` with nothing registered to compare it to.
>
> **Check 2 — Localhost/loopback handling.** Find how `127.0.0.1`/`localhost`/`::1` redirect URIs are treated. PASS requires scheme+host+path to still match exactly while the port is allowed to vary (the standard allowance for CLI/desktop clients using an ephemeral local port). FAIL if loopback gets the same loose tolerance as a broken general case.
>
> **Check 3 — Dynamic Client Registration trust gap.** Skip as N/A if I don't support DCR. Otherwise: find where a self-registering client's `redirect_uri` is captured at registration and confirm it's pinned to that client ID and re-checked by exact match on every later authorization request. FAIL if a registered client can supply a different `redirect_uri` at authorization time than what it registered.
>
> **Check 4 — URL-parsing correctness.** Find whether the redirect_uri comparison uses a proper URL parser or naive string matching. FAIL if something like `https://trusted-host.com@evil.com/callback` or `https://trusted-host.com.evil.com/callback` would pass a `startsWith`-style check against `https://trusted-host.com`.
>
> **Check 5 — Authorization-code binding at redemption.** Find the token-exchange handler. PASS requires it to verify the `redirect_uri` (and/or PKCE `code_verifier`) matches what was used at the original authorization request, so a stolen code can't be redeemed elsewhere.
>
> Give me back a table: check name, status (PASS/WARN/FAIL/UNKNOWN/N-A), the exact evidence (file/line or quoted snippet) you based it on, and the relevant spec concept. Then call out the single highest-priority fix in plain language — what an attacker would actually do with the gap — followed by a concrete runnable code snippet (not pseudocode) in my stated language that fixes it. List any remaining non-PASS checks with a one-line fix each.
>
> Rules for you to follow: never report this as a live vulnerability scan, penetration test, or comprehensive audit — it's a static read against five specific checks for one vulnerability class. Never invent a CVE, a statistic about what percentage of servers do something, or a severity score beyond what you can see in my code. Never tell me to just disable Dynamic Client Registration as the fix unless I say I don't need it — the fix is making DCR safe, not removing it. If you recognize my library as having a known CVE pattern (e.g. the 2025 workers-oauth-provider redirect_uri allowlist bug), name it and tell me to check my pinned version.
>
> My language/runtime: [Node.js or Python]
> Do I support Dynamic Client Registration: [yes/no]
> My OAuth/MCP library (if any): [name, or "hand-rolled"]
>
> My authorization code:
> [paste your /authorize, /register, and redirect_uri validation/token-exchange code here]

## What you get back

A table scoring the five checks PASS/WARN/FAIL/UNKNOWN/N-A with evidence cited from your own code, an overall verdict (FAIL if any check fails, WARN if anything is unresolved, PASS only if everything applicable passed), the single highest-priority exploit path explained in plain language, a runnable code fix for it, and one-line fixes for anything else that didn't pass.

## Limits — read this before you rely on the output

- This is a review of the code you paste, not a scan of a live server. If you want to know whether a server you don't operate is vulnerable, this skill can't tell you that — it needs the source.
- It checks one vulnerability class (redirect-URI / open-redirect authorization-code theft). It says nothing about prompt injection, tool-permission scope, token storage, or any other MCP security concern.
- A PASS from this review is not a certification — it means the specific five checks didn't find a gap in what you showed it. Get a second opinion before treating a self-hosted auth implementation as production-ready for real users' credentials.
