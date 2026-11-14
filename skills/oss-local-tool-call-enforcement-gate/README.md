# OSS Local Tool-Call Enforcement Gate — Policy Drafting Companion

Paste the prompt below into any AI chat tool (Claude, ChatGPT, etc.) when you're adopting a local, fully-free agent tool-call enforcement gate — a Rego/OPA-to-Wasm gate like `eqtylab/cupcake` (or a fork of it), MCP server-side middleware, or a LangChain/CrewAI tool-call callback — and you want to add a new safety rule without hand-writing Rego yourself.

This is a **drafting companion**, not the gate itself. It does not intercept or run anything live. It turns a plain-English rule into a reviewable Rego policy draft, a paired test file, and wiring notes — you still run the tests and wire it into your own gate.

## Data source

This skill's own inputs are **Manual**: you type/paste the rule and the tool's argument schema into the chat. (The underlying enforcement *gate* this skill is a companion to is Connected — it hooks into a mature extension point like MCP middleware, a LangChain callback, or a Rego/Wasm pre-call hook already built into the agent framework — but this drafting skill itself reads nothing live; it only works with what you paste in.)

## What to hand over

Before running this, have three things ready:

1. **The rule, in plain English.** Example: "never let the agent delete files outside /workspace without asking for confirmation first."
2. **The exact tool-call schema being gated** — the tool's name and its argument names/types, copied from your MCP server manifest, your LangChain `@tool` definition, or wherever your framework declares tools. Example: `delete_file(path: string)`. Don't paraphrase this — paste the real names, because a drafted policy that references the wrong field name silently does nothing.
3. **(Optional) Which integration point you're using** — MCP server middleware, a LangChain/CrewAI callback, or a cupcake-style Rego/Wasm pre-call hook. If you're not sure yet, say so; the output will include a short note for all three.

## The prompt

```
I'm adding a rule to a local agent tool-call enforcement gate. Act as a Rego/OPA policy drafting assistant for this.

My rule (plain English): <paste your rule here>

Tool schema being gated: <tool name and argument names/types, exact>

Integration point: <MCP middleware | LangChain/CrewAI callback | cupcake-style Rego/Wasm hook | not sure yet>

Do the following, in this order, and don't skip any step:

1. Break my rule into: which tool call(s) it applies to, what condition makes a call unsafe, and whether the disposition should be a hard block, a human-confirmation step, or allow-with-audit-log.
2. If I didn't give you the exact argument names, stop and ask me for them instead of guessing.
3. If my rule is ambiguous about scope (e.g. "outside X" — does that cover relative paths, symlinks, or traversal like "../"?), call out the ambiguity explicitly and default to the STRICTER interpretation, flagged as an assumption for me to confirm — never silently pick the looser one.
4. If the condition requires parsing free-form text (like a raw shell command string) rather than matching a clean field, tell me plainly that Rego can only pattern-match that, not truly parse it, and name the specific ways someone could bypass the pattern (quoting, encoding, variable expansion). Don't present a regex match as complete coverage.
5. Draft a Rego policy with an explicit default-deny (never a default-allow), one rule per disposition my rule implies, and a plain-English comment above each rule line tying it back to my original request.
6. Draft a paired Rego test file (opa test style) with at least one test that should be ALLOWED and one that should be BLOCKED/require confirmation, built from the exact schema I gave you — not invented field names. Name each test after the scenario it checks.
7. Give me the exact local command to validate the policy on its own (opa test or opa eval), plus a short paragraph on how to wire this into the integration point I named (or a brief note for each of the three if I wasn't sure).
8. End with one line reminding me this is a draft I need to run and review myself — you have not tested it against my live system.

Format your answer as:
- "Assumptions & scope notes" (bullets, before any code)
- "Policy" (Rego code block)
- "Tests" (Rego code block)
- "Verify & wire it in" (the command, then the wiring paragraph)
```

## What you get back

A single response with four sections in this exact order: assumptions/scope notes called out up front, the Rego policy, the paired test file, and a verify-and-wire-in section with the exact command to run locally plus wiring notes for your stated integration point.

## What this will refuse to do

- It will not guess your tool's argument names — if you didn't give them, it asks first.
- It will never draft a policy that defaults to allow.
- It will never claim a regex/string match on free-form content (shell commands, paths, URLs) is complete — it names what it can't catch.
- It will never claim the draft has been tested against your actual running system — you run `opa test` yourself.
- It will never resolve an ambiguous rule by quietly picking the more permissive reading.

If any of those show up in the output, the draft is unreliable — ask it to redo the step it skipped.
