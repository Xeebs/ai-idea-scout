---
name: mcp-agent-tool-call-test-rig
description: Drafts a starter suite of sequencing-sensitive test scenarios (forbidden tool-call orders, required preconditions, near-miss distractors, redundant-call limits) from an MCP tool manifest, ready to drop into a tool-call sequence-assertion framework. Use when a developer has a multi-tool MCP server and no tests yet for call *order*, not just per-tool correctness.
---

# MCP Agent Tool-Call Test Rig — Scenario Drafter

## When to use this
A developer has (or is about to wire up) an MCP server with several tools an agent calls in sequence, and they have zero or thin coverage for call *order* bugs — e.g. an agent that could call `transfer_funds` before `verify_identity`, or `close_ticket` before a ticket was ever created. They already have (or are about to write) per-tool unit tests, or they're using a sequence-assertion library (pytest-style `assert_tool_order`, `assert_not_called`, `assert_max_steps`, subsequence matchers — e.g. `AgentProof`, `assay-core`, `agentguard`, or a hand-rolled equivalent). This skill does not run or score anything — it is a one-shot authoring aid that produces the scenario list a human then pastes into that framework. It does not replace a CI test runner, record/replay mock transport, or multi-model fidelity harness — those are separate, persistent infrastructure, not something a chat-pasted skill can provide.

## Inputs
**Data source**: Connected — primary path is a live MCP `tools/list` JSON-RPC call against the user's own MCP server (this call is part of the MCP spec and already implemented in every MCP SDK today, so "connected" here just means the user runs it and shares the result, not that this skill holds any credentials itself). Manual fallback — if no live server is reachable, the user pastes the tool manifest as JSON: an array of `{name, description, inputSchema}` objects (exactly what `tools/list` returns).

Required from the user:
1. The tool manifest (live JSON-RPC result or pasted JSON) — minimum 3 tools, more is better.
2. Optional but valuable: 1-2 sentences of domain context ("this is a banking ops server", "this is a support-ticket CRM") — sharpens precondition inference beyond what descriptions alone give.
3. Optional: which assertion functions their framework supports, if not the four default ones below — otherwise this skill assumes `assert_tool_order(a, b)`, `assert_not_called(tool, given=[...])`, `assert_max_steps(tool, n)`, and subsequence matching.

## Procedure
0. **State the input path.** Before anything else, note in one line whether the manifest came from a live `tools/list` call or was manually pasted — never claim a live read happened when the user pasted JSON instead.
1. **Parse the manifest.** List every tool's name, description, and input/output schema fields. If a tool has no description or an empty schema, add it to a running "Manifest Gaps" list — never guess its behavior from the name alone without flagging the guess as low-confidence.
2. **Classify each tool** into one of: read/query (verbs like `get`, `list`, `check`, `verify`, `search`), state-mutating action (`create`, `update`, `delete`, `transfer`, `freeze`, `send`, `close`, `merge`), or ambiguous (flag it).
3. **Infer precondition and forbidden-order relationships** using three signal types, in order of confidence:
   - Explicit: the description literally says "requires X", "must be called after Y", "only valid once Z is confirmed".
   - Schema-linked: one tool's output field name matches another's required input field (e.g. `get_balance` returns `account_id` that `transfer_funds` requires).
   - Domain-logic inference (lowest confidence, always labeled as such): a mutating tool that changes state tied to a value a read-only tool would check (e.g. a `transfer_funds`-shaped tool alongside a `verify_identity`-shaped or `get_balance`-shaped tool implies the mutator should never fire first).
4. **Identify near-miss distractor pairs**: tools with similar names, overlapping descriptions, or schemas that differ only slightly (e.g. `update_ticket_status` vs `close_ticket`, or `delete_contact` vs `merge_contacts`) — these are where an LLM agent is most likely to pick the wrong tool mid-sequence.
5. **Draft scenarios** in four categories, capped at roughly 2-3 scenarios per category per 10 tools in the manifest (don't pad past what the manifest actually supports):
   - **Forbidden-order** — pairs that must never fire in a given order → maps to `assert_not_called(B, after=A)` or an order assertion inverted.
   - **Required-precondition** — tool B's correct use requires tool A fired first in the same trajectory → maps to `assert_tool_order(A, B)`.
   - **Near-miss distractor** — present the agent a scenario where two similarly-named tools could both plausibly apply, and assert only the correct one was called → maps to subsequence/exact-match assertion on the correct tool.
   - **Redundant-call cap** — a read-only tool that shouldn't need calling more than N times in one trajectory → maps to `assert_max_steps(tool, n)`.
6. **Write each scenario** as a self-contained block: name, one-line setup (what the user's trajectory/prompt should attempt to do), the risky tool pair or tool, the assertion call in pseudo-code using the framework the user specified (or the four defaults), and a one-line rationale citing which manifest field(s) justified it.
7. **Close with the Manifest Gaps list** — any tool the skill could not confidently reason about, and why (missing description, no schema, genuinely no detectable relationship to other tools).

## Output format
Markdown, in this exact order:
```
Manifest source: <live tools/list call | manually pasted JSON>

## Manifest Gaps
- <tool name>: <what's missing / why confidence is low> (omit section if none)

## Forbidden-Order Scenarios
### <scenario name>
- Setup: <one line>
- Risky pair: `<tool A>` → `<tool B>` (B must never follow A without <condition>)
- Assertion: `assert_not_called("<B>", after="<A>")`  (or framework-specific equivalent)
- Rationale: <manifest evidence>

## Required-Precondition Scenarios
(same block shape, assert_tool_order)

## Near-Miss Distractor Scenarios
(same block shape, naming both candidate tools and which is correct)

## Redundant-Call Scenarios
(same block shape, assert_max_steps)
```
Each category may be empty if the manifest genuinely supports no scenarios of that type — state "None found at manifest confidence bar" rather than inventing one.

## Guardrails
- Never invent a tool, parameter, or behavior that isn't in the manifest the user provided — this skill reasons only from what it was handed, live or pasted.
- Never execute, call, or simulate actually running any tool — this is draft generation of test *descriptions*, not a test runner, mock transport, or record/replay harness (that's the separate, persistent "Test Rig" project this skill is the authoring companion to, not a replacement for).
- Always label domain-logic-inferred relationships as inferred/low-confidence, distinct from explicit or schema-linked ones — a human must verify inferred ones before trusting them in CI.
- Cap total scenario count to what the manifest's size and detail actually support; a 4-tool manifest with thin descriptions should produce a short list plus a long Manifest Gaps section, not 20 padded scenarios.
- If the manifest has fewer than 3 tools, or no tool has any mutating verb, say plainly that sequencing-sensitive testing may not be the right fit for this server and suggest per-tool happy-path testing instead — don't force forbidden-order scenarios where none plausibly exist.
