---
name: rules-file-stable-volatile-splitter
description: Splits a bloated AGENTS.md/CLAUDE.md into a trimmed stable rules file plus a draft STATE.md of volatile status content, flagging ambiguous lines for human confirmation. Use when a rules file has grown past the point of being hand-maintainable and is starting to get mis-followed.
---

# Rules-File Stable/Volatile Splitter

## When to use this
The moment someone notices their `AGENTS.md`/`CLAUDE.md` has grown past ~100-150 lines through accumulated fixes and nobody ever removes anything — and either the agent is starting to mis-follow or skip parts of it, or every request is visibly re-pasting a bloated file. This is a one-time cleanup pass: it proposes a split, it does not keep the split in sync afterward (that needs a persistent hook/CI job, which is a separate, project-level tool — not this skill).

## Inputs
**Data source**: Manual — the user pastes the full current text of their `AGENTS.md`/`CLAUDE.md` (or equivalent rules file) verbatim, in one message. No file path access, repo access, or connector is used or needed.

Optional but helpful: the file's approximate current token/line count (if the user already knows it), and whether the repo also has a separate status/scratch file already (so its content isn't duplicated into the new draft `STATE.md`).

## Procedure
1. **Parse by block, not just by line.** Treat each markdown heading (`#`/`##`/`###`) as a boundary; within a heading's body, group consecutive lines that share the same classification into one block rather than fragmenting every sentence. Preserve the original line order within each destination file.
2. **Classify every line into STABLE, VOLATILE, or AMBIGUOUS** using content type, not age, as the signal:
   - **STABLE** markers: build/test/lint commands, directory/architecture facts, trade-off priorities, naming conventions, security/safety invariants, "never"/"always" imperatives that aren't tied to a specific dated instance.
   - **VOLATILE** markers: explicit dates or relative-time phrasing ("as of", "currently", "this week", "Q3 2026"), `TODO`/`WIP`/"in progress", file-count or status snapshots, references to a specific recent incident/PR/migration, checklist items that track a task rather than state a policy.
   - **AMBIGUOUS**: a line that mixes both (a stable fact phrased with volatile language, e.g. "the API currently uses v2 endpoints") or doesn't clearly match either pattern. Never force-classify these — flag them.
3. **Write a one-line rationale for every AMBIGUOUS line** — the specific words that triggered the ambiguity, and which way you lean.
4. **Assemble two drafts**, preserving the original file's section structure wherever the surviving lines allow it:
   - A trimmed stable file (same filename as the input: `AGENTS.md`/`CLAUDE.md`), containing only STABLE blocks.
   - A draft `STATE.md`, containing only VOLATILE blocks, re-organized under light headings (e.g. `## Current Work`, `## Open TODOs`, `## Recent Changes`) based on what each block actually is — not a verbatim re-dump of wherever it happened to live in the original.
5. **Report counts**: original line count vs. new stable-file line count vs. new `STATE.md` line count vs. ambiguous-line count — so the user can see the actual size reduction of the file re-pasted every request.
6. Every original line must land in exactly one place: the stable draft, the volatile draft, or the ambiguous table. Never drop a line silently, and never add a new rule or fact that wasn't already in the input.

## Output format
Three parts, in this order:
1. **Stable file draft** — a fenced markdown block, ready to save over the original `AGENTS.md`/`CLAUDE.md`.
2. **`STATE.md` draft** — a fenced markdown block, ready to save as a new file.
3. **Ambiguous lines table** — columns: `Original line (excerpt)` | `Lean (stable/volatile)` | `Rationale`. Empty table (explicitly say "none") if nothing was ambiguous.
Followed by one line of counts: `Original: N lines → Stable: A lines, Volatile: B lines, Ambiguous: C lines (needs your call)`.

## Guardrails
- Never silently drop, merge away, or paraphrase-away a line from the input — classify it, don't edit its meaning.
- Never invent new rules, commands, or facts not already present in the pasted input.
- Never write files directly to the user's repo — this skill only produces draft text for the user to review and save themselves; it has no filesystem or git access in this mode.
- Never classify by age alone — a six-month-old build command is still stable; a two-day-old TODO is still volatile. Classify by what kind of claim the line makes.
- If the pasted file has little or no volatile content, say so plainly and recommend against forcing a split rather than inventing a `STATE.md` with no real content.
- This skill does not keep the split in sync after the fact — do not imply the output is "wired up" or self-updating; that is the separate, as-yet-unbuilt project-mode tool described in the parent idea.
