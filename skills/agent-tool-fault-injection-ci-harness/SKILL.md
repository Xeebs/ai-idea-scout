---
name: agent-tool-fault-injection-ci-harness
description: Drafts a per-tool fault-injection test plan (timeouts, HTTP 429s, malformed responses) and a declared safe-degradation policy for each tool, from an MCP tool manifest, ready to drop into a fault-injection/assertion harness or hand-build. Use when a developer has a tool-calling agent that has only ever been tested against happy-path tool responses.
---

# Agent Tool Fault-Injection CI Harness — Test Plan Drafter

## When to use this
A developer has (or is about to wire up) an MCP-based or tool-calling agent whose tools call real external APIs — payment processors, CRMs, internal services — and they have zero or thin coverage for what the agent does when a tool call times out, gets rate-limited, or returns a malformed/unexpected response. They already have, or are about to write, a fault-injection stub (a transport interceptor that can delay, reject, or corrupt a tool's response on command — hand-rolled, or a package exposing something like `inject_timeout(tool, after_ms)`, `inject_429(tool, retry_after)`, `inject_malformed(tool, shape)`). This skill does not run or inject anything itself — it is a one-shot authoring aid that produces the fault scenarios and per-tool recovery-policy specs a human then pastes into that harness, or uses as a checklist while hand-building one. It does not replace a CI test runner, a transport interceptor, or a persistent regression suite — those are separate, standing infrastructure a chat-pasted skill cannot provide.

## Inputs
**Data source**: Connected — primary path is a live MCP `tools/list` JSON-RPC call against the user's own MCP server (this call is part of the MCP spec and already implemented in every MCP SDK today, so "connected" here just means the user runs it and shares the result, not that this skill holds any credentials or makes any live calls itself). Manual fallback — if no live server is reachable, the user pastes the tool manifest as JSON: an array of `{name, description, inputSchema}` objects (exactly what `tools/list` returns).

Required from the user:
1. The tool manifest (live JSON-RPC result or pasted JSON) — minimum 3 tools, more is better.
2. Optional but valuable: for each tool, what the real backing API actually does on failure today (e.g. "the payments API returns HTTP 429 with a `Retry-After` header"; "the CRM API has no documented timeout, we've seen it hang 20s+"). Without this, fault parameters are generic placeholders, not grounded in the real API.
3. Optional: which idempotency guarantees exist on the mutating tools (e.g. "transfer_funds accepts an idempotency key"). This materially changes whether retry-on-timeout is a safe default.

## Procedure
0. **State the input path.** Before anything else, note in one line whether the manifest came from a live `tools/list` call or was manually pasted — never claim a live read happened when the user pasted JSON instead.
1. **Parse the manifest.** List every tool's name, description, and input/output schema fields. If a tool has no description or an empty schema, add it to a running "Manifest Gaps" list — never guess its behavior from the name alone without flagging the guess as low-confidence.
2. **Classify each tool's retry-safety**, using name verbs and description as signal:
   - **Idempotent/read-only** (`get`, `list`, `check`, `verify`, `search`, `fetch`) — safe to retry on timeout/429 with backoff by default.
   - **Mutating, declared idempotent** (description or user context states an idempotency key/token exists) — safe to retry only with that key reused, not as a fresh call.
   - **Mutating, no idempotency signal** (`create`, `charge`, `transfer`, `delete`, `send`, `close`, `merge` with no stated idempotency guarantee) — retry-on-timeout is UNSAFE by default (risk of double-execution); flag this explicitly rather than assuming a safe default.
   - **Ambiguous** — flag it; do not assign a retry policy without saying so.
3. **Draft a per-tool recovery-policy spec** for every tool: what counts as safe degradation for *that* tool specifically (e.g. "on timeout: retry once with backoff, idempotency key reused, else surface 'payment pending, check status' — never silently retry a fresh charge"; "on malformed response: never treat partial/corrupt JSON as a valid balance figure — must raise and ask the user to retry").
4. **Draft fault scenarios** in four categories, capped at roughly 2-3 scenarios per category per 10 tools in the manifest (don't pad past what the manifest supports):
   - **Timeout injection** — tool hangs past a plausible or user-stated threshold. Assert: no infinite retry loop, no silent fabricated result, policy from step 3 is followed.
   - **Rate-limit (429) injection** — tool returns 429, optionally with `Retry-After`. Assert: backoff honors `Retry-After` if present, doesn't hammer the API, surfaces a graceful wait/degrade message if retries exhaust.
   - **Malformed-response injection** — tool returns a response that's valid transport but wrong shape (missing required field, wrong type, truncated JSON, empty success envelope). Assert: the agent never treats this as valid data and silently continues (the single highest-severity failure mode — a fabricated balance, a "ticket closed" that never happened).
   - **Cascading/combined fault** — two tools in the same trajectory fault in sequence (e.g. tool A times out, agent retries and calls tool B which then 429s) — only draft this category if the manifest has ≥4 tools with an inferable call relationship; otherwise state "skipped — insufficient multi-tool signal."
5. **Write each scenario** as a self-contained block: tool name, fault type and parameters (using placeholder values clearly marked `[placeholder]` unless the user supplied real API behavior in step 2 of Inputs), the pseudo-code harness call, the expected-safe assertion, the specific unsafe behavior this scenario is designed to catch, and a one-line rationale citing which manifest field or user-supplied context justified it.
6. **Close with two lists**: "Manifest Gaps" (tools the skill could not confidently reason about, and why) and "Needs Real API Behavior" (every placeholder fault parameter that should be replaced with the tool's actual documented or observed failure behavior before this plan is trusted as realistic).

## Output format
Markdown, in this exact order:
```
Manifest source: <live tools/list call | manually pasted JSON>

## Manifest Gaps
- <tool name>: <what's missing / why confidence is low> (omit section if none)

## Per-Tool Recovery-Policy Specs
### <tool name> — <retry-safety class>
- Safe degradation: <what "safe" means for this specific tool>
- Retry policy: <retry/no-retry, backoff shape, idempotency note>

## Timeout Injection Scenarios
### <scenario name>
- Tool: `<tool name>`
- Fault: `inject_timeout(tool="<name>", after_ms=<value>[placeholder])`
- Expected-safe assertion: <pseudo-code, e.g. assert_recovers_within(retries=1, backoff="exponential")>
- Catches: <specific unsafe behavior, e.g. "infinite retry loop with no backoff">
- Rationale: <manifest/context evidence>

## Rate-Limit (429) Injection Scenarios
(same block shape, inject_429)

## Malformed-Response Injection Scenarios
(same block shape, inject_malformed, naming the specific malformed shape e.g. "missing `amount` field", "truncated JSON", "success envelope with null body")

## Cascading Fault Scenarios
(same block shape, or "Skipped — insufficient multi-tool signal")

## Needs Real API Behavior
- <tool>: <which placeholder value needs replacing with the real documented/observed failure mode>
```
Each category may be empty if the manifest genuinely supports no scenarios of that type — state "None found at manifest confidence bar" rather than inventing one.

## Guardrails
- Never claim a live `tools/list` read happened when the user pasted JSON instead, and vice versa — state the actual source every time.
- Never assign a "safe to retry" policy to a mutating tool with no stated idempotency guarantee — flag it as unsafe-by-default and say why, even if that makes the plan less tidy.
- Never invent a specific real-world fault parameter (an exact timeout threshold, a real `Retry-After` value, a real error payload shape) and present it as fact — mark every parameter not supplied by the user as `[placeholder]` and list it in "Needs Real API Behavior."
- Never treat a malformed-response scenario as lower priority than a timeout scenario — fabricated-result-treated-as-real is the highest-severity failure mode this plan exists to catch, and every tool that returns structured data needs at least one malformed-response scenario.
- Never draft a scenario for a tool the manifest gives no real signal about (empty schema, no description, no user context) — put it in Manifest Gaps instead of guessing.
- Never claim this plan has been executed, that the harness caught anything, or that the agent's actual behavior is known — this skill only authors the test plan; running it and reading the results is the user's and the harness's job, not this skill's.
- Do not conflate this with call-*order* testing (forbidden sequences, preconditions) — that is a different skill and a different failure class; this plan is scoped to reliability-under-fault (timeouts, rate limits, malformed data), not sequencing correctness.
