# Skill File Structure

Produced only for ideas tagged **SKILL** or **BOTH** in `.claude/rules/idea-format.md`. One directory per skill, flat under `skills/` (this repo is single-domain, so no industry subfolders):

```
skills/
  <skill-slug>/
    SKILL.md            # Claude Code skill format
    README.md           # Portable — self-contained prompt template for any AI tool
    tests/
      scenario-1.md      # Realistic test input + expected output criteria
      scenario-2.md
```

`<skill-slug>` matches the parent idea's filename in `ideas/` (e.g. idea `agent-escalation-policy-engine.md` → skill `skills/agent-escalation-policy-engine/`).

## SKILL.md contents

```markdown
---
name: <skill-slug>
description: One line — what it does and when Claude should reach for it.
---

# <Skill Title>

## When to use this
The exact trigger moment — what the user says or what state they're in when this skill applies.

## Inputs
What the user needs to hand over for this to work (files, context, a specific question). Open with one line restating the parent idea's **Data Sources** classification exactly: `**Data source**: Manual — <what gets pasted>` or `**Data source**: Connected — <named API/connector, and whether it's mature today>`. This is the single line a reviewer checks first; never omit it or soften it into vaguer prose.

## Procedure
Step-by-step instructions Claude follows. Be concrete — this is the actual logic, not a summary of it.

## Output format
Precisely what gets produced and how it's structured.

## Guardrails
Explicit "never do X" list — the failure modes that would make this skill harmful or useless if skipped.
```

## README.md contents

A fully self-contained prompt template usable by someone with no Claude Code installation — paste-into-any-chat-tool format. Must stand alone: restate the procedure and output format in prose, don't just say "see SKILL.md".

## Test scenarios

Each `scenario-N.md` is a realistic input (a real-shaped example, not a toy) plus a checklist of pass/fail criteria an evaluator (human or agent) can check the output against. No `result.md` is required before publishing — unlike Grimoire, this pipeline does not run a dedicated QA pass; the skill-synthesizer self-checks against its own scenarios before reporting back, and the publisher does the final read before anything goes out.

## Quality bar

A skill must be:
1. **Specific** — targets one named task/trigger, not a broad "help with X" prompt.
2. **Novel** — if the skill-synthesizer's search turns up 3+ close public equivalents, it must differentiate clearly or the idea stays Format: PROJECT only (drop the skill angle, note why in the idea file).
3. **Self-contained** — a reader with zero prior context in this repo can use the README version immediately.
4. **Tested against its own scenarios** — the synthesizer runs the procedure mentally (or actually, via Bash/Read tools where the scenario allows) against both test scenarios before reporting done.
