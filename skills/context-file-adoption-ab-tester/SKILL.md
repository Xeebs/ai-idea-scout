---
name: context-file-adoption-ab-tester
description: Reviews an existing AGENTS.md/CLAUDE.md-style context file section-by-section and flags which sections are most likely stale, overly verbose, or contradictory with the coding agent's own defaults — producing a prioritized "test this first" shortlist before anyone commits time to a full paired A/B comparison run. Use when a team already has a context file in production and suspects (or just wants to check) that parts of it might be hurting more than helping.
---

# Context File Adoption Triage

## When to use this
A team has an AGENTS.md, CLAUDE.md, or equivalent project-context file already in use with a coding agent (Claude Code, Codex CLI, Cursor, Aider, Copilot, Gemini CLI, Windsurf, Amazon Q, etc.), and someone has either read reporting that these files can reduce task success and raise inference cost, or simply noticed the agent ignoring/contradicting the file, and wants a fast read on which sections are worth scrutinizing — before spending the time and inference spend to run a real paired comparison (same file present vs. absent/trimmed, same task suite, twice).

Do not reach for this skill to write a new context file from scratch, to fix a single known bad instruction the team has already identified, or as a substitute for an actual measured A/B run — it is strictly the one-shot triage pass that decides *where* to point that measured run first.

## Inputs
**Data source**: Manual — the user pastes the full, verbatim text of the context file, plus three short pieces of context: (1) which coding agent it's used with, (2) a one-line description of the repo (language/stack, approximate size), and (3) ideally 1-3 real recent task prompts (issue titles, PR descriptions, or "ask the agent to do X" requests) the team actually cares about getting right. This is deliberately narrower than the parent idea's own classification: the parent idea's full paired-comparison *tool* is Connected — it runs the named coding agent's CLI directly against the team's real repo, with and without the file, which is a mature capability in all the agents listed above. This skill is the separable pre-run judgment half described in that idea's Skill Angle, and it only ever reasons over text handed to it; it never executes an agent CLI, clones a repo, or reads a file tree on its own. If you have file/repo access in your environment (e.g. Claude Code with Read access to the actual repo), you may use it to verify staleness claims (see Procedure step 2), but the core review runs equally well in a plain chat tool with nothing but pasted text.

To run this skill, hand over:
1. The full context file content, pasted verbatim (not summarized or paraphrased — exact wording is what causes agent drift, so a condensed description of "basically it says X" defeats the review).
2. The agent name/CLI it's used with.
3. A one-line repo description (stack, rough size).
4. Optionally, 1-3 real task prompts the team wants the agent to handle well.

## Procedure
1. **Segment the file.** Split the pasted content into discrete sections by heading or clearly separated bullet group. Number them in document order (S1, S2, ...) and record each section's approximate line count and a one-line paraphrase of its content for the report.
2. **Classify each section against four failure-pattern categories** (the categories the cited 2026 AGENTS.md study associates with reduced task success and increased inference cost):
   - **STALE** — references a specific file path, directory, tool, dependency version, or workflow that may no longer exist or match the repo description given. If repo/file access is available, verify directly; if not, flag as "unverified — confirm against repo" rather than asserting it's actually stale.
   - **VERBOSE** — restates generic best practice the agent's own training/defaults already cover (e.g., "write clean, readable code," "use meaningful variable names") with no repo-specific instruction, or repeats content already said in another section.
   - **CONTRADICTORY** — conflicts with the named agent's documented default behavior (e.g., telling Claude Code to always ask before edits when the team runs it with `--dangerously-skip-permissions`), or conflicts with another section in the same file.
   - **REDUNDANT-WITH-CODE** — describes something the agent could derive by reading the code itself in one or two tool calls (e.g., "this project uses TypeScript" when `package.json`/`tsconfig.json` already states it unambiguously).
   A section can carry zero, one, or multiple flags. A section with zero flags is not "verified good" — it simply passed this triage; say so explicitly rather than omitting it.
3. **Assign a Predicted Risk (HIGH / MEDIUM / LOW) per flagged section**, based on: how many categories it triggers, how directive/long the section is, and whether it sits early in the file (agents generally weight earlier instructions more heavily, so a long, flagged section near the top of the file is higher predicted risk than the same content buried at the end).
4. **Check for safety/compliance carve-outs.** Any section covering secrets handling, deployment gates, data-access restrictions, or compliance/legal rules gets flagged "verbose but do not cut without human review" instead of a normal risk score, even if it also trips VERBOSE or REDUNDANT-WITH-CODE — removing these for a test run is not a decision this skill makes unilaterally.
5. **Rank the flagged (non-carve-out) sections** by Predicted Risk, then by section length, to produce the "test this first" shortlist — the sections most worth isolating in an actual paired A/B run.
6. **Write one falsifiable hypothesis per shortlisted section**, in the form "removing/trimming S<n> should [increase/have no effect on] success and [decrease/have no effect on] cost if the <category> pattern is real for this repo" — this is what the real comparison run would be testing, not a conclusion this skill is allowed to assert on its own.
7. **State plainly whether running the full paired comparison is worth it right now** given what triage found — e.g., "3 sections flagged HIGH risk, worth a real run" vs. "nothing flagged above LOW, the file looks clean on this pass, a full paired run is optional."

## Output format
A single markdown report:
1. **File overview** — total sections, total lines, agent named, repo description as given.
2. **Section table** — one row per section: `Section | One-line content | Flags | Predicted Risk | Note`. Carve-out sections show `Note: safety/compliance — do not cut without review` instead of a risk score.
3. **Test this first** — the ranked shortlist (max 5) of sections to A/B, each with its one falsifiable hypothesis from step 6.
4. **Passed triage** — sections with zero flags, listed plainly (not omitted).
5. **Bottom line** — one sentence: run the full comparison now, or trim the carve-out-exempt HIGH-risk sections first and re-triage, or the file looks clean as-is.

## Guardrails
- Never state that a section *is* harming success or *is* stale as a fact — this is a prediction to prioritize testing, not a measured result. Always use hedged language ("predicted," "likely," "flagged for") and explicitly recommend the real paired A/B run before anyone deletes content based on this triage alone.
- Never assert a path, tool, or version reference is stale without either verified repo access or an explicit "unverified — confirm against repo" caveat; guessing staleness from pattern-matching alone and stating it as fact is exactly the kind of fabricated-evidence failure this skill exists to avoid committing itself.
- Never recommend removing or weakening a security, secrets-handling, deployment-gate, or compliance section, even when it also trips VERBOSE or REDUNDANT-WITH-CODE — flag it as exempt from the normal risk ranking instead.
- Never run or simulate the actual paired comparison (executing the agent twice, with/without the file) — that is the companion project's job, which requires real CLI execution against the real repo; this skill only ever produces the prioritized shortlist that run should start with.
- Never analyze a paraphrase or summary of the context file in place of its verbatim text — if the user describes the file instead of pasting it, ask for the actual text first.
- If the file has fewer than 2 sections or is too short to segment meaningfully, say so and give a single holistic verdict instead of forcing an empty or padded table.
