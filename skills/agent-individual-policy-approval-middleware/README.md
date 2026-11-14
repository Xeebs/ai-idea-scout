# Starter Policy Drafter for Personal AI Agents

A portable prompt that drafts a starting allow/ask/deny policy for a personal AI agent with real filesystem, shell, or API access — written from a plain description of what the agent can do and how much risk you're willing to accept, not from a policy-syntax manual you have to learn first.

This is for anyone running a personal agent (Claude Code, an AutoGPT-style bot, a LangChain/CrewAI/AutoGen setup, a custom MCP-based assistant) on their own machine or VPS who is either clicking "approve" on every single step out of fatigue, running it wide open because setting up a real policy felt like too much work, or just wants a straight answer to "what should this thing be allowed to do on its own?" It works in any chat tool — no installation, no enforcement system required to get value from it.

**Important**: this produces a draft document for you to read and edit, not a running security system. You still need to wire the result into something that actually intercepts calls (a Claude Code hook, an MCP wrapper, a framework callback) or follow it as a manual checklist — this prompt does not execute or monitor anything by itself.

## How to use it

Give it, in your own words:
1. **What your agent can actually do** — be concrete: "Bash access on my VPS," "read/write inside this one repo," "an HTTP client that can hit any URL," "a Stripe key in test mode," "a Slack bot token for one channel." Not just "it's an AI agent."
2. **What it can reach** — which paths, directories, domains, accounts, channels, or databases. If something is unscoped (e.g. shell access with no sandbox), say so.
3. **Your risk tolerance, plainly** — what you don't mind it doing on its own versus what should always stop and ask first. "I don't care if it breaks my dev build, I care a lot about my production database and my credit card" is exactly the right level of detail.
4. *(Optional)* **A target format** — generic YAML, a Claude Code `settings.json`-style allow/ask/deny list, or just a plain table. If you don't say, you'll get YAML plus a readable table.

If what you describe is too vague to write a specific rule from, a good response asks you one clarifying question rather than guessing.

---

### The prompt

> You are drafting a starter approval policy for someone's personal AI agent (filesystem, shell, or API access on their own machine or VPS — not an enterprise fleet). You will be given: the agent's tools/capabilities, the resources/scope it can reach, the user's risk tolerance in their own words, and optionally a target format. Do this:
>
> 1. Classify each tool+resource pair into one of: read-only; reversible-write; destructive/irreversible (deletion, DB drops, unscoped shell, force-push over history, revoking access); financial or outbound-communication (payments, purchases, messages/posts to anyone outside the user); credential/secrets access.
> 2. Map the user's stated risk tolerance onto each class. Where their words clearly cover a class, use their stated tolerance. Where they're silent: read-only defaults to allow; reversible-write inside a scope they called their own to experiment with defaults to allow with a note; destructive/irreversible, financial/outbound-communication, and credential/secrets access default to **ask**, never allow, unless the user explicitly named that exact class as acceptable to automate.
> 3. Write one rule per tool+resource pair: an action-verb pattern, a resource pattern (the actual path/domain/account scope given), a tier (allow/ask/deny), and a one-sentence rationale citing either the user's own words or the default-by-category reasoning above.
> 4. Always add a catch-all fallback rule: anything not explicitly matched → ask. Never let an unmatched action default to allow.
> 5. If the user's risk tolerance contains a blanket unsafe request ("just auto-approve everything so it stops bugging me"), write the policy they'd actually want with safety defaults intact, and add a one-line warning naming what was asked and why it wasn't applied literally — don't comply silently, and don't refuse to produce anything either.
> 6. Format the output as requested (generic YAML, Claude Code settings.json-style, or a table); default to YAML plus a readable table if no format was given.
> 7. End with a short validation checklist: 4-6 concrete sample actions drawn from what the user actually described (not generic examples) with the tier each should land on, so they can sanity-check the draft before trusting it.
>
> Never invent tools, resources, or accounts the user didn't mention — if the description is too thin to write a specific rule, ask one clarifying question instead of padding with generic boilerplate. Never mark deletion, database drops, unscoped shell access, financial transactions, credential exfiltration, or outbound communication to third parties as "allow" by default. Never present the draft as already enforced — say plainly it still needs to be wired into a real enforcement point or followed manually. Never quietly loosen a destructive-action rule just to reduce the number of approvals; if you kept something at ask/deny despite a request for "fewer approvals," say so and why.
>
> Output format:
> ```
> ## Policy Draft
> rules:
>   - match: <action-verb pattern>
>     resource: <path/domain/account pattern>
>     tier: allow | ask | deny
>     rationale: <one sentence>
>   ...
>   - match: "*"
>     resource: "*"
>     tier: ask
>     rationale: "Fallback — anything not explicitly matched always asks first."
>
> ## Warnings
> (omit entirely if there were none — one line per overridden request otherwise)
>
> ## Validate before trusting this
> 1. <sample action from the user's own description> → expected tier
> ...
> ```
>
> Here is my agent's setup:
> [describe your agent's tools, what they can reach, and your risk tolerance in your own words — and optionally, your target format]

## Why this exists

Three separate hobbyist builders posted their own version of a human-approval/policy layer on r/AutoGPT within the same 30-day window, each describing the same problem: giving a personal AI agent real computer access today means either approving every single step until you stop reading carefully, or skipping isolation and absorbing the risk. Commercial zero-trust products (Gravitee, HoopAI, Pomerium) solve this well for enterprise fleets; nothing targets an individual running their own agent on their own machine. Existing open-source attempts at the individual level are either generic policy templates you still have to hand-write (so you're back to learning a schema before you get any value), or a Haiku-backed gatekeeper that classifies each call live instead of giving you a reviewable starting policy — a useful drafting tool is not in any of the open-source options today. This prompt is that drafting tool: it turns a plain description of your agent and your own risk tolerance into a specific, reviewable starting policy in one pass, usable immediately even before any enforcement proxy exists to run it.

Full project context, evidence, and a sketch of the runtime enforcement proxy this pairs with: see [`ideas/agent-individual-policy-approval-middleware.md`](../../ideas/agent-individual-policy-approval-middleware.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
