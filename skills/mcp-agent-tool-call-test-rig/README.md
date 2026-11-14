# MCP Agent Tool-Call Test Rig — Scenario Drafter

A paste-anywhere prompt template that turns an MCP (Model Context Protocol) tool manifest into a starter suite of **sequencing-sensitive test scenarios** — the kind of bugs that only show up when an AI agent calls your tools in the *wrong order*, not when each tool is tested alone.

## Why this exists

Most MCP testing help you'll find online drafts per-tool unit tests: happy path, invalid input, maybe one edge case, for each tool individually. That's useful but it misses a whole class of real bugs: an agent that calls `transfer_funds` before `verify_identity`, or `close_ticket` before a ticket was ever created, or picks `delete_contact` when it meant `merge_contacts` because the names and descriptions are nearly identical. Those bugs only exist across a *trajectory* of calls, not inside any single tool. This skill drafts exactly that kind of scenario — forbidden call orders, required preconditions, near-miss tool-name confusions, and redundant-call limits — so you have something concrete to drop into a sequence-assertion test framework (your own, or an existing one like a pytest plugin with `assert_tool_order` / `assert_not_called` / `assert_max_steps` style functions).

This is a one-shot authoring aid, not a test runner. It does not execute anything, mock any transport, or record/replay real traffic — it only writes the scenario descriptions you'd then implement or paste into your own test suite.

## What you need to provide

**Data source**: Connected — ideally, run your MCP server's `tools/list` call yourself (this is a standard part of the MCP protocol; every MCP SDK today can produce this list) and paste the JSON result here. Manual fallback — if you don't have a live server handy, paste the tool manifest as JSON directly: an array of objects with `name`, `description`, and `inputSchema` for each tool, i.e. exactly what `tools/list` returns.

Hand this skill:
1. The tool manifest (required, minimum 3 tools — fewer than that and sequencing tests usually aren't the right fit).
2. One or two sentences of domain context, e.g. "this is a banking back-office server" or "this is a support-ticket CRM bundle" — this sharpens the precondition and forbidden-order guesses well beyond what tool descriptions alone give.
3. (Optional) The exact assertion function names your test framework uses, if different from the defaults: `assert_tool_order(a, b)`, `assert_not_called(tool, after=...)`, `assert_max_steps(tool, n)`, and subsequence/exact-match checks.

## What the skill does, step by step

0. **States the input path first** — one line noting whether it's working from a live `tools/list` call or a manually pasted manifest, so you always know which Data Source path produced the output.
1. **Reads every tool** in the manifest: name, description, input/output schema fields. Any tool with no description or an empty schema gets flagged in a "Manifest Gaps" list rather than guessed at.
2. **Classifies each tool** as read/query (verbs like get, list, check, verify, search), state-mutating (create, update, delete, transfer, freeze, send, close, merge), or ambiguous.
3. **Infers relationships between tools** using three confidence tiers, always labeled:
   - **Explicit** — the description literally states a dependency ("requires an active session", "only valid after X").
   - **Schema-linked** — one tool's output field matches another's required input field (e.g. a `get_balance`-style tool returns an `account_id` that a `transfer_funds`-style tool requires).
   - **Domain-logic inferred** (lowest confidence, always marked as inferred) — a mutating tool paired with a read-only tool that logically should gate it, based on the domain context you gave.
4. **Finds near-miss distractor pairs** — tools with similar names or overlapping descriptions where an agent could plausibly pick the wrong one mid-sequence (e.g. `update_ticket_status` vs. `close_ticket`).
5. **Drafts scenarios** in four categories, sized to how much the manifest actually supports (roughly 2-3 scenarios per category per 10 tools — it won't pad a thin manifest with invented scenarios):
   - Forbidden-order pairs
   - Required-precondition sequences
   - Near-miss distractor cases
   - Redundant-call caps (a read-only tool shouldn't need N+ calls in one trajectory)
6. **Writes each scenario** as a short, self-contained block with a setup line, the risky tool pair, a pseudo-code assertion call mapped to your framework's functions (or the four defaults above), and a one-line rationale citing the manifest evidence behind it.
7. **Ends with a Manifest Gaps section** listing any tool it couldn't confidently reason about and why.

## Output format

Markdown, always in this order, with any empty category stating "None found at manifest confidence bar" instead of being padded:

```
Manifest source: <live tools/list call | manually pasted JSON>

## Manifest Gaps
- <tool>: <what's missing>

## Forbidden-Order Scenarios
### <name>
- Setup: ...
- Risky pair: toolA -> toolB
- Assertion: assert_not_called("toolB", after="toolA")
- Rationale: ...

## Required-Precondition Scenarios
(same shape, assert_tool_order)

## Near-Miss Distractor Scenarios
(same shape, names both candidate tools and the correct one)

## Redundant-Call Scenarios
(same shape, assert_max_steps)
```

## Guardrails — what this skill will never do

- Never invents a tool, field, or behavior not present in the manifest you gave it.
- Never executes, calls, or simulates actually running a tool — it writes test *descriptions* only.
- Always labels inferred (domain-logic) relationships as such, separately from explicit or schema-linked ones, so you know which ones need your own sanity check before they go into CI.
- Never pads scenario count past what a thin or sparsely-described manifest actually supports — a small or under-documented manifest gets a short scenario list and a longer Gaps section instead.
- If your manifest has fewer than 3 tools, or no mutating tools at all, it will say plainly that sequencing tests may not be the right fit and suggest per-tool happy-path testing instead.

## How to use this

Paste this whole README into any AI chat tool (Claude, ChatGPT, etc.) along with your tool manifest JSON and a line of domain context, then ask it to draft the scenario suite following the procedure and output format above.
