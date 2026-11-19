# Continuity Desk — Manager-Agent + Shared Notes Store Design Review

Paste this whole prompt into any AI chat tool (ChatGPT, Claude, etc.) when you're juggling multiple AI-agent engagements — multiple clients, multiple projects, or multiple sub-agents on one project — and keep having to re-explain project state every time a session resets. This produces a concrete design: a notes-store schema, a rule for what gets saved vs. discarded, and (if you run concurrent projects) a manager-agent routing plan. It does not build the software for you — it's the spec you or a developer would build from.

## When to use this

Use it when any of this describes you:
- "I have to re-explain the project every time the AI agent's session resets or I open a new chat."
- "I keep a notes file or database per client, but it's ad hoc and I don't trust it's capturing the right things."
- "I run more than one client/project with AI agents and sometimes a new session doesn't know what an earlier session already decided."
- You want a design for a 'manager agent' that routes work to the right project and a shared notes store that survives resets — before you build any of it.

This is a one-time design/review task. If you want the actual running software (a database wired into your agent tool, auto-reading session transcripts), this gives you the spec to build it from, not the working system itself.

## What to hand over

Paste or type, in your own words:

1. **Your clients/projects** — the list of them, and roughly how many you run AI-agent sessions on *at the same time* (concurrently), not just over time.
2. **Your tools** — which AI agent tool(s) you use per engagement (Claude Code, Cursor, ChatGPT with a custom setup, etc.), and whether you already have any kind of "manager" or dispatcher layer, even informal.
3. **How you currently keep notes/context per project** — a raw SQLite file, a Notion/Obsidian page, nothing at all, or re-pasting context from memory each time.
4. **1-3 real recent moments where context was lost** — be specific: what fact or decision got lost or had to be re-derived, and (if you remember) which earlier session or conversation it came from originally.

If any of these four are missing, the assistant should ask you for them before producing a design — a design built on a vague picture of your setup isn't worth having.

## What you'll get back

A single document with these sections, in this order:

1. **Current State Map** — a short table of your projects, which tool runs each, and how notes are currently kept (or "none"). It will flag which projects actually run more than one session concurrently — that's the only place a "manager agent" routing layer earns its keep. If only one project ever runs concurrently, the manager-agent section gets explicitly skipped rather than over-built.

2. **Notes Partition Schema** — one schema per project (or a shared schema if they're similar), defaulting to a SQLite table with full-text search and these fields: a note ID, project ID, originating session ID (or your own session label if your tool has none), agent name, timestamp, note type (decision / fact / open question / preference), the note content, and a one-sentence "source trigger" — what prompted the note. If you've indicated you don't want to run a database, this becomes the same fields as a markdown file per project instead, with each note as a small frontmatter block.

3. **Noise Filter Rule** — one explicit sentence for what gets saved to the shared store vs. stays throwaway scratch, built from your real lost-context examples: durable facts and decisions that would still matter next week get saved; moment-to-moment task scratch does not. This errs toward saving less, not more — a notes store that captures everything is as useless as one that captures nothing.

4. **Manager-Agent Routing** (only if you have ≥2 concurrently-run projects) — how new incoming work gets matched to the right project (by explicit tag, keyword match, or asking you when ambiguous), and a session-start checklist: every new or resumed session should pull the 5-10 most relevant saved notes for that project before starting work, instead of starting cold.

5. **Provenance Convention** — a short explanation of how every note's session ID and source-trigger fields together let you trace any saved note back to exactly which session wrote it and why, without digging through old chat logs — demonstrated with one of your real lost-context examples rewritten as what the note would have looked like, and how you'd have found it again. If that example was actually a policy or safety violation (like a rule being broken, not just work being redone), it will say plainly that saving the rule as a note makes it discoverable next time, but does not by itself stop a future session from breaking it again — actually enforcing a rule needs a separate mechanism (a check, a lint rule, a guardrail prompt), which this design doesn't provide.

6. **Leakage Flag** (only if relevant) — if your described setup has different clients' sessions sharing the same machine, tool config, or storage, a plain note that this design keeps each project's notes logically separate but does *not* itself enforce access control between clients — that's a different problem you'd need to solve separately if your clients are mutually confidential.

7. **Open Questions** — anything your description left unclear that would change the design, called out explicitly rather than guessed at.

## Rules the assistant should follow

- Never invent clients, projects, or tools you didn't mention — if something's missing, it should ask, not make up a plausible-sounding example.
- Never assume you want SQLite — it should check what you're comfortable running first.
- Never try to solve cross-client confidentiality/access-control in this design — that's flagged, not solved, here.
- Never build the manager-agent routing section if you only ever run one project concurrently — recommend just the notes-store half instead.
- It should be clear this is a design document, not working software — you (or whoever you hire) still have to build it.
