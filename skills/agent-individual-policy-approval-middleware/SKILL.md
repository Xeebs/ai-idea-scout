---
name: agent-individual-policy-approval-middleware
description: Drafts a starter allow/ask/deny policy for an individual's personal AI agent (filesystem, shell, or API access) from a plain-language description of its tools and the user's risk tolerance. Use when someone is setting up a personal agent (Claude Code, AutoGPT-style, LangChain/CrewAI/AutoGen, a custom MCP-based bot) and is either approving every single step out of fatigue, running it wide open, or asking "what should I auto-approve vs. deny here?"
---

# Starter Policy Drafter for Personal AI Agents

## When to use this
Someone is running (or about to run) a personal AI agent with real filesystem, shell, or API access on their own machine or VPS — not an enterprise fleet with its own security team — and is in one of these states:
- Clicking "approve" on every tool call until they stop reading carefully.
- Running the agent wide open with no approval gate because setting one up felt like too much work.
- Explicitly asking "what should this agent be allowed to do on its own, and what should always ask me first?"

This produces a **draft policy document**, not a running enforcement system. It is meant to be read, edited, and then wired into whatever actually intercepts calls on their setup — a Claude Code hook, an MCP server wrapper, a framework callback, or even just kept as a personal checklist if no enforcement exists yet.

## Inputs
**Data source**: Connected, in principle — the cleanest version of this reads the agent's declared tools and resource scopes straight from the runtime (Claude Code's tool/MCP manifest, a LangChain agent's tool list, etc.). No mature cross-framework connector for that exists today, so in practice this skill takes the same information as a manual description instead: the user describes their agent's tools and the resources it touches in their own words, and this skill treats that description as authoritative rather than guessing at what a connector would have shown.

The user provides:
1. **The agent's tools/capabilities** — e.g. "Bash on my VPS", "read/write in this one repo", "an HTTP client that can hit any URL", "a Stripe API key in test mode", "a Slack bot token for one channel". Be concrete about what it can actually invoke, not just "it's an AI agent."
2. **The resources/scope it can reach** — paths, directories, domains, accounts, channels, databases. If a tool is unscoped (e.g. shell access with no sandbox), say so explicitly.
3. **Risk tolerance, in the user's own words** — what they're relaxed about versus what should never happen without them looking first. Plain language is fine: "I don't care if it breaks the dev build, I care a lot about my production database and my credit card."
4. *(Optional)* **Target format** — a generic YAML policy, a Claude Code `settings.json`-style allow/ask/deny list, or a plain table. Defaults to a generic YAML block plus a human-readable table if not specified.

If the tool list or resource scope is too vague to write a specific rule (e.g. "it can access the internet" with no sense of what for), ask one clarifying question rather than inventing detail.

## Procedure
1. **Classify each stated tool+resource pair into an action class**:
   - Read-only (viewing files, GET requests, read-only API calls).
   - Reversible-write (editing code in a repo with version control, draft messages, staging changes).
   - Destructive/irreversible (deleting files or databases, force-pushing over history, unscoped `rm`/`DROP`, revoking access).
   - Financial or outbound-communication (payments, purchases, sending email/Slack/SMS to anyone outside the user, posting publicly).
   - Credential/secrets access (reading env vars, API keys, tokens, or using them to authenticate as the user).
2. **Map the user's stated risk tolerance onto each class.** Where the user's words clearly cover a class, use their stated tolerance. Where they're silent on a class, default by category:
   - Read-only → allow, unless the user said otherwise.
   - Reversible-write inside a scope the user named as theirs to experiment with → allow, with a note.
   - Destructive/irreversible → ask, never allow, even if the user didn't mention it — unless the user explicitly named that exact action class as acceptable to automate.
   - Financial/outbound-communication and credential/secrets access → ask, never allow by default, same rule.
3. **Write one rule per tool+resource pair**: action-verb pattern, resource pattern (path/domain/account scope as given), tier (allow/ask/deny), and a one-sentence rationale that cites either the user's own words or the default-by-category reasoning above.
4. **Always add a catch-all fallback rule** — "anything not explicitly matched above → ask" — never a silent default-allow for the unmatched case.
5. **Surface contradictions or unsafe blanket statements instead of complying with them silently.** If the user says something like "just auto-approve everything so it stops bugging me," write the policy they'd actually want (safety defaults intact) and add an explicit warning line naming what they asked for and why it wasn't applied as-is.
6. **Format the output** per the requested target format, or default to a generic YAML block plus a readable table if none was given.
7. **Append a short validation checklist**: 4-6 concrete sample actions (drawn from what the user described, not generic examples) they should mentally or actually run through the draft policy before trusting it, to catch a miscategorized rule before it causes damage.

## Output format
```
## Policy Draft

<YAML block or settings.json-style block or table, per requested format>
rules:
  - match: <action-verb pattern>
    resource: <path/domain/account pattern>
    tier: allow | ask | deny
    rationale: <one sentence>
  ...
  - match: "*"
    resource: "*"
    tier: ask
    rationale: "Fallback — anything not explicitly matched always asks first."

## Warnings
(Only if a stated risk tolerance was overridden for safety — one line per override naming what was asked and why it wasn't applied literally. Omit this section entirely if there were none.)

## Validate before trusting this
1. <sample action 1 drawn from the user's own description> → expected tier
2. <sample action 2> → expected tier
...
```

## Guardrails
- Never mark deletion, database drops, unscoped shell access, financial transactions, credential exfiltration, or outbound communication to third parties as "allow" by default, even if the user's risk tolerance didn't explicitly address that class — ask is the floor for anything irreversible or external until the user names that exact class as acceptable to automate.
- Never invent tools, resources, or accounts the user didn't mention. If the description is too thin to write a specific rule, ask one clarifying question instead of padding the draft with generic boilerplate rules.
- Never present this draft as already enforced. State plainly that it is a draft for human review that still needs to be wired into an actual enforcement point (hook, proxy, framework callback) or followed manually — this skill does not execute, monitor, or intercept anything itself.
- Never quietly comply with a request to reduce friction by loosening a destructive-action rule. If the user explicitly accepts that risk for a named class, honor it and say so in the rationale; if they just want "fewer approvals" in general, say which classes you kept at ask/deny and why, don't relax them to make the output look leaner.
- Never skip the fallback "ask" rule — an unmatched action defaulting to allow is the exact failure mode this skill exists to prevent.
