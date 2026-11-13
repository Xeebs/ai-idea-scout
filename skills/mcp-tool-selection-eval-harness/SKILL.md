---
name: mcp-tool-selection-eval-harness
description: One-shot forensic diagnosis of an MCP/agent tool-misrouting incident — paste the user intent, the tool that got called instead, and the full candidate tool list, and get back the overlap root-cause, a reworded tool description, and 2-3 regression test scenarios. Use this when an agent picked the wrong tool even though every individual tool passes its own unit tests.
---

# MCP Misroute Forensics

## When to use this
Use this the moment someone reports (or you notice) a **tool-selection failure**: an agent with multiple MCP (or other function-calling) tools registered picked the wrong tool for a request, even though the tool it picked works fine on its own and passes its own tests. The telltale phrasing: "all the tools pass their individual tests, but the agent keeps choosing the wrong one for this kind of request." This is a diagnostic tool for a single incident — it is not a continuously-running CI test suite. If what's wanted is an ongoing regression suite that gates every merge, this skill still produces the first few test cases for that suite, but running it on every PR is a separate, bigger piece of infrastructure (a "route check" harness), not this skill.

## Inputs
**Data source**: Manual — the user pastes (1) the original user request/intent verbatim, (2) the name and full description text of the tool the agent actually called, (3) the name and full description text of every other tool the agent had available to choose from (especially the one it *should* have called, if known), and (4) optionally, the system prompt or any routing instructions given to the agent. There is no mature connector that reads MCP tool registries or agent trace logs directly today — this is forensic incident data a developer copies out of logs, a support ticket, or a terminal session, so it has to be pasted in.

If any of (1)-(3) is missing, do not guess. Ask for it explicitly before proceeding — a diagnosis built on an assumed tool description is worse than no diagnosis, because it will produce a confident-sounding but wrong root cause.

## Procedure
1. **Extract the incident.** Restate in one line: "User asked for X, the agent called tool A (should have called tool B)." If the user doesn't know what the "right" tool was, infer the most plausible candidate from the pasted tool list and flag the inference as unconfirmed rather than stated fact.
2. **Diff the descriptions.** Line up tool A's description against tool B's (and against any other tool in the list with meaningful overlap). Identify the specific shared words, verbs, domain nouns, or example phrases that make both tools look like valid matches for the request. Quote the exact overlapping phrase from each description — don't summarize vaguely as "the descriptions are similar."
3. **Identify the missing boundary.** Tool descriptions usually say what a tool does but not when *not* to use it. Name the boundary condition that's absent (e.g., tool A's description never excludes "sentiment/opinion" requests even though tool B owns that domain).
4. **Check for system-prompt interference.** If a system prompt or routing instruction was provided, scan it for keyword-triggered rules (e.g., "always use X when the user mentions 'report'") that could override good descriptions on their own. Note this separately from the description-overlap root cause — it's a distinct failure mode with a different fix (edit the system prompt, not the tool description).
5. **Write the fix.** Propose a concrete rewording of the offending tool's description (and the correct tool's, if it also lacks a boundary) that adds an explicit "use this for / do NOT use this for" line disambiguating the two. Keep the rewrite short enough to still work as a function-calling schema description (1-3 sentences), not a paragraph.
6. **Generate regression scenarios.** Write 2-3 new test cases in the format `intent -> expected_tool` that would have caught this exact failure, including at least one deliberate near-miss distractor phrased close to the original failing request but for the genuinely-correct tool, and one phrased to confirm the fix doesn't break the tool that correctly handled similar requests before.
7. **State confidence and limits.** If descriptions alone can't fully explain the misroute (e.g., both descriptions are already well-bounded and distinct), say so plainly instead of forcing a root cause — the real cause may be model-specific tool-calling behavior, too many tools in context, or a system-prompt conflict, and the diagnosis should name which of those is most likely rather than overclaim certainty.

## Output format
A single markdown report with these sections, in this order:

```
## Incident Summary
<one line: intent -> tool called (vs. tool expected)>

## Root Cause: Description Overlap
- Chosen tool ("<name>"): "<quoted overlapping phrase>"
- Expected tool ("<name>"): "<quoted overlapping phrase>"
- Missing boundary: <what neither description rules out>

## System Prompt Interference (only if a system prompt was provided)
<keyword rule found, or "none found">

## Suggested Description Rewrite
**<tool name>** — current: "<original>"
Rewrite: "<new description with explicit use/don't-use boundary>"

## Regression Scenarios to Add
```yaml
- intent: "<near-identical phrasing to the original failing request>"
  expected_tool: <correct tool name>
- intent: "<distractor that still tests the boundary>"
  expected_tool: <correct tool name>
- intent: "<confirms the previously-correct routing still works>"
  expected_tool: <the tool that handled similar requests correctly before>
```

## Confidence & Limits
<what this diagnosis is sure of, what it isn't, and what to check next if the rewrite doesn't fix it>
```

## Guardrails
- Never fabricate a tool's description, behavior, or name beyond what was pasted in — if a needed detail is missing, ask, don't invent.
- Never state a root cause as certain when the evidence is ambiguous; say "most likely cause" and name the runner-up explanation.
- Never propose removing or merging tools as the fix unless the user explicitly asks for that — the smallest viable fix is a description rewrite plus a regression case, not an architecture change.
- Never produce regression scenarios in exact-duplicate phrasing of the original failing request only — always include at least one near-miss distractor, since a one-exact-case regression test is trivially satisfied without fixing the real ambiguity.
- Never claim this diagnosis by itself constitutes a CI-gating test suite — it produces incident-specific scenarios a developer then adds to whatever suite (or ad hoc test file) they maintain; this skill does not run or gate anything.
- Never hide which parts of the output are inferred (e.g., an assumed "expected tool") vs. directly stated by the user — mark inferences clearly.
