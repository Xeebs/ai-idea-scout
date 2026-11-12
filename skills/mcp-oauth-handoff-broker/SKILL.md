---
name: mcp-oauth-handoff-broker
description: Diagnoses a stuck MCP (Model Context Protocol) server OAuth sign-in flow — no auth URL, dead browser-open, infinite about:blank, stale credentials — by matching the user's host, symptom, and logs against a fingerprint table of known cross-host OAuth-surfacing bugs, then returns a ranked diagnosis and manual remediation steps. Use when an MCP server install or reconnect stalls during sign-in and the host gives no useful error.
---

# MCP OAuth Handoff Triage

## When to use this

Reach for this when a user is installing or reconnecting an OAuth-gated MCP server (Notion, Gmail, Slack, GitHub, or any SaaS-wrapped server) inside a host — Claude Desktop, Claude Code, Cursor, Codex, or similar — and the sign-in flow has stalled: no auth URL ever appears, a browser opens to a blank or looping page, the "Authenticate" control is missing or unresponsive, or the host reports "connected" while every tool call still fails as unauthenticated. The host's own error message is typically useless ("couldn't connect," silence, or nothing at all).

This is a **one-shot diagnostic triage**, not a running fix. It does not install anything, does not perform the OAuth handshake itself, and does not persist across sessions — it reads what the user hands over, matches it against known failure patterns, and hands back a diagnosis plus steps the user runs by hand. If the user wants a persistent, host-agnostic fix that intercepts every future OAuth handshake, say plainly that this skill doesn't do that — it's a point-in-time unstick.

## Inputs

Required — ask for anything missing rather than guessing:
1. **Host and version**: which client (Claude Desktop, Claude Code, Cursor, Codex, other) and version/build if known.
2. **MCP server**: name and, if known, the OAuth provider behind it (Notion, Google, GitHub, Slack, custom).
3. **Symptom in the user's own words**: what they see right now — no URL, a browser window stuck somewhere, a missing button, an error toast, or "it says connected but nothing works."

Strongly recommended, sharpens the diagnosis:
4. **Logs or console output**, if the host exposes any (verbose/debug logs, browser devtools network tab, terminal output). Before pasting, tell the user to strip any OAuth token, authorization code, or client secret from the log text — the skill does not need secret values to diagnose, only URLs, status codes, and error strings. If a secret-shaped string (long opaque token, `code=`, `access_token=`) appears anyway, redact it in the report and tell the user it was present.
5. **What's already been tried**: restart, different browser, re-adding the server, etc.

If required inputs are missing, proceed on what's given and say explicitly which fingerprint checks couldn't be run for lack of information — never invent a host behavior or log line the user didn't provide.

## Procedure

1. **Normalize the report**: host + version, server + provider, symptom, and any log excerpt, each stated plainly even if "unknown" for some.

2. **Match against the fingerprint table below.** For each row, check whether the stated symptom and any log evidence are consistent with it. A row only counts as a match if the user's actual symptom description lines up — do not force-fit a fingerprint onto a vague symptom.

   | Fingerprint | Typical symptom | Typical evidence in logs | Known-affected hosts (as of Nov 2026) |
   |---|---|---|---|
   | URL never surfaced | Install/connect hangs; no sign-in link or button ever shown | Install log shows server registered, no `auth_url` or redirect logged | Plugin-based MCP installs (e.g. Codex-style plugin flows) |
   | Auto-open disabled silently | Host claims it opened a browser; nothing opens | Log shows an auth URL was generated but no corresponding OS browser-launch call | Desktop hosts with a configurable or buggy auto-open setting |
   | Infinite `about:blank` loop | Browser window opens and reloads a blank page repeatedly, never resolves | Browser history/network tab shows repeated navigation to `about:blank` with no outbound request | Desktop hosts using an embedded or managed browser view |
   | Stuck on provider's post-login page | Browser shows the IdP's "signing you in" / consent-granted page indefinitely after the user actually approved access | Provider-side logs (if visible) show approval granted; host shows no corresponding callback received | Flows where the callback redirect silently fails after a successful provider-side approval |
   | Callback never reaches client (environment-blocked) | Everything above looks normal, but the host never registers success | Client is running inside WSL, a remote/SSH session, or behind a strict corporate proxy/VPN; localhost callback port is not reachable from the browser's actual network context | Terminal/CLI-launched hosts (e.g. inside WSL) reached via a browser on a different network boundary |
   | Discovery fails before login starts | Host immediately errors ("couldn't reach," "invalid server") before any sign-in UI appears | Request to the server's `/.well-known/oauth-authorization-server` or equivalent metadata path returns 404 or a non-JSON body | Any host, when the MCP server's auth metadata endpoint is misconfigured |
   | Flow stalls after registration | Client registration succeeds (visible in logs), but the authorize/token endpoints are never called | Server logs show a registration request, no subsequent `/authorize` or `/token` hit | Hosts that register a client but fail to open/redirect to the resulting authorize URL |
   | Stale local credential/config | Re-adding or removing the server has no effect; old behavior persists; a previously failed attempt is "remembered" | Config file shows the server already present from a prior session; credential store has an entry for the server with no usable token, or an empty/expired one | Hosts that cache config or credentials and don't reload on edit |

3. **Rank matches by evidence strength**: a fingerprint matched by both symptom *and* a specific log line is "high confidence"; matched by symptom alone with no log to confirm is "possible — unconfirmed." Never present a possible match as certain.

4. **For each ranked candidate, give concrete manual remediation steps**, cheapest and least destructive first:
   - URL never surfaced / stalls after registration → check the host's raw install/debug log for an `auth_url` or `/authorize` link and open it manually in a browser. If no logs were supplied at all, say so and give two concrete next steps before concluding there's no fix: (a) find and enable the host's verbose/debug logging mode and retry, then re-check for a URL in that output; (b) check the MCP server/plugin's own docs or CLI output for an alternate manual sign-in path (a printed device code, a manual authorize link). Only if both come up empty is this a host bug with no current user-side fix.
   - Auto-open disabled → look for a browser/auto-open setting in host preferences; if found, toggle it; otherwise extract and manually open the URL from logs.
   - Infinite `about:blank` loop → close the embedded browser window and manually open the auth URL (from logs) in the system's default browser instead.
   - Stuck on provider's post-login page → close the tab/window manually; return to the host and check if the connection actually succeeded despite the stuck page (many of these are cosmetic once approval was granted).
   - Callback never reaches client in a blocked environment → run the host from a native context instead of WSL/remote/SSH if possible; check corporate VPN/proxy isn't blocking the localhost callback port; temporarily disable the VPN to test.
   - Discovery fails → this points at the MCP server's own configuration, not the client; report the failing metadata URL to the server's maintainer.
   - Stale local credential/config → fully remove the server from the host's config, restart the host, clear any matching entry in the OS keychain/credential manager for that server name, then re-add from scratch.

5. **If no fingerprint matches cleanly**, say so explicitly and give the generic first-pass checklist: confirm the server's metadata endpoint returns 200, try a different browser with extensions disabled, confirm no VPN/proxy is interfering, restart the host fully, and re-check logs after each step — then ask the user for the specific piece of evidence (which log, which screen) that would let the table actually match.

6. **Write the report** (format below).

7. **Self-check before returning**: confirm every fingerprint marked "matched" is traceable to a symptom or log line the user actually gave — not inferred from "this is usually what happens." Confirm remediation steps map 1:1 to the candidates actually ranked, not a generic dump of every row's fix.

## Output format

```markdown
# MCP OAuth Sign-In Triage — <host> / <server>

## What was reported
- Host: <host + version, or "unknown">
- MCP server / provider: <as given>
- Symptom: <verbatim-ish summary>
- Evidence supplied: <logs / none>

## Ranked Diagnosis
1. **<Fingerprint name>** — <High confidence | Possible, unconfirmed>
   Matched because: <symptom and/or log line>
   Try this: <ordered remediation steps>
2. (repeat for additional candidates, if any)

## If none of the above resolves it
<Generic checklist from step 5, only if no high-confidence match>

## Note
This is a one-time manual unstick, not a persistent fix — if this keeps recurring across reconnects, the underlying bug is in <host>'s OAuth-surfacing code and needs a report to that host's maintainers, not a repeat of this triage.
```

## Guardrails

- Never claim a specific host version has a specific known bug unless that was stated by the user or is in the fingerprint table above — do not fabricate a GitHub issue number, changelog entry, or maintainer statement that wasn't given to you.
- Never ask the user to paste a raw OAuth token, authorization code, or client secret — ask for status codes, URLs with sensitive query params stripped, and error text only; redact and flag any secret-shaped string that slips through anyway.
- Never present an unconfirmed fingerprint match as a certain diagnosis — rank by evidence and say "possible, unconfirmed" when there's no log to back it.
- This triage does not perform the OAuth flow, install anything, or modify host configuration itself — every remediation step is something the user runs by hand. Say so if the user expects an automated fix.
- If every fingerprint comes up empty, say that plainly and give the generic checklist — don't force a best-guess diagnosis to seem more useful than the evidence supports.
