# MCP OAuth Sign-In Triage — portable prompt template

Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.), fill in the details about your stuck sign-in, and send it. No other setup is needed — this works standalone, outside Claude Code.

## What this does

MCP (Model Context Protocol) servers that wrap a SaaS API (Gmail, Slack, Notion, GitHub, and similar) require an OAuth sign-in before they work. Across hosts — Claude Desktop, Claude Code, Cursor, Codex, and others — this sign-in handoff has independently broken in several different ways: the sign-in URL never shows up, a browser opens to a blank page that never resolves, the browser gets stuck on the identity provider's own "you're signed in" page forever, or the host claims "connected" while every tool call still fails. The host's own error message is usually useless or nonexistent.

This prompt matches whatever you can tell it — your host, the MCP server, what you're actually seeing, and any logs you have — against a table of known failure patterns, and gives you back a ranked diagnosis plus manual steps to try, cheapest first.

This is a **one-time diagnostic pass**, not a running fix. It doesn't perform the OAuth flow for you, install anything, or persist across sessions — it reads what you give it and hands back a diagnosis and steps you run yourself.

## What you need to provide

1. **Host and version** — Claude Desktop, Claude Code, Cursor, Codex, or other, with version if you know it.
2. **MCP server** — its name, and the OAuth provider behind it if known (Notion, Google, GitHub, Slack, custom).
3. **Symptom, in your own words** — what you're actually seeing: no URL ever appeared, a browser window is stuck somewhere, a button is missing, or it says "connected" but nothing works.

Strongly recommended:
4. **Logs or console output**, if your host exposes any. Before pasting, strip out any OAuth token, authorization code, or client secret — the diagnosis only needs URLs, status codes, and error text, never secret values.
5. **What you've already tried** (restart, different browser, re-adding the server, etc.).

If you don't have one of these, say "unknown" rather than guessing — the diagnosis will say plainly which checks it couldn't run.

## The full prompt to paste

```
I'm stuck on an OAuth sign-in for an MCP (Model Context Protocol) server. Diagnose this as a one-time triage — don't assume you can fix it automatically, just tell me what's likely wrong and what to try by hand.

Here's what I have:
- Host and version: <e.g. Claude Desktop 0.x, Claude Code, Cursor, Codex, or "unknown">
- MCP server / OAuth provider: <name, and provider if known>
- Symptom in my own words: <what's actually happening right now>
- Logs or console output (secrets stripped): <paste, or "none available">
- What I've already tried: <restart / different browser / re-added server / etc., or "nothing yet">

Match what I've given you against these known failure patterns, and only call something a match if my actual symptom or log evidence supports it — don't force a fit:

1. URL never surfaced — install/connect hangs, no sign-in link or button ever shown.
2. Auto-open disabled silently — host claims it opened a browser; nothing opens.
3. Infinite about:blank loop — browser opens and reloads a blank page repeatedly, never resolves.
4. Stuck on the identity provider's post-login page — browser shows "signing you in" or a consent-granted page indefinitely, even though I actually approved access.
5. Callback never reaches the client in a blocked environment — everything looks normal but the host never registers success; common when the client runs inside WSL, over SSH/remote, or behind a strict VPN/proxy that blocks the localhost callback port.
6. Discovery fails before login starts — host errors immediately ("couldn't reach," "invalid server") before any sign-in UI appears; usually the server's own OAuth metadata endpoint is misconfigured.
7. Flow stalls after client registration — registration succeeds in logs, but the authorize/token endpoints are never called.
8. Stale local credential/config — re-adding or removing the server has no effect; a credential store entry for it persists with no usable token.

For each pattern that plausibly matches, rate it High confidence (symptom AND log evidence both point to it) or Possible, unconfirmed (symptom fits but no log to confirm) — never present an unconfirmed guess as certain.

Then give me, for each ranked candidate, the cheapest and least destructive fix to try first:
- URL never surfaced / stalls after registration → find and manually open the auth URL from raw logs if one exists. If I have no logs at all, first tell me how to enable verbose/debug logging for my host and retry, and check whether the server/plugin's own docs mention an alternate manual sign-in path (a printed device code, a manual authorize link) — only say this is a host bug with no fix if both of those come up empty.
- Auto-open disabled → look for a browser/auto-open setting in host preferences and toggle it, or manually open the URL from logs.
- Infinite about:blank loop → close the embedded browser and manually open the auth URL in my system's default browser instead.
- Stuck on provider's post-login page → close the tab manually and check whether the connection actually succeeded anyway — many of these are cosmetic once I already approved access.
- Blocked callback environment → try running the host natively instead of WSL/remote/SSH, or temporarily disable any VPN/proxy to test.
- Discovery fails → this is the MCP server's own misconfiguration, not something I can fix client-side; report the failing metadata URL to the server's maintainer.
- Stale credential/config → fully remove the server from my host config, restart the host, clear any matching entry in my OS keychain/credential manager, then re-add from scratch.

If nothing matches cleanly, say so and give me a generic first-pass checklist instead: confirm the server's metadata endpoint returns 200, try a different browser with extensions off, rule out VPN/proxy interference, fully restart the host, and re-check logs after each step.

Format the answer as:

# MCP OAuth Sign-In Triage — <host> / <server>

## What was reported
(host, server/provider, symptom, evidence supplied)

## Ranked Diagnosis
1. **<pattern name>** — High confidence | Possible, unconfirmed
   Matched because: ...
   Try this: ...
(repeat for any other candidates)

## If none of the above resolves it
(generic checklist, only if nothing matched with confidence)

## Note
State plainly that this is a one-time manual unstick, not a persistent fix, and that a recurring version of this bug needs a report to the host's own maintainers.

Rules:
- Never invent a specific bug report, version number, or maintainer statement I didn't give you.
- Never ask me for a raw OAuth token, authorization code, or client secret — only status codes, URLs with sensitive parameters stripped, and error text. If something secret-shaped appears in what I pasted anyway, flag it and redact it in your answer rather than repeating it.
- Don't present an unconfirmed match as certain.
- Don't perform the OAuth flow or claim you modified any configuration — every step is something I run myself.
- If nothing matches, say so plainly rather than forcing a best guess.
```

## What you get back

A short triage report: what you told it, a ranked list of which known MCP OAuth failure pattern(s) your symptom most likely matches (each honestly labeled confirmed-by-evidence or just plausible), concrete manual steps to try for each — cheapest first — and, if nothing matches, a generic fallback checklist. It's meant to turn "the sign-in is just stuck and the host tells me nothing" into a specific next action, not a guess.
