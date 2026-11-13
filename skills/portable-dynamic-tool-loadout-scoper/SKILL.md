---
name: portable-dynamic-tool-loadout-scoper
description: One-shot design aid that scopes a large tool/MCP catalog down to the task-relevant subset for a specific upcoming agent step, with a one-line rationale per included and excluded tool, framework-agnostic. Use before wiring any runtime tool-filtering middleware, or whenever an agent with a growing tool catalog needs a human-reviewed loadout for one step.
---

# Portable Dynamic Tool Loadout Scoper

## When to use this
Use this the moment someone is designing (not yet debugging) an agent step and the tool catalog has grown past the point where "just give it everything" feels safe — typically 15+ registered tools or MCP servers, several with overlapping capability (e.g., two search tools, three messaging tools, a file tool and a doc tool that both "read content"). The telltale phrasing: "our agent has access to too many tools now and I'm worried it'll pick the wrong one for this step" or "what's the minimal tool set this step actually needs."

This is a **design-time, advisory** skill — it recommends a loadout for a human to review and wire in manually (via a tool filter, a per-step allowlist, or a framework's tool-visibility setting). It does not run inside a live agent loop and does not modify any running system.

Do not use this for a **post-incident** diagnosis — if an agent already picked the wrong tool and you're trying to figure out why, that's a different problem (diffing two overlapping tool descriptions after a known misroute), not a pre-task scoping call.

## Inputs
**Data source**: Manual — the user pastes (1) the full tool/MCP catalog the agent currently has registered, as a list of `name: one-line description` entries (schema/parameter summaries are a bonus but not required), and (2) a description of the specific task or step the agent is about to perform (not the whole session's goal — the next concrete action). Optionally, the user also pastes (3) a maximum loadout size and/or a list of tools that must always be included regardless of relevance (e.g., a logging or safety tool). There is no mature connector that reads an agent framework's live tool/MCP registry today — the runtime version of this (wiring directly into Claude Agent SDK, LangGraph, CrewAI, or the OpenAI Agents SDK's tool-calling loop) is separate infrastructure, not this skill; this skill works from what the user pastes.

If the task/step description is missing or is really a whole multi-step goal rather than one concrete action, ask for the next single step before proceeding — scoping against a vague or multi-step goal just reproduces the "too many plausible tools" problem this skill exists to fix.

## Procedure
1. **Parse the catalog.** List every tool with its name and description, numbered, so nothing gets silently skipped.
2. **Check catalog size first.** If the catalog has fewer than ~8 tools, say so and skip scoping — recommend keeping the full catalog. Scoping below that size adds a review step without a real confusion problem to fix.
3. **Classify each tool against the task/step** (not the whole session goal) into exactly one bucket:
   - **Core** — the step cannot plausibly be done without this tool.
   - **Possible** — plausible but not clearly required; would only help in an edge case of this step.
   - **Irrelevant** — no plausible connection to this step.
4. **Flag overlaps.** For any two or more tools whose descriptions could both legitimately be called for this step (same verb/domain, e.g., two tools that both "search," two that both "post a message"), flag the group explicitly as an ambiguity risk — this is the exact "confusion" failure mode the scoping is meant to prevent, so burying it would defeat the point.
5. **Assemble the loadout:**
   - Always include every tool the user listed as mandatory.
   - Include every Core tool.
   - Include Possible tools only up to the stated max loadout size (default: Core count + up to 4 more, picking the most relevant Possible tools first); if no max was given, default budget is 8 total tools or the Core count plus 3, whichever is larger.
   - Everything else is excluded.
6. **Set a confidence flag.**
   - **HIGH** — Core vs. Irrelevant classification was clear-cut for nearly every tool.
   - **LOW** — the task description was vague, more than ~30% of tools landed in Possible, or an overlap flag touches a tool that would be Core if it were the "wrong" one of the pair. On LOW confidence, say so explicitly and recommend the full catalog as the safer fallback rather than a scoped list — do not quietly ship a guess.
7. **Write one rationale line per tool, for every tool in the catalog, included or excluded.** No tool is left unexplained.

## Output format
```
## Loadout Recommendation — <task/step name>

**Catalog size**: <n> tools | **Recommended loadout**: <m> tools | **Confidence**: HIGH | LOW

### Included
- <tool name> (Core|Possible|Mandatory) — <one-line reason tied to the step>
...

### Excluded
- <tool name> (Irrelevant|Possible, over budget) — <one-line reason>
...

### Overlap / ambiguity flags
- <tool A> vs <tool B>: <what makes them both plausible for this step, and which one this recommendation picked>
(or "None detected" if genuinely none)

### Confidence note
<If LOW: explain why, and state that the full catalog is the recommended fallback for this step.>
```

## Guardrails
- Never drop a tool from the loadout without a stated one-line reason — an unexplained exclusion is indistinguishable from a mistake to the person reviewing this.
- Never invent what a tool does beyond its given description. If a description is too thin to classify confidently, say so and default that tool to Possible rather than guessing Core or Irrelevant.
- Never exclude a tool the user explicitly marked mandatory, regardless of relevance classification.
- Never scope a catalog under ~8 tools — say explicitly that scoping isn't warranted yet.
- On LOW confidence, never present the scoped list as the primary recommendation — the full catalog fallback must be stated as the actual recommendation, with the scoped list offered only as a secondary option to review.
- This is advisory output for a human to wire in manually (a per-step allowlist or a framework tool-visibility setting) — never claim it has modified, filtered, or restricted any running agent's actual tool access.
- Do not use this to diagnose an already-occurred tool-misrouting incident — that's a forensic, after-the-fact task (comparing the tool that was wrongly called against the one that should have been) and needs the incident's actual request/response trace, not a pre-task catalog description.
