---
name: mcp-redirect-uri-trust-scanner
description: Audits a self-hosted MCP server's OAuth-style authorization code (redirect-URI validation, localhost/SEP-837 handling, dynamic-client-registration trust gaps) against the MCP spec's 2026-07-28 security considerations and the open-redirect pattern found vulnerable in 114 of 119 live servers. Use when a user is building, reviewing, or about to expose a self-hosted MCP server that implements OAuth/dynamic client registration and wants a one-time check before shipping.
---

# MCP Redirect-URI Trust Scanner

## When to use this

The user is writing, maintaining, or about to deploy a self-hosted MCP server that implements OAuth-style authorization — especially one that supports Dynamic Client Registration (DCR), letting MCP clients self-register without a pre-vetted allowlist. They want to know, before shipping or exposing the server, whether their `redirect_uri` handling is exploitable for authorization-code theft via an open-redirect — the exact gap the MCP spec's 2026-07-28 revision addressed but which an independent scan found still unpatched in 114 of 119 live servers tested. This is a **point-in-time code review**, not a continuously-running scanner and not a drop-in library — it's for someone who wants a verdict on their own code right now.

Do not use this for: auditing a server you don't control and can't read the source of (that needs a live probe, which this skill does not perform); general MCP tool-permission or prompt-injection audits (different vulnerability class entirely); OAuth providers unrelated to MCP.

## Inputs

**Data source**: Manual — the user pastes or uploads the actual source files that implement their MCP server's authorization endpoints: the `/authorize` handler, the dynamic client registration (`/register`) handler if DCR is supported, and wherever `redirect_uri` is compared, stored, or validated. No live connector, no running-server probe — if the code isn't in the conversation, this skill cannot see it.

Required:
1. The source code above (paste directly, or point to specific files if working inside a repo Claude already has file access to).
2. Language/runtime: Node.js or Python (the two dominant MCP server runtimes) — the check logic generalizes to other languages, but the suggested-fix code samples are Node/Python.

Helpful but optional:
3. Whether the server supports Dynamic Client Registration at all (if not, skip check 3 below — mark it N/A, not FAIL).
4. The specific OAuth/MCP SDK or library in use (e.g., `@cloudflare/workers-oauth-provider`, `mcp-sdk`, a hand-rolled implementation) — libraries with known CVEs (e.g., CVE-2025-4143) get flagged by name if recognized.

## Procedure

Run these five checks in order against the pasted code. For each, find the actual comparison/validation logic — never infer a verdict from the library name or framework alone without seeing the code that calls it.

**Check 1 — Exact-match redirect-URI validation.**
Find where an incoming `redirect_uri` (at `/authorize` or at token redemption) is checked against the value registered for that client. PASS requires a full string-equality or parsed-URL-equality comparison (scheme + host + port + path, all exact) against a pre-registered value. FAIL if the match is prefix-based, substring-based, regex/wildcard, domain-only (ignoring path), or if there's any code path that accepts a `redirect_uri` the client supplies with no registered value to compare against.

**Check 2 — Localhost/loopback handling (SEP-837).**
Find how `redirect_uri` values pointing at `127.0.0.1`, `localhost`, or `::1` are treated. PASS requires scheme+host+path to still match exactly while allowing the port to vary (the SEP-837-sanctioned exception for CLI/desktop clients using an ephemeral local port), ideally paired with a visible warning/consent step. FAIL if loopback URIs get the same wildcard tolerance as a misconfigured general case, or if no special-casing exists and loopback just happens to pass through an already-broken Check 1.

**Check 3 — Dynamic Client Registration trust gap.**
Skip (mark N/A) if DCR isn't supported. Otherwise: find where a self-registering client's `redirect_uri` is captured at registration time. PASS requires that value to be pinned to that client ID and re-validated with exact match on every later `/authorize` call — a registered client cannot supply a different `redirect_uri` at authorization time than the one it registered. FAIL if registration doesn't persist a redirect_uri, or if `/authorize` accepts any `redirect_uri` the request supplies regardless of what was registered.

**Check 4 — URL-parsing correctness (userinfo/host-confusion bypass).**
Find whether the comparison in Check 1 uses a proper URL parser (splitting scheme/userinfo/host/port/path) or naive string prefix/`startsWith` matching. FAIL if an attacker-controlled value like `https://trusted-host.com@evil.com/callback` or `https://trusted-host.com.evil.com/callback` would pass a `startsWith("https://trusted-host.com")` style check. PASS if the comparison parses the URL and checks host/port/path as discrete fields.

**Check 5 — Authorization-code binding at redemption.**
Find the `/token` handler that exchanges an authorization code. PASS requires the exchange to verify the `redirect_uri` supplied at redemption matches the one used at the original `/authorize` call (and/or PKCE `code_verifier` binding), so a stolen code can't be redeemed from a different redirect target. FAIL if the token endpoint accepts the code without re-checking `redirect_uri` or PKCE.

If the pasted code doesn't contain enough to resolve a check either way, mark it **UNKNOWN** and name the exact file/function that's missing — never default an unresolved check to PASS.

## Output format

```
## MCP Redirect-URI Trust Scan

**Overall verdict**: PASS | WARN | FAIL
(FAIL if any check is FAIL. WARN if any check is UNKNOWN and none are FAIL. PASS only if every applicable check is PASS or N/A.)

| # | Check | Status | Evidence | Spec reference |
|---|-------|--------|----------|-----------------|
| 1 | Exact-match redirect-URI validation | PASS/WARN/FAIL/UNKNOWN | file:line or quoted snippet | MCP Authorization spec 2026-07-28, security-considerations §redirect_uri |
| 2 | Localhost/SEP-837 handling | ... | ... | SEP-837 |
| 3 | DCR trust gap | ... (or N/A — DCR not supported) | ... | MCP spec, dynamic client registration section |
| 4 | URL-parsing correctness | ... | ... | — |
| 5 | Auth-code binding at redemption | ... | ... | OAuth 2.1 / PKCE |

### Highest-priority fix
One paragraph naming the single most exploitable FAIL/UNKNOWN and why (what an attacker does with it, concretely — e.g. "an attacker sends the victim a crafted authorization link; the victim's MCP client completes the OAuth dance; the authorization code lands at the attacker's redirect_uri instead of the legitimate client's").

### Suggested fix
A concrete code diff or snippet in the user's stated language (Node or Python) for the highest-priority fix — not pseudocode, runnable logic the user can adapt directly.

### Everything else found
One line per remaining non-PASS check with its own minimal fix suggestion.
```

## Guardrails

- Never mark a check PASS without having actually seen the comparison/validation code — a library name, framework reputation, or the absence of an obvious red flag is not evidence of PASS. Mark UNKNOWN and say what file is missing instead.
- Never report this as a live vulnerability scan of a running server, a penetration test, or a comprehensive security audit — it is a static read of the five specific checks above, against one known vulnerability class (open-redirect / authorization-code theft via redirect_uri). Say so explicitly in the output if the user seems to be treating it as more than that.
- Never invent a CVE ID, a stats claim ("X% of servers do this"), or a severity score beyond what's directly observable in the pasted code — the 114/119 figure is background motivation for why this check exists, not a number to apply to the user's own server.
- Never recommend "just disable Dynamic Client Registration" as the primary fix when exact-match validation is achievable — DCR is a legitimate feature; the fix is making it safe, not removing it, unless the user explicitly says they don't need DCR.
- If the pasted code uses a library/SDK with a known CVE pattern (e.g., the 2025 `workers-oauth-provider` redirect_uri allowlist bug), name the CVE and tell the user to check their pinned version — don't assume they're on a patched version without evidence.
- If no code is provided at all — only a description or a URL to a server the user doesn't control the source of — say this skill needs the actual source and cannot produce a verdict from a description alone.
