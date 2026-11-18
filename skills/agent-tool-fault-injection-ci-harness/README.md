# Agent Tool Fault-Injection CI Harness — Test Plan Drafter

A self-contained prompt template. Paste the block below into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.), fill in the bracketed inputs, and it will draft a fault-injection test plan for your tool-calling agent — what to break, how to break it, and what "safe" recovery looks like per tool. It does not run anything. It produces the test plan you then hand to a fault-injection harness (a transport interceptor that can delay, reject, or corrupt a tool's response on command) or use as a checklist while hand-building one.

## When to use this

Use this when you have a tool-calling agent (MCP-based or otherwise) whose tools call real external APIs — payment processors, CRMs, internal services, anything that can legitimately time out, rate-limit, or return a malformed response — and you have only ever tested it against happy-path tool responses. You're about to find out the hard way what your agent does when a dependency fails, unless you test it on purpose first.

This does not replace a CI runner or a transport-level fault injector. It drafts the scenarios you feed into one.

## What to hand it

1. **Your tool manifest.** Either:
   - A live `tools/list` JSON-RPC result from your MCP server (paste the raw JSON), or
   - A manually written list of your tools as JSON: `[{"name": "...", "description": "...", "inputSchema": {...}}, ...]`
   - Minimum 3 tools. State clearly which of the two you're providing.
2. **(Optional, strongly recommended) Real failure behavior.** For any tool where you know how the real backing API actually fails — e.g. "the payments API returns HTTP 429 with a `Retry-After` header," "the CRM API has no documented timeout but we've seen it hang 20+ seconds in production" — include it. Without this, the plan uses generic placeholder values and says so.
3. **(Optional) Idempotency notes.** For mutating tools (anything that creates, charges, transfers, deletes, sends, or closes something), say whether it accepts an idempotency key or token. This changes whether retrying on timeout is safe or dangerous.

## The prompt template

```
You are drafting a fault-injection test plan for my tool-calling agent. Do not run
anything or claim you have tested anything — you are producing a test plan I will
feed into a fault-injection harness (or hand-build one from your scenarios).

My tool manifest source: [LIVE tools/list CALL / MANUALLY WRITTEN JSON]
My tool manifest:
[PASTE JSON HERE — array of {name, description, inputSchema}, minimum 3 tools]

Known real failure behavior (optional, leave blank if unknown):
[e.g. "payments_api: real 429 with Retry-After header, typical retry-after 5-10s"]

Idempotency notes on mutating tools (optional, leave blank if unknown):
[e.g. "charge_card accepts an idempotency_key parameter"]

Follow this procedure:

1. State whether the manifest came from a live call or manual paste — don't
   mix this up.
2. Parse every tool: name, description, schema fields. Flag any tool with no
   description or empty schema as a "Manifest Gap" — don't guess its behavior
   from the name alone without saying the guess is low-confidence.
3. Classify each tool's retry-safety:
   - Idempotent/read-only (get/list/check/verify/search/fetch) → safe to retry
     on timeout/429 with backoff by default.
   - Mutating with a stated idempotency key → safe to retry ONLY reusing that
     key, never as a fresh call.
   - Mutating with NO stated idempotency guarantee (create/charge/transfer/
     delete/send/close/merge) → retry-on-timeout is UNSAFE by default (risk of
     double-execution) — flag this explicitly even if it makes the plan messier.
   - Ambiguous → flag it, don't assign a policy.
4. Write a per-tool recovery-policy spec: what "safe degradation" means for
   THAT specific tool (not a generic rule) — covering timeout, rate-limit, and
   malformed-response behavior.
5. Draft fault scenarios in four categories (skip a category and say so if the
   manifest doesn't support it — don't pad):
   - Timeout injection — tool hangs. Does the agent loop forever, fabricate a
     result, or degrade safely per the policy in step 4?
   - Rate-limit (429) injection — tool returns 429, optionally with
     Retry-After. Does the agent honor it, or hammer the API?
   - Malformed-response injection — tool returns wrong-shaped data (missing
     field, wrong type, truncated JSON, empty success envelope). Does the agent
     ever treat this as real data and continue silently? This is the highest-
     severity failure mode — every data-returning tool needs at least one of
     these scenarios.
   - Cascading fault — two tools fault in the same trajectory. Only draft this
     if the manifest has 4+ tools with an inferable call relationship;
     otherwise write "skipped — insufficient multi-tool signal."
6. For each scenario give: tool name, fault type + parameters (mark anything
   not grounded in my stated real failure behavior as [placeholder]), the
   expected-safe behavior, the specific unsafe behavior it's designed to catch,
   and a one-line rationale.
7. Close with two lists: "Manifest Gaps" and "Needs Real API Behavior" (every
   placeholder parameter I should replace with real documented/observed values
   before trusting this plan as realistic).

Never claim you ran anything. Never invent a specific real-world timeout
threshold, Retry-After value, or error payload and present it as fact — mark
it as a placeholder if I didn't supply it. Never assign "safe to retry" to a
mutating tool with no idempotency guarantee.
```

## What you get back

A markdown test plan with, in order: the manifest source statement, a Manifest Gaps list, a per-tool recovery-policy spec for every tool, scenario blocks grouped under Timeout / Rate-Limit / Malformed-Response / Cascading headings (each with tool, fault call, expected-safe assertion, what unsafe behavior it catches, and rationale), and a closing "Needs Real API Behavior" list of every placeholder you should go fill in with the truth before you trust the plan.

## What this does NOT do

- It does not inject any faults or run any tests — you still need a transport interceptor / fault-injection harness (hand-rolled, or an existing package) to actually execute the scenarios.
- It does not know your API's real timeout/rate-limit behavior unless you tell it — unstated values are placeholders, not facts.
- It does not test call *order* or sequencing bugs (e.g. "tool B fired before tool A should have") — that's a different problem; this is scoped to reliability under fault (timeouts, rate limits, bad data), not sequencing correctness.
- It does not replace a standing regression suite — run this once per tool-manifest change, not once ever.
