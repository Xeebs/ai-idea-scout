# Rules-File Stable/Volatile Splitter

A prompt you can paste into any AI chat tool (Claude, ChatGPT, Copilot Chat, Gemini — no Claude Code install required) to clean up a bloated `AGENTS.md`/`CLAUDE.md` file. If your AI coding agent's instruction file has grown through months of accumulated fixes until it's hundreds of lines long, and the agent is starting to skip or mis-follow parts of it, this splits it into a small, durable rules file plus a separate draft "current status" file — once, as a cleanup pass.

**What this is not**: a tool that keeps the split in sync automatically going forward. This is a one-time audit. If you want the status file to stay fresh on its own via a git hook or CI job, that's a separate, more involved project — this just gets you the clean starting split.

## How to use it

1. Open a new chat with any capable AI assistant.
2. Paste the prompt below.
3. Paste your full current `AGENTS.md`/`CLAUDE.md` content right after it.
4. Review the two drafts it produces and the ambiguous-lines table before saving anything over your real files.

## The prompt

```
You are going to split a bloated AI-agent rules file (AGENTS.md or CLAUDE.md)
into two files: a trimmed STABLE file (the same filename, kept) and a new
STATE.md containing only VOLATILE content. I will paste my current file after
this prompt.

Classify every line or logical block (group consecutive lines under one
heading that share a classification; don't fragment every sentence) into one
of three buckets:

- STABLE: build/test/lint commands, architecture/directory facts, trade-off
  priorities, naming conventions, safety/security invariants, "never"/
  "always" rules that are NOT tied to one dated instance.
- VOLATILE: explicit dates or relative-time language ("as of", "currently",
  "this week", a quarter/year), TODO/WIP/"in progress" markers, file-count or
  status snapshots, references to one specific recent incident/PR/migration,
  task-tracking checklist items.
- AMBIGUOUS: anything mixing both, or unclear either way (e.g. a stable fact
  phrased with volatile wording like "the API currently uses v2"). Do not
  force a classification on these — flag them instead.

Classify by WHAT KIND OF CLAIM the line makes, never by how old it looks. An
old build command is still stable. A two-day-old TODO is still volatile.

Preserve the original order of surviving lines within each output file.
Every single line from the input must end up in exactly one place: the
stable draft, the STATE.md draft, or the ambiguous table below — never
dropped, never silently reworded, and never supplemented with content that
wasn't in the original.

Produce exactly this output, in this order:

1. STABLE FILE DRAFT (fenced markdown block) — only the stable content,
   same overall section structure where it still makes sense.
2. STATE.md DRAFT (fenced markdown block) — only the volatile content,
   reorganized under light headings such as "## Current Work",
   "## Open TODOs", "## Recent Changes" based on what each block actually
   is, not wherever it originally lived.
3. AMBIGUOUS LINES TABLE — columns: Original line (excerpt) | Lean
   (stable/volatile) | Rationale. Write "none" if there are no ambiguous
   lines.
4. One summary line: "Original: N lines -> Stable: A lines, Volatile: B
   lines, Ambiguous: C lines (needs your call)."

If the input has little or no volatile content, say so plainly instead of
forcing an unnecessary split.

Here is my file:

<paste your AGENTS.md / CLAUDE.md content here>
```

## What you get back

- A ready-to-save stable rules file, trimmed of anything time-bound.
- A draft `STATE.md` you can save alongside it, holding only the stuff that was actually changing.
- A short table of anything the assistant couldn't confidently classify, so you make the final call on those lines yourself rather than trusting a forced guess.
- A one-line count showing how much smaller your per-request rules file just got.

## Why this exists

Teams running AI coding agents against the same repo for months tend to append every fix to one rules file and never remove anything, until the file is big enough that it gets re-pasted in full on every single request (burning tokens) and the agent starts missing or misapplying parts of it. The fix people reach for today is a manual, repo-specific split into a "sacred" rules file plus a separate status file — but everyone invents their own version of that split from scratch, with no shared method for deciding what goes where. This prompt packages that method so you can run it in one pass instead of eyeballing a few hundred lines yourself.
