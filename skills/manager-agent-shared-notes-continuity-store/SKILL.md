---
name: manager-agent-shared-notes-continuity-store
description: Audits a freelancer's or small team's current multi-client/multi-project AI agent setup and designs a concrete manager-agent + shared notes-store architecture (schema, routing rules, provenance tagging) so context survives session resets. Use when someone describes re-explaining project state every time an agent session resets, or running several AI-agent engagements in parallel with only ad hoc notes.
---

# Continuity Desk Design Review

## When to use this
The user is running (or about to run) more than one AI-agent engagement at a time — multiple clients, multiple internal projects, or multiple sub-agents on the same project — and describes any of:
- "I have to re-explain the project every time the session resets."
- "I keep a SQLite file / notes doc per client but it's not really organized."
- "My sub-agents don't know what the other sessions already decided."
- They want a design for a "manager agent" that dispatches work across projects and a shared notes store that survives resets, before committing to building the actual runtime.

This is a one-shot design/review task, not the runtime itself. If the user wants the actual working notes-store software built and wired into their agent runtime, say so explicitly and treat this skill's output as the spec for that build, not a substitute for it.

## Inputs
**Data source**: Manual — the user pastes a description of their current setup: (1) the list of clients/projects they juggle and roughly how many run concurrently, (2) which AI agent tool(s) they use per engagement (e.g. Claude Code, Cursor, a custom agent script) and whether a "manager" layer already exists in any form, (3) how notes/context are currently kept per project if at all (raw SQLite, a notes app, nothing, re-pasting from memory), and (4) 1-3 concrete recent instances where context was lost or re-derived unnecessarily, described in enough detail to see what fact was lost and when. No API or connector is read — if the user instead wants this skill to read live session transcripts automatically, that is the separate runtime-infrastructure half of this idea (the project, not the skill) and is out of scope here.

If the user's description is missing (1)-(4), ask for whichever pieces are missing before producing the design — a design built on an incomplete picture of their setup is worse than no design.

## Procedure
1. **Map the current state.** List out, in a short table, every project/client the user mentioned, which agent tool runs it, and how notes are currently kept (or "none"). Flag any project where more than one agent session can run concurrently — that's where the manager-agent routing layer actually earns its keep; a single-project, single-session user only needs the notes-persistence half.
2. **Classify each lost-context instance.** For each of the 1-3 concrete instances the user gave, identify: what fact/decision was lost, which session it originated in (if known), and whether it was a *durable fact* (would still matter next week — a client's API key format, a decided architecture choice, a style preference) or *session-local noise* (a mid-task scratch thought that shouldn't persist). This becomes the basis for the noise filter in step 4.
3. **Design the per-project notes partition schema.** Default to one SQLite file per project/client with a single `notes` table and FTS5 virtual table for search, with these columns: `note_id`, `project_id`, `session_id` (the originating agent session's ID or a user-assigned label if the tool has no session IDs), `agent_name`, `created_at`, `note_type` (`decision` | `fact` | `open_question` | `preference`), `content`, `source_trigger` (one sentence: what prompted this note to be written). If the user's description signals no appetite for running SQLite (e.g. solo non-technical user, wants something in Notion/Obsidian), substitute one markdown file per project with the same fields as YAML frontmatter per note-block instead of a DB table — same schema, different storage, and say so explicitly.
4. **Write the noise filter rule.** One explicit sentence of criteria, derived from step 2's classification, for what gets written to the shared store vs. stays session-local scratch. Err toward under-capturing (the idea file's own stated risk: too aggressive capture fills the store with noise) — default rule: only decisions, durable facts, and open questions that would still be true next week qualify; task-level scratch work does not.
5. **Design the manager-agent routing rule**, only if step 1 found ≥2 concurrently-run projects. State: how new incoming work gets matched to a project_id (by explicit user tag, by keyword match against project names, or — if ambiguous — by asking), and the session-start checklist every new/resumed sub-agent session should run: query the project's notes store for the top 5-10 most relevant entries (by FTS match against the task description, or most-recent if no clear match) and surface them before starting work. If step 1 found only one concurrently-run project, state explicitly that the manager-agent layer isn't needed yet and the notes-store half alone addresses the described pain.
6. **Write the provenance-tagging convention.** One paragraph: every note's `session_id` + `source_trigger` fields together must let a human trace any note back to "which session wrote this and why" without grepping chat logs — restate this as the concrete acceptance test for the design (pick one real lost-context instance from step 2 and show what the note would have looked like, and how it would have been found). If the chosen instance is actually a policy/safety violation (e.g. a stated rule like "never log PII" was broken) rather than redundant re-derived work, say explicitly that persisting the rule as a note makes it *discoverable* at the next session's start but does not *enforce* it — enforcement (a lint rule, pre-commit check, or an automated guardrail prompt) is a separate mechanism this design does not provide, and should be called out as a gap rather than implied to be solved.
7. **Flag cross-client leakage risk explicitly but do not design for it.** If the user's described setup has agent sessions for different clients sharing any resource (same machine, same agent tool config, same vector store), say plainly that this design assumes each project's partition stays logically separate but does not itself enforce access control between them — that is a different problem (isolation/leak-prevention), and point out it needs separate handling if the user's clients are mutually confidential.

## Output format
A single markdown document with these sections, in order:
1. **Current State Map** — the table from step 1.
2. **Notes Partition Schema** — the concrete schema from step 3 (table/columns or markdown-frontmatter equivalent), named per project if schemas differ.
3. **Noise Filter Rule** — the one-sentence rule from step 4.
4. **Manager-Agent Routing** — the routing + session-start checklist from step 5, or the explicit "not needed yet" statement.
5. **Provenance Convention** — the paragraph from step 6, plus the worked example showing one real lost-context instance resolved.
6. **Leakage Flag** (only if applicable per step 7).
7. **Open Questions** — anything the user's description left ambiguous that would change the design (e.g. "unclear whether Client B's sessions ever run concurrently with Client A's — if so, routing needs a tie-break rule").

## Guardrails
- Never invent clients, projects, or tools the user didn't mention — if details are missing, ask rather than fill in a plausible-sounding example.
- Never assume SQLite is wanted — check what the user's described comfort level and existing tools actually support before defaulting to it.
- Never design or imply an access-control/leak-prevention mechanism between clients — that's a different, separable concern (flag it, don't solve it here).
- Never produce the routing-layer section if the user's setup only has one concurrently-active project — recommend the notes-store half alone instead of over-building.
- Never claim this design is a working implementation — it is a spec a developer (the user, or someone they hire) still has to build; say so if there's any risk of that being unclear.
- Never imply that persisting a safety/policy rule as a note (e.g. "never log PII") by itself *enforces* that rule — a note makes a rule discoverable at the next session's start, it does not stop a future session from violating it; enforcement is a separate mechanism outside this design's scope, and a lost-context instance that's really a policy violation must be labeled as such rather than treated as solved.
