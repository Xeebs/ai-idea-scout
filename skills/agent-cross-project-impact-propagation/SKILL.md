---
name: agent-cross-project-impact-propagation
description: Checks whether a change you just made in one project could affect open tasks in your other concurrent projects or client engagements. Use right before a commit or at session wrap-up when you're juggling 2+ projects with their own task/backlog lists.
---

# Ripple Check — Cross-Project Impact Flag

## When to use this
Right before committing a change, or when wrapping up a coding session, and you are juggling two or more concurrent projects or client engagements (freelancer, contractor, or small dev shop running CLI coding agents like Claude Code, Cursor, or Codex across multiple codebases). You just made a decision — changed an API shape, deprecated a field, switched a convention, renamed something load-bearing — and you want to know whether any *other* open task, in this project or a different one, quietly depends on the old behavior.

This is the manual, install-nothing companion to "Ripple," a hypothetical always-on daemon that would do this automatically by watching git history across registered repos. This skill does the same judgment on demand, from what you paste, with no daemon, no embeddings infra, and no persistent state.

## Inputs
**Data source**: Manual — you paste (1) a one-to-three-sentence description of the change you just made or the diff itself, and (2) one or more open task/backlog lists, each labeled with the project or client it belongs to (a plain bullet list is fine — whatever you already keep in a TASKS.md, a Markdown backlog, or similar). Nothing is read from disk, git, or any API by this skill. (The full "Ripple" project this skill companions would instead connect directly to each registered project's local git history and each coding CLI's session-state files on the developer's own machine — that connected version does not exist yet; this skill is the standalone manual version that works today.)

Required:
1. The change: what changed, in concrete terms (a field, endpoint, convention, dependency version, data shape) — not just "fixed a bug."
2. At least one task list, each clearly labeled with its project/client name.

Optional but helpful:
3. A note on whether any of the listed projects share a system, library, vendor API, or database with the one you just changed — this disambiguates a real dependency from two projects that merely sound similar.

## Procedure
1. **Parse the change.** Restate it in one line as a concrete technical fact: what interface, field, convention, or assumption changed, and what the old vs. new behavior is. If the user's description is too vague to extract a concrete fact (e.g., "cleaned some stuff up"), ask one clarifying question before proceeding — do not guess.
2. **Extract the dependency surface.** List the specific things another task could be depending on: exact field/endpoint/function names, the specific convention (e.g., "offset-based pagination params `page`/`limit`"), any deprecation window, and any explicitly named shared system (library, vendor API, shared DB) from the optional input.
3. **Walk every pasted task, in every list, one at a time.** For each task, decide:
   - **LIKELY** — the task's own text names or clearly implies the exact interface/field/convention that changed (e.g., the task references the same field name, the same endpoint, or explicitly builds on the exact old behavior).
   - **POSSIBLE** — the task is in the same project/codebase as the change and touches the same general area (same module, same data object) but doesn't explicitly confirm the dependency, OR the task is in a *different* project that was explicitly flagged (per input #3) as sharing the relevant system with the changed project.
   - **NONE** — no plausible dependency. Default here. Topic-word overlap alone (e.g., both tasks mention "pagination") across two *different, unrelated* projects is NOT sufficient for POSSIBLE or LIKELY — see Guardrails.
4. **Never silently skip a list.** If a pasted list has zero LIKELY/POSSIBLE matches, say so explicitly in the output rather than omitting that project.
5. **Write a one-line reason for every LIKELY/POSSIBLE flag**, citing the specific overlapping term or system, not a vague "seems related."
6. **Apply the confidentiality rule before writing cross-project output** (see Guardrails) — abstract any flag that crosses a client/project boundary.
7. **Recommend a next action per flag**: "confirm with teammate," "update this task's description," "re-test after merge," or "ignore — false positive, logged for calibration."

## Output format
```
## Ripple Check — <one-line restatement of the change>

### <Project/Client A>
- [LIKELY] "<task text>" — <specific reason>. Next: <action>
- [POSSIBLE] "<task text>" — <specific reason>. Next: <action>

### <Project/Client B>
- No tasks flagged as likely or possibly affected.

### Confidence note
<1 line: how much signal this was based on — e.g., "based only on task titles; task bodies/descriptions weren't pasted, so some matches may be missed.">
```
Always include every pasted project/client as its own section, even when nothing is flagged in it.

## Guardrails
- **Never flag on topic-word overlap alone.** Two tasks both mentioning "pagination," "auth," or "export" in two different, unrelated client projects is not a dependency — it's a coincidence. Only flag a cross-project match as POSSIBLE (never LIKELY) when the user has explicitly stated the two projects share the relevant system, library, or vendor API; otherwise mark NONE and, if genuinely ambiguous, note it under the confidence line instead of inventing a flag.
- **Never leak concrete content across a client/project boundary.** If two pasted lists belong to different named clients, any flag that references client A's change in client B's section must be abstracted to the nature of the change ("an API pagination convention changed upstream in another engagement") — never the specific field names, code, vendor names, or business details from client A. Within the *same* client/project, full detail is fine.
- **Never invent a task.** Only evaluate tasks the user actually pasted, verbatim or near-verbatim when quoting them back.
- **Never mark something LIKELY on a guess.** If you're not sure whether the dependency is real, it's POSSIBLE at most, with the reasoning stated so the user can judge for themselves.
- **Never drop a pasted list from the output**, even if it has nothing flagged — absence must be stated, not implied by omission.
- **Don't ask the user to install anything or connect any account.** This skill does its entire job from what's pasted in the conversation.
