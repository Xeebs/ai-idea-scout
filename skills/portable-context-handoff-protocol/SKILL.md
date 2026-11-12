---
name: portable-context-handoff-protocol
description: Drafts a tool-agnostic "context bundle" (architecture, decisions, open threads, pitfalls) and renders it into CLAUDE.md, Cursor rules, and a generic system-prompt block, so a developer switching between AI coding tools on the same project doesn't re-explain context from scratch. Use when a user is about to switch tools, is onboarding a new tool to an existing project, or complains about re-explaining the same project context repeatedly.
---

# Portable Context Handoff Protocol

## When to use this

The user is working on one project across two or more AI coding tools (e.g. Claude Code, Cursor, ChatGPT/Copilot, Windsurf) in the same week, and either:
- is about to open a different tool and wants it to start with the context the last tool already had, or
- says something like "I keep re-explaining this to every tool," "my CLAUDE.md and Cursor rules have drifted apart," or "I need to hand this project to [another tool/person] without a context dump," or
- has an existing CLAUDE.md, `.cursorrules`, `AGENTS.md`, or chat transcript that's stale or tool-specific and needs to become portable.

This is a one-shot drafting task, not a sync daemon. It does not run in the background and does not auto-detect drift — it produces a snapshot the user re-runs when context has moved on.

## Inputs

Ask for (or extract from what the user already pasted):

1. **Project one-liner** — what the project is and its current phase (e.g. "Django billing service, mid-refactor of the invoicing module").
2. **Tools in play** — which AI tools the user switches between, and which one(s) they want this bundle to render for.
3. **Existing context, if any** — paste of a current CLAUDE.md, `.cursorrules`, `AGENTS.md`, or a chat summary. If none exists, the user describes architecture and recent decisions in their own words.
4. **Recent decisions and open threads** — what's been decided (and why), what's still unresolved, what's been tried and rejected. If the user has access to recent commit messages or PR descriptions, those are good raw material to paste in.

If the user gives only (1) and (2) with nothing else, proceed anyway — produce a thinner bundle and mark the missing sections explicitly rather than refusing or inventing content.

## Procedure

1. **Gather and reconcile.** Read any pasted existing context files first; treat them as the current source of truth for conventions and tone, not something to override with a generic template.
2. **Extract into five canonical sections:**
   - **Architecture Summary** — stack, key components, how they fit together (3–6 bullets).
   - **Recent Decisions** — each one dated (or marked "undated" if the user didn't give a date), one line of rationale per decision.
   - **Open Threads** — unresolved questions or in-progress work, phrased so the next tool knows what NOT to assume is settled.
   - **Rejected Approaches** — anything tried and abandoned, with the one-line reason, so the next tool doesn't re-propose it.
   - **File/Component State** — which files or modules are mid-change, stable, or off-limits right now.
3. **Mark gaps explicitly.** For any section where the input doesn't support real content, write `UNKNOWN — not provided` under that heading. Never fabricate a decision, a rationale, or a rejected approach that wasn't stated or clearly implied.
4. **Write the canonical bundle** as a single tool-agnostic markdown document using the five sections above, plus a header with the project name and the date the bundle was drafted (so staleness is visible at a glance).
5. **Render tool-specific adapters** for each tool the user named (default to all three if unspecified):
   - **Claude Code** — same five sections formatted as a `CLAUDE.md`-ready block (Claude Code reads this as project memory).
   - **Cursor** — the same content condensed into `.cursorrules` / `AGENTS.md` style (Cursor and most newer tools read `AGENTS.md`); note anything cut for length.
   - **Generic / ChatGPT or other chat tool** — a short system-prompt-style paragraph covering the same five sections in prose, sized to paste into a custom instructions box.
   If condensing for a size-constrained adapter required cutting content, say exactly what was cut in a one-line note under that adapter's block.
6. **Add a staleness flag**: one line stating "Re-run this after N more commits/decisions" or "Re-run before your next tool switch if more than [X days/commits] have passed," calibrated to how fast the project is moving based on what the user described.

## Output format

A single reply with:
1. The canonical bundle (markdown, five sections, dated header).
2. One fenced code block per requested tool adapter, each clearly labeled with the target filename (`CLAUDE.md`, `AGENTS.md` / `.cursorrules`, "Generic system prompt").
3. A one-line staleness recommendation.
4. If any section was marked `UNKNOWN`, a short bullet list at the end naming exactly what's missing and what input would fill it in next time.

## Guardrails

- Never invent a decision, rationale, or rejected approach the user didn't state or clearly imply — mark it `UNKNOWN` instead. A fabricated "decision" that another tool then treats as settled is worse than a gap.
- Never silently drop content when condensing for a size-constrained adapter — always note what was cut.
- Never claim this bundle auto-syncs with the repo or stays current on its own — it is a snapshot; say so and give the re-run cadence.
- If the user pastes an existing CLAUDE.md or `.cursorrules`, preserve its established conventions and terminology in the canonical bundle rather than replacing them with generic phrasing.
- Do not produce adapters for tools the user didn't name unless they asked for "all" or didn't specify — don't pad the output with irrelevant tool formats.
