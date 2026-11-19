# Gatekeep: MCP Server Pre-Publish Quality Review

A copy-paste prompt template for reviewing a Model Context Protocol (MCP) server's tool design **before you publish it** — to the official MCP registry, an `awesome-mcp-servers`-style list, Show HN, or anywhere else. It catches the class of mistake that ships fine technically but confuses or misleads the AI agent calling your tools: vague descriptions, ambiguous units, unbounded lists, permission scope creep, and destructive actions with no safety rail.

This is a **one-time design review**, not a runtime/protocol conformance test. It does not replace tools like `mcp-assert` or `mcp-conform` (which test actual wire-protocol behavior) — use this first, for design quality, then run a conformance tool before shipping if you want deeper coverage.

## When to use this

Paste this prompt into Claude, ChatGPT, or any capable chat tool when:
- You just finished building an MCP server and want a second opinion before publishing.
- You're about to submit to the official MCP registry or a community list and want to catch obvious mistakes first.
- You inherited or are reviewing someone else's MCP server (e.g. a PR) and want a structured design checklist instead of an ad-hoc read-through.

## What to give it

Provide **one** of the following:
- A public GitHub repo URL for the server (works in tools with web/repo access — e.g. Claude with GitHub access, or a tool that can fetch URLs).
- The tool manifest/schema itself — paste the actual tool definitions (names, descriptions, input/output JSON schemas) directly into the chat. This works in any tool, even with zero connectors.
- Optionally, alongside either of the above: what permissions/scopes the server requests (OAuth scopes, API access level) if that's declared separately from the tool schema — without this, the reviewer will skip the permission-scope-creep check and say so.

If you only have a manifest and no permission info, that's fine — say so, and the review will note that one check category was skipped rather than guessing.

## The prompt

```
You are reviewing an MCP (Model Context Protocol) server's tool design before it gets published.
This is a one-time pre-publish design review, not a runtime/protocol conformance test — only
evaluate what's visible in the manifest/schema/source I give you. Do not test actual network/transport
behavior, do not fuzz, and do not claim to have found security vulnerabilities beyond what the
schema/docs literally show.

Here is the server to review: <PASTE REPO URL, OR PASTE THE TOOL MANIFEST/SCHEMA DIRECTLY>
[Optional: Here are the permissions/scopes it requests: <PASTE IF KNOWN>]

Do this:
1. List every tool you found by name. If you can't find any tools in what I gave you, say so and stop
   instead of inventing any.
2. For each tool, check it against this list (mark PASS / WARN / FAIL per item, and skip any item that
   doesn't logically apply to that tool — e.g. don't penalize a read-only tool for missing a destructive-
   action safeguard):
   - Naming: verb-noun, unambiguous, no version numbers baked into the name. FAIL if two tools are
     distinguishable only by a number/suffix.
   - Description clarity: explains when to call it and what it returns, not just a restatement of the
     name. WARN if under ~8 words or purely restates the name; FAIL if missing.
   - Input schema typing: every parameter has a concrete type, required vs optional is marked,
     constrained values use enums rather than free text. FAIL on missing required-field markers; WARN
     on missing enums where free text invites typos.
   - Units/ambiguous values: any parameter where the unit could be ambiguous (time, distance, currency)
     must state the unit. FAIL if genuinely ambiguous with no default shown; otherwise PASS.
   - Pagination: any tool that can return an unbounded list must expose a limit/cursor/page parameter.
     FAIL if unbounded with no documented cap; WARN if capped but undocumented.
   - Error-handling guidance: does the description/docs tell the calling agent what happens on failure
     and whether retry is safe? WARN if absent (escalate to FAIL only if paired with a destructive action).
   - Destructive-action safeguards: any tool that deletes/sends/pays/irreversibly mutates state must
     require an explicit confirmation parameter or clearly document irreversibility. FAIL if neither.
3. If I gave you permission/scope info: compare what the server requests against what its tools
   actually use. FAIL if it requests write/delete/full access but every tool only reads; WARN if the
   mismatch is partial or unclear. If I didn't give you this info, skip this check and say so explicitly
   — don't guess.
4. Flag any tools that look redundant/overlapping (near-identical purpose) as a WARN design smell,
   suggesting a merge or parameterization instead.
5. Roll everything into one overall verdict:
   - FAIL if any FAIL finding exists anywhere.
   - WARN if there are no FAILs but 3+ WARNs, or any single destructive-action/permission-scope WARN.
   - PASS if there are no FAILs and at most 2 minor WARNs.

Output format — a single report:

# MCP Pre-Publish Review — <server name>
Scope checked: <repo URL or "pasted manifest"> · <N> tools examined
Overall verdict: PASS | WARN | FAIL

## Findings
A table: Tool | Category | Severity | Issue | Suggested fix — one row per finding.

## Summary
Counts of FAIL / WARN / clean tools.

## Not covered by this review
A one-line reminder that this is a design/schema review only — recommend running a protocol-conformance
tool (e.g. mcp-assert, mcp-conform) and a dedicated security review before publishing if the server
touches sensitive data.

Rules: never issue a verdict for files/tools you weren't actually shown; never invent a security
vulnerability not directly evidenced in what I gave you; never apply a checklist item where it doesn't
logically apply; never claim this replaces protocol-conformance or security testing.
```

## What you get back

A single markdown report with: every tool checked against the seven-item design checklist, a severity (PASS/WARN/FAIL) and a specific suggested fix for each finding, an overall gate verdict, and an explicit reminder of what this review does *not* cover (protocol conformance, deep security testing). If you only gave it a manifest with no permission/scope info, the report will say the permission-scope-creep check was skipped rather than silently omitting it.

## Guardrails (built into the prompt)

- It will not grade tools it wasn't shown — if a repo fetch is partial, it reports exactly what it did and didn't review.
- It will not invent security vulnerabilities — this is a design review, not a penetration test.
- It will not apply irrelevant checklist items to a tool (e.g. won't dock a read-only tool for missing a destructive-action safeguard).
- It will always flag that this isn't a substitute for a protocol-conformance tool like `mcp-assert` or `mcp-conform` — run one of those too before you actually publish.
