---
name: agent-skill-pod-shared-infra-broker
description: Scores a proposed new agent capability against a weighted fold-vs-split rubric and, when splitting wins, drafts a manifest skeleton (tools, OAuth scopes, UI fields, messaging topic). Use when a team is deciding whether to bolt a new capability onto an existing agent or spin it out as its own skill-scoped agent.
---

# Skill-Pod Fit Advisor

## When to use this
Use this when a team already running one or more production agents is about to add a new capability and is debating two options: fold the new capability into an existing "mega-agent" (more tools/prompt on the same agent), or stand it up as its own skill-scoped agent ("skill-pod"). The trigger moment is specifically the design decision before any code is written — not a general architecture review and not a request to actually build the broker/runtime infrastructure itself.

## Inputs
**Data source**: Manual — the user pastes (1) a one-paragraph description of the proposed new capability, and (2) the existing agent's current tool list and OAuth/API scopes (a bullet list or a dump of the system prompt's tool section is fine). Nothing is read from a live system; this skill never queries a running agent's config.

Required:
- One-paragraph description of what the new capability does, who/what it talks to, and how often it's expected to run.
- The current mega-agent's existing tool list and OAuth/API scopes it already holds.

Optional (improves accuracy, ask for these if missing and the user can supply them easily):
- Which team would own/maintain the new capability vs. who owns the mega-agent today.
- Whether the new capability touches data the mega-agent doesn't currently touch (PII, financial, health, etc.).
- Whether the new capability needs its own user-facing UI/form distinct from the mega-agent's existing surface.

## Procedure
1. Read the one-paragraph description and the existing tool/scope list. If either is missing, ask for it before scoring — do not guess at scopes or tool counts.
2. Score each of the 7 signals below as present (yes) or absent (no). Only mark "yes" if the input text actually supports it; do not infer a signal from vibes.

   | # | Signal | If yes | Points |
   |---|--------|--------|--------|
   | 1 | New capability needs an OAuth scope / third-party credential the mega-agent does not already hold | split pressure | +2 |
   | 2 | Adding this capability would push the mega-agent's total tool count past ~12 | split pressure | +2 |
   | 3 | New capability touches a data-sensitivity class (PII, financial, health, auth secrets) the mega-agent doesn't currently touch | split pressure | +2 |
   | 4 | New capability is owned/maintained by a different team than the mega-agent's owning team | split pressure | +2 |
   | 5 | New capability needs its own user-facing UI/form distinct from the mega-agent's existing surface | split pressure | +1 |
   | 6 | New capability needs shared conversational state/context with the mega-agent's existing tools on every turn (tight coupling) | fold pressure | -2 |
   | 7 | New capability is expected to run only sporadically/rarely relative to the mega-agent's core loop | fold pressure | -1 |

3. Sum the points (split-pressure signals add, fold-pressure signals subtract) to get a net score.
4. Apply the threshold:
   - Net score ≥ 4 → **SPLIT** (stand up a new skill-pod).
   - Net score 1–3 → **BORDERLINE** — lean fold for now, but flag it as a candidate to split later if any one more split-pressure signal appears.
   - Net score ≤ 0 → **FOLD** (add to the existing mega-agent).
5. If the recommendation is SPLIT, draft a manifest skeleton: skill name (kebab-case, derived from the capability description), the specific tools it needs, the specific OAuth scopes it needs (named, not generic), the UI fields it needs to render inputs/outputs, and a messaging topic name it would publish/subscribe to. Leave values the user didn't supply as `<TBD: ...>` placeholders rather than inventing them.
6. If the recommendation is FOLD or BORDERLINE, state which specific tool(s)/scope(s) get added to the existing agent instead, and note the single signal that would flip the decision to SPLIT if it changed.

## Output format
```
## Recommendation: SPLIT | FOLD | BORDERLINE
Net score: <n>

## Signal scoring
- [yes/no] Signal 1: New OAuth scope/credential — <one-line justification from the input>
- [yes/no] Signal 2: Tool count past ~12 — <one-line justification>
- [yes/no] Signal 3: New data-sensitivity class — <one-line justification>
- [yes/no] Signal 4: Different owning team — <one-line justification>
- [yes/no] Signal 5: Needs own UI surface — <one-line justification>
- [yes/no] Signal 6: Tight coupling to shared context — <one-line justification>
- [yes/no] Signal 7: Sporadic/rare call frequency — <one-line justification>

## If SPLIT: manifest skeleton
{
  "skill": "<kebab-case-name>",
  "tools": ["<tool-1>", "..."],
  "oauth_scopes": ["<named-scope-1>", "..."],
  "ui_fields": ["<field-1>", "..."],
  "messaging_topic": "<topic-name>"
}

## If FOLD/BORDERLINE: what to add to the existing agent instead
<specific tool(s)/scope(s) to bolt onto the mega-agent, and the one signal to watch for next time>
```

## Guardrails
- Never mark a signal "yes" without a concrete sentence from the user's input backing it — if the input doesn't say which team owns what, score signal 4 "no" and say so, don't assume.
- Never invent OAuth scope names, tool names, or UI fields for the manifest skeleton — use `<TBD: ...>` placeholders for anything the user didn't specify.
- Never recommend building or provisioning the actual shared-infra broker (Postgres schema, OAuth proxy, messaging bus) — this skill only produces a fold/split recommendation and a manifest skeleton; the broker is separate runtime infrastructure, not something this skill stands up.
- Never treat a single strong signal as automatically decisive outside the scored threshold — always report the net score and let the threshold drive the recommendation, even if it feels "obviously" one way.
- If the user's tool list is already small (fewer than 5 tools) and no other split-pressure signal is present, say explicitly that splitting now is premature even if one signal scores positive — don't let one isolated +2 override the overall picture without calling out the context.
