---
name: mcp-tool-semantic-drift-detector
description: Compares a before/after pair of pasted MCP server `list_tools` snapshots plus a description of how your integration calls the affected tools, and returns a BREAKING/WARN/SAFE classification that catches non-schema breaks (reworded descriptions, narrowed enums, changed units, altered pagination) that a plain schema diff misses. Use before accepting an MCP server version bump or a changed tool catalog.
---

# MCP Tool Semantic Drift Detector

## When to use this
You are about to upgrade (or were just notified of a `list_changed` event for) an MCP server you depend on — third-party or your own — and need to know whether the new tool catalog will break your integration before you accept it. Use this the moment you have two tool-list snapshots to compare: one from the version you're currently running, one from the version you're considering, and you want more than "did the JSON schema change" — you want to know if a reworded description, a narrowed enum, a unit change, or an altered pagination/error shape will silently break calls your code actually makes.

Do not use this for continuous, scheduled monitoring of a live server — that's a CI-pipeline job (baseline snapshotter + scheduled scan + behavioral replay against the live server), which is a separate, persistent-infrastructure build, not what this one-shot skill does. This skill only reasons over two static snapshots and whatever usage description you give it; it never executes a call against a live server.

## Inputs
**Data source**: Manual — you paste two JSON `list_tools` snapshots (the full tool array including `name`, `description`, and `inputSchema` for each tool) directly into the chat: one captured before the version/catalog change ("baseline"), one captured after ("current"). The parent idea's full project is Connected (it reads a live MCP server's `list_tools`/`call_tool` output directly); this skill is the explicit manual fallback for when you don't have that live pipeline wired up and just need a one-time pre-upgrade check.

Required:
1. **Baseline snapshot** — JSON array/object of tool definitions from the version you're running today.
2. **Current snapshot** — same shape, from the version you're about to adopt.

Strongly recommended (the report degrades to conservative-default mode without it, see Guardrails):
3. **Your calling pattern** — for each tool you actually call, which fields you set, which enum values you pass, which response fields your code reads, and any assumptions about pagination, units, or error shape. A few lines of plain English or a snippet of your actual call code both work. 1-3 real example request/response pairs you currently rely on are even better.

## Procedure
1. Parse both snapshots into `{tool name: {description, inputSchema}}` maps. If either snapshot fails to parse as valid tool-list JSON, stop and ask for a corrected paste rather than guessing at malformed input.
2. **Tool-set diff**: list tools present only in baseline (removed), only in current (added), and in both (compare below). Flag any added tool whose name/description strongly overlaps a removed tool as a likely rename, not just an unrelated add+remove pair.
3. **Structural schema diff**, per tool present in both: required-field additions/removals, type changes, enum value changes (narrowed = values removed, widened = values added, renamed = old value gone and a similar new one appears), default-value changes, and nested-property changes in complex (object/array) parameters.
4. **Description-semantic diff**, per tool present in both: compare the natural-language description text for meaning, not just literal string equality. Specifically look for and name: changed side-effect claims (e.g. "returns results" → "returns and emails results"), changed units (e.g. "size in KB" → "size in MB"), changed pagination language (e.g. "returns all results" → "returns first page, use `cursor` for more"), changed error-handling language, and any rewording significant enough that an agent choosing between tools by description alone might now pick a different tool for the same user intent.
5. **Cross-reference against the stated calling pattern** (if given): for every change found in steps 3-4, check it against what the user said they actually set/read/assume. A change only affecting a field, enum value, or behavior the user doesn't touch is SAFE for them specifically even if it would be BREAKING in general — say so explicitly ("general-purpose BREAKING, but SAFE for your stated usage because you don't pass that field").
6. **Classify every individual change** — never bundle multiple changes into one verdict — using this rubric:
   - **BREAKING**: a field/enum value/tool the stated usage depends on was removed, renamed, or narrowed to exclude a value in use; an incompatible type change on a field in use; a new required field with no default; a unit, pagination, or error-shape change on something the stated usage reads or assumes.
   - **WARN**: optional field added/removed; enum narrowed/widened on a value not confirmed in use; a description rewording that could plausibly shift tool selection or interpretation but doesn't contradict the stated explicit call; a pagination/error-shape or unit change on a tool the user calls but didn't describe precisely enough to confirm impact — unless that change lands on a field `required` in both versions, in which case it escalates to BREAKING by default (see Guardrails).
   - **SAFE**: purely additive, non-conflicting schema changes; cosmetic description edits (typos, formatting) with no meaning change; any change explicitly confirmed via the stated usage as not touched.
7. Produce the report (see Output format).
8. If the baseline or current snapshot is missing a tool the user says they call, or the usage description is too vague to resolve a specific change, list it under "Needs more info" instead of guessing — ask the specific follow-up question that would resolve it.

## Output format
A single markdown report, in this order:

```
## MCP Compatibility Report

**Summary**: N tools added, N removed, N changed, N unchanged. X BREAKING, Y WARN, Z SAFE.

| Tool | Change | Classification | Why |
|------|--------|-----------------|-----|
| search_docs | enum `format` narrowed: removed "xml" | BREAKING | your stated usage passes format="xml" |
| search_docs | description reworded: "returns all matches" → "returns first 20, use `cursor`" | WARN | pagination behavior changed; not confirmed whether your code paginates |
| get_user | added optional field `locale` | SAFE | purely additive |

### Needs more info
- <tool>: <what's ambiguous> — <specific question that would resolve it>

### Recommendation
<Safe to upgrade. | Upgrade only after addressing: <list of unresolved BREAKING items>. | Do not upgrade without further testing — behavioral changes (pagination/error shape) can't be confirmed from schema text alone; test against a staging call before accepting.>
```

Never omit the "Why" column — a bare BREAKING/WARN/SAFE label without the specific mechanism (narrowed enum, changed units, reworded description, altered pagination, etc.) is not an acceptable output.

## Guardrails
- Never report a change that isn't literally present in a diff between the two pasted snapshots — no inferring what "probably" changed between versions you weren't shown.
- Never classify a change as SAFE solely because the user didn't mention it — if no calling-pattern description was given at all, default every change that could plausibly affect a caller to WARN (never SAFE) and say explicitly in the Summary that this is a conservative default due to missing usage context.
- Exception that raises the floor from WARN to BREAKING even with no calling-pattern description: a change to a field that is `required` in both schemas (so every caller, confirmed or not, must supply it) whose *meaning* changes incompatibly — a unit change, a semantics change, an incompatible type change. There's no unconfirmed-usage escape hatch here because there's no scenario in which a caller avoids touching a required field; default this to BREAKING and say why ("required in both versions, so every caller is affected regardless of confirmed usage"). The WARN default stays in force for anything conditional on *which* value or *whether* an optional field is used (a specific enum value, an optional parameter) — those genuinely depend on usage you weren't shown.
- Never mark "safe to upgrade" as the recommendation while any BREAKING item is unresolved, even if the user seems eager to upgrade.
- Never claim to have verified live behavior (actual pagination, actual error responses, actual side effects) — this skill reasons over static text only. Any change whose real-world impact depends on execution gets flagged as a WARN with "requires a live test call to confirm," not a verified verdict.
- Never conflate this one-shot check with continuous monitoring — if the user asks to automate this on a schedule or wire it into CI, say plainly that this skill is the manual pre-upgrade version and that a scheduled/CI version needs a persistent baseline-snapshot + scan pipeline, which this skill does not run.
- If the two pasted snapshots are from genuinely different tool sets (e.g., wrong files pasted, or a different server entirely) such that the diff would be mostly noise, say so and ask for a corrected pair rather than producing a report full of spurious BREAKING verdicts.
