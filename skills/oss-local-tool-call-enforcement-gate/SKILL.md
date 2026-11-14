---
name: oss-local-tool-call-enforcement-gate
description: Drafts an OPA/Rego policy (default-deny) plus allow/deny test cases and wiring notes for gating a specific agent tool call, from a plain-English safety rule — for anyone adopting a local, fully-free tool-call enforcement gate (e.g. a cupcake-style Wasm gate, MCP server middleware, or a LangChain/CrewAI callback) who doesn't want to hand-write Rego. Use when the user describes a rule they want enforced on an agent's tool calls and names (or pastes) the tool's argument schema.
---

# OSS Local Tool-Call Enforcement Gate — Policy Drafting Companion

## When to use this
The user is running (or setting up) a local, in-process agent tool-call enforcement gate — a Rego/OPA-to-Wasm gate (e.g. `eqtylab/cupcake` or a fork of it), MCP server-side middleware, or a LangChain/CrewAI tool-call callback — and says something shaped like "I want to block/require confirmation for [some tool call] when [some condition]" or "never let the agent [destructive action] without asking." This skill does not run as the gate itself; it is a one-shot drafting aid invoked each time the user wants to add a new rule.

## Inputs
**Data source**: CONNECTED per the parent idea (the gate itself intercepts tool calls at a mature framework hook — MCP middleware, a LangChain/CrewAI callback, or a Rego/Wasm pre-call hook). This companion skill is the drafting half, not the live gate, so its own concrete inputs are Manual — the user must hand over, in the chat:
1. **The plain-English rule** — e.g. "never let the agent delete files outside /workspace without confirmation."
2. **The tool-call schema being gated** — the exact tool name and its argument names/types, pasted from the user's MCP server manifest, LangChain `@tool` definition, or framework tool registry (e.g. `delete_file(path: string)`). Do not proceed without this — guessing a schema the user didn't provide is the single most common way this kind of draft ships broken.
3. **The integration point** (optional but preferred) — one of: MCP server middleware, LangChain/CrewAI callback, cupcake-style Rego/Wasm pre-call hook, or "not sure yet." Defaults to generic Rego + a short note on all three if omitted.

## Procedure
1. Parse the plain-English rule into its components: the triggering tool(s), the condition(s) that make a call unsafe, and the required disposition (hard block vs. require human confirmation vs. allow with audit log).
2. If the tool-call schema wasn't given, stop and ask for it by name — do not invent argument names.
3. If the plain-English rule is ambiguous about scope (e.g. "outside /workspace" — does this cover relative paths, symlinks, `../` traversal, or only literal absolute-path arguments?), state the ambiguity explicitly and pick the stricter interpretation as the draft default, flagged as an assumption the user must confirm.
4. If the condition requires parsing free-form content rather than matching a structured argument (e.g. the argument is a raw shell command string, not discrete fields), say so explicitly: Rego can only do string/regex matching on that argument, not true command parsing, so the draft is pattern-based and can be bypassed by obfuscation (e.g. quoting, variable expansion, encoding). Recommend defense-in-depth (e.g. also allow-listing safe commands) rather than presenting the pattern match as complete coverage.
5. Draft the Rego policy:
   - Explicit `default allow := false` (or the gate's equivalent deny-by-default field) — never default-allow.
   - A `package` name derived from the tool name.
   - One rule per disposition the plain-English request implies (e.g. a `deny` rule and a separate `confirm`/`ask` rule if the request wants human-in-the-loop rather than a hard block).
   - Plain-English comments above each rule line tying it back to the specific clause of the user's request it implements.
6. Draft a paired test file using `opa test` conventions: at minimum one test case where the call should be allowed and one where it should be blocked/confirmed, each constructed from the exact schema given in step 2 (not invented field names), each test name stating which clause of the rule it checks.
7. Write wiring notes for the stated integration point (or all three, briefly, if none was stated): where this policy file goes, what the hook call looks like (e.g. the MCP middleware call that evaluates the Wasm-compiled bundle against the incoming tool call, or the LangChain callback's `on_tool_start` check), and the exact local command to validate the policy on its own before wiring it in (`opa test <file>.rego` or `opa eval -d <policy>.rego -i <input>.json "data.<package>.allow"`).
8. Close with one line reminding the user this is a draft to review and test against their actual gate before relying on it in production — never claim it has already been validated against their live system.

## Output format
A single Markdown response with four sections, in this order:
1. **Assumptions & scope notes** — any ambiguity called out in step 3/4, stated as bullets, before any code.
2. **Policy** — the Rego policy in a fenced ```rego block.
3. **Tests** — the Rego test file in a fenced ```rego block, each test function named to describe its scenario.
4. **Verify & wire it in** — the exact `opa test`/`opa eval` command to run locally, followed by a short paragraph of wiring notes for the named integration point.

## Guardrails
- Never invent a tool name or argument name the user didn't provide — ask instead of guessing.
- Never ship a policy with an implicit or default-allow — every draft must default-deny explicitly.
- Never present a string/regex-based match over free-form content (shell commands, URLs, file paths with possible traversal) as complete coverage — always name the bypass classes it can't catch.
- Never claim the draft has been tested against the user's actual framework or live tool calls — it has only been checked for internal consistency against the schema given; the user must run the tests themselves.
- Never silently resolve an ambiguous scope question by picking the looser (more permissive) interpretation — default to the stricter reading and flag it.
