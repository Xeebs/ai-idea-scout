# Portable Dynamic Tool Loadout Scoper

A paste-into-any-AI-chat prompt that scopes a large agent tool/MCP catalog down to the subset actually relevant to one specific upcoming task step, with a one-line reason for every tool it keeps or drops. Works regardless of which agent framework you're building on (Claude Agent SDK, LangGraph, CrewAI, OpenAI Agents SDK, or none at all — it only needs the tool descriptions, not the running system).

## When to use this

Your agent's tool catalog has grown past "just give it everything" — 15+ registered tools or MCP servers, several with overlapping jobs (two search tools, three messaging tools, a file tool and a doc tool that both "read content"). You're about to have the agent take a specific step and you want to hand it only the tools that step plausibly needs, instead of the whole catalog — because the more tools an agent sees at once, the worse it gets at picking the right one, even when every tool individually works fine.

This is a design-time, advisory tool. It gives you a recommendation to review and apply by hand (a per-step allowlist, a framework's tool-visibility setting, etc.) — it does not connect to your agent or change anything live.

Do not use this to figure out why an agent already picked the wrong tool on a past run — that's a different, forensic problem that needs the actual request/response trace from the incident, not a pre-task catalog description.

## What to hand it (copy-paste this into the chat)

1. **The full tool/MCP catalog** your agent currently has registered — a list of `name: one-line description` entries. Include every tool, even ones you're sure are irrelevant; don't pre-filter.
2. **The specific task or step** the agent is about to perform next — one concrete action, not the whole session's goal. ("Reply to this GitHub issue about a 500 error" is a step; "manage our engineering backlog" is not.)
3. **(Optional) a maximum loadout size** you want to cap at, and **(optional) any tools that must always be included** no matter what (e.g., a logging or audit tool).

## The prompt

Paste this, filling in your own catalog and task:

```
I need you to scope down an agent's tool catalog to just what's relevant for one upcoming step. Here's the full catalog and the step. Follow this procedure exactly:

1. Parse the catalog — list every tool by name and description, numbered, skip nothing.
2. If the catalog has fewer than ~8 tools, say scoping isn't warranted at this size and recommend keeping the full catalog — stop there.
3. Classify every tool against the SPECIFIC STEP (not any broader goal) into exactly one bucket:
   - Core: the step cannot plausibly be done without it.
   - Possible: plausible but not clearly required, only helps in an edge case of this step.
   - Irrelevant: no plausible connection to this step.
4. Flag any pair or group of tools whose descriptions could both legitimately apply to this step (same verb/domain — e.g., two tools that both "search" or both "post a message"). Call these out explicitly as ambiguity risks.
5. Assemble the recommended loadout: always include my stated mandatory tools; include every Core tool; include Possible tools up to my stated max size (or, if I didn't give you one, Core count + 3, or 8 total, whichever is larger) — pick the most relevant Possible tools first; everything else is excluded.
6. Set a confidence flag: HIGH if the Core/Irrelevant split was clear-cut for nearly every tool; LOW if the task description was vague, more than ~30% of tools landed in Possible, or an ambiguity flag touches a tool that would be Core if it were the "wrong" one of the pair. If LOW, say so and recommend the FULL catalog as the actual fallback recommendation, with the scoped list offered only as a secondary option.
7. Give a one-line reason for every tool in the catalog, included or excluded — none left unexplained.

Never invent what a tool does beyond the description I gave you — if a description is too thin to classify confidently, default that tool to Possible and say why, rather than guessing.

Here's my catalog:
[paste name: description for every tool]

Here's the task/step:
[paste the one concrete next action]

Max loadout size (optional): [number, or "none"]
Always-include tools (optional): [list, or "none"]

Give me the output as:

## Loadout Recommendation — <task/step name>
Catalog size: <n> tools | Recommended loadout: <m> tools | Confidence: HIGH/LOW

### Included
- <tool> (Core/Possible/Mandatory) — <reason>

### Excluded
- <tool> (Irrelevant/Possible, over budget) — <reason>

### Overlap / ambiguity flags
- <tool A> vs <tool B>: <what makes both plausible, which one was picked> (or "None detected")

### Confidence note
<if LOW: why, and that the full catalog is the real recommendation>
```

## What you get back

A markdown recommendation listing which tools to expose for this one step, a one-line reason for every single tool (not just the ones kept), any overlapping tools flagged as a confusion risk, and an explicit confidence flag — if confidence is low, the honest recommendation is to keep the full catalog rather than trust a shaky scoped guess.

## Guardrails (built into the prompt above, don't skip these if you adapt it)

- Every excluded tool gets a stated reason — no silent drops.
- No catalog under ~8 tools gets scoped; the tool says so and stops.
- Mandatory tools are never excluded, regardless of relevance.
- Low confidence means the full catalog is the real recommendation, not the scoped list.
- This never claims to have changed what tools your agent can actually see — you still have to apply the recommendation yourself.
- Not for diagnosing a tool your agent already picked wrong on a real run — that needs the actual incident trace, not a catalog description.
