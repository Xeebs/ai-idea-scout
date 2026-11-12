# Portable Context Handoff Protocol

Paste this whole thing into any AI chat tool (ChatGPT, Claude, Gemini, a Cursor chat, whatever) when you're switching between two or more AI coding tools on the same project and don't want to re-explain the architecture, recent decisions, and open questions from scratch every time. It turns whatever you know about the project into one tool-agnostic "context bundle," plus ready-to-paste versions for Claude Code, Cursor, and a generic chat tool.

This is a one-shot drafting task. It does not watch your repo or auto-update — you re-run it when enough has changed that the last bundle is stale.

## When to use this

Use it when:
- You're about to open a different AI coding tool on a project you've been working in with another one, and you want it to start from where the last tool left off.
- You keep re-typing the same "here's the architecture, here's what we decided, here's what's still open" explanation to every new tool or session.
- Your CLAUDE.md and your Cursor rules (or AGENTS.md) have drifted apart and you want one source reconciled into both.
- You're handing a project off to a teammate (or a future version of yourself) and want more than a raw chat dump.

## What to give it

Paste or describe:

1. **Project one-liner** — what it is and what phase it's in right now (e.g. "Node/Postgres API, mid-migration off a legacy auth service").
2. **Which tools you switch between** — and which one(s) you want the output formatted for (Claude Code, Cursor, ChatGPT/other, or "all three").
3. **Any existing context file** — your current CLAUDE.md, `.cursorrules`, `AGENTS.md`, or even a copy-pasted chat summary, if you have one. If you don't have one, just describe the architecture and recent decisions in your own words.
4. **Recent decisions, open threads, and dead ends** — what's been decided and why, what's still unresolved, and anything you tried and abandoned (so the next tool doesn't propose it again). Recent commit messages or PR descriptions work well as raw material here.

If all you have is #1 and #2, that's fine — say so and it will still produce something useful, just thinner, with the gaps clearly marked instead of made up.

## What it does

1. Reads anything you pasted (an existing CLAUDE.md, rules file, or chat summary) as the current source of truth — it won't override your established conventions and phrasing with generic boilerplate.
2. Organizes everything into five sections:
   - **Architecture Summary** — stack and key components, 3–6 bullets.
   - **Recent Decisions** — dated where possible, one line of rationale each.
   - **Open Threads** — what's unresolved, phrased so the next tool doesn't assume it's settled.
   - **Rejected Approaches** — what was tried and abandoned, and why, so it doesn't get re-proposed.
   - **File/Component State** — what's mid-change, stable, or off-limits right now.
3. Marks any section it can't fill from what you gave it as `UNKNOWN — not provided`, instead of guessing. It will never invent a decision or a reason you didn't actually give it.
4. Writes the canonical bundle (all five sections, dated header) once, then renders it into whichever tool formats you asked for:
   - **Claude Code** — a `CLAUDE.md`-ready block.
   - **Cursor** — a `.cursorrules` / `AGENTS.md`-style block, condensed if needed, with a note on anything cut for space.
   - **Generic / ChatGPT** — a short prose paragraph sized for a custom-instructions box.
5. Adds one line telling you when to re-run this (e.g. "re-run after your next few commits or before your next tool switch").

## Output you'll get

- The canonical bundle in plain markdown (the five sections above, dated).
- One clearly labeled code block per tool you asked for (`CLAUDE.md`, `AGENTS.md`/`.cursorrules`, or "Generic system prompt").
- A one-line staleness recommendation telling you when to redo this.
- If anything was marked unknown, a short list at the end of exactly what's missing, so you know what to bring next time.

## The prompt to paste

```
I'm switching between AI coding tools on the same project and want a portable context bundle so I stop re-explaining myself to each one.

Project: [one-liner + current phase]
Tools I switch between: [e.g. Claude Code and Cursor] — render the output for: [name the tool(s), or say "all three: Claude Code, Cursor, generic"]

Here's my existing context (paste a CLAUDE.md / .cursorrules / AGENTS.md / chat summary if you have one, otherwise describe the architecture yourself):
[paste or describe]

Recent decisions, open threads, and anything tried and abandoned:
[list what you remember — commit messages or PR descriptions are great raw material]

Please:
1. Pull this into five sections: Architecture Summary, Recent Decisions (dated, with rationale), Open Threads, Rejected Approaches, File/Component State.
2. Mark anything you can't fill in as UNKNOWN — not provided. Don't invent decisions, rationale, or rejected approaches I didn't give you.
3. Write the canonical bundle once, then render it as [the tool format(s) I named above] — note anything you had to cut to fit a tool's size limits.
4. End with one line on when I should re-run this, and (if anything was marked unknown) a short list of what I should bring next time.
```

## Guardrails (what it should never do)

- Never invent a decision, rationale, or rejected approach you didn't state — gaps get marked `UNKNOWN`, not filled with plausible-sounding guesses.
- Never silently cut content to fit a tool's size limit without telling you what was cut.
- Never claim the bundle stays in sync with your repo on its own — it's a snapshot, and it will tell you when to redo it.
- If you pasted an existing CLAUDE.md or rules file, it keeps your conventions and terminology rather than replacing them with generic phrasing.
- It won't pad the output with formats for tools you didn't ask for.
