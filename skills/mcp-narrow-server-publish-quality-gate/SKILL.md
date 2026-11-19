---
name: mcp-narrow-server-publish-quality-gate
description: Pre-publish design-quality review for a Model Context Protocol (MCP) server — audits tool manifest/schema for ambiguous descriptions, permission scope creep, pagination/unit inconsistencies, and missing error-handling guidance, returning a pass/warn/fail verdict with line-level fixes. Use before submitting a new MCP server to the official registry, an awesome-mcp-servers-style list, or any Show-HN-style launch.
---

# Gatekeep: MCP Server Pre-Publish Quality Review

## When to use this
Reach for this skill the moment someone says a variant of: "I built an MCP server, can you review it before I publish/submit it?", "is my MCP server ready to ship?", "review my tool manifest before I put this on the registry/Show HN", or pastes an MCP server's tool definitions and asks if anything looks wrong. This is a **one-time pre-publish review**, not an always-on CI gate and not a protocol wire-conformance test — it checks tool *design* quality, the class of mistake that ships fine technically but confuses or misleads the calling agent.

Do not use this for: runtime/transport testing (stdio/SSE/HTTP behavior), fuzzing, or deep security penetration testing — recommend the user also run a dedicated conformance/security tool (e.g. `mcp-assert`, `mcp-conform`) for those; this skill only reviews what's visible in the manifest, schema, and surrounding docs/source it was actually given.

## Inputs
**Data source**: Connected — when given a repo URL, reads the target MCP server's repository via the GitHub API (a mature, existing connector) to pull its tool manifest/schema, server entry file, and any README/permission declarations. Manual fallback also supported: the user may instead paste the tool manifest/schema JSON (or point to local files) directly, which is the only path available outside Claude Code or when the repo isn't public/accessible.

Required, one of:
- A public GitHub repo URL for the server, OR
- The tool manifest/schema itself (the JSON/TS/Python tool definitions — names, descriptions, input/output schemas), pasted or in local files, OR
- Both a manifest and the declared permission/connection scope (OAuth scopes, API keys requested, filesystem/network access) if that's described separately from the tool schema (e.g. in a README or config file).

If only a manifest is given with no permission/scope info, proceed but flag that permission-scope-creep checks (see Procedure step 3) can't be run and say so explicitly in the output — never guess at declared scopes that weren't shown.

## Procedure
1. **Locate and extract the tool manifest.** If given a repo URL, fetch the server's entry point and tool-registration code (commonly `tools/`, `src/tools.ts`, `server.py`, or wherever `list_tools`/`@tool` decorators live) plus `README.md` and any config/manifest file declaring required scopes or permissions. If given pasted text, parse it directly. List every tool found by name before proceeding — if fewer than 1 tool is found, stop and report that extraction failed rather than inventing tools.

2. **For each tool, check design quality against this checklist** (each item below is PASS, WARN, or FAIL per tool — never apply a checklist item to a tool that doesn't have the relevant feature, e.g. don't dock a read-only tool for "missing pagination" if it never returns a list):
   - **Naming**: verb-noun, unambiguous (e.g. `send_message` not `msg` or `do_action`), no version numbers baked into the name. FAIL if two tools have near-identical names distinguishable only by number/suffix.
   - **Description clarity**: description explains *when an agent should call this* and *what it returns*, not just a restatement of the name. WARN if under ~8 words or purely restates the tool name; FAIL if missing entirely.
   - **Input schema typing**: every parameter has a concrete type (no bare untyped `object`/`any` catch-alls for structured data), required vs. optional is marked, and constrained-value parameters (status, category, etc.) use `enum` rather than free-text. FAIL on missing required-field markers; WARN on missing enums where free text invites typos.
   - **Units and ambiguous values**: any numeric parameter with a possible unit ambiguity (time: seconds vs ms, distance: km vs mi, currency) must state the unit in the description or field name. FAIL if genuinely ambiguous (e.g. `timeout` with no unit and no default shown); PASS if the unit is explicit.
   - **Pagination**: any tool that can return an unbounded list (messages, contacts, search results, logs) must expose a limit/cursor/page parameter. FAIL if a list-returning tool has no bound and no documented cap; WARN if a cap exists but isn't mentioned in the description.
   - **Error-handling guidance**: description or docs tell the calling agent what happens on failure (specific error codes/messages, whether retry is safe). WARN if absent; this is rarely a FAIL on its own unless paired with a destructive action (see next item).
   - **Destructive-action safeguards**: any tool that deletes, sends, pays, or irreversibly mutates state must require an explicit confirmation parameter or clearly document the irreversibility in its description. FAIL if a destructive tool has neither.

3. **Check permission/connection scope creep** (only if scope info was provided per Inputs): compare what the server *requests* (OAuth scopes, declared API permissions) against what its tools *actually use*. FAIL if the server requests write/delete/full-account access while every tool only reads data; WARN if the mismatch is partial or unclear from the docs.

4. **Check for redundant/overlapping tools**: two or more tools that do near-identical things (e.g. `get_messages` and `fetch_messages` with the same params) should be flagged WARN as a design smell — suggest merging or parameterizing instead of listing both.

5. **Tally severities into one overall gate verdict**:
   - **FAIL** — one or more FAIL findings anywhere.
   - **WARN** — zero FAILs but three or more WARNs, or any single destructive-action/permission-scope WARN.
   - **PASS** — zero FAILs, at most two minor WARNs.

6. **Write the review** in the Output format below. Never silently drop a finding to make the result look cleaner, and never add a finding for something not actually observed in the given manifest/source.

## Output format
A single markdown report:

```
# MCP Pre-Publish Review — <server name>
Scope checked: <repo URL or "pasted manifest"> · <N> tools examined
Overall verdict: PASS | WARN | FAIL

## Findings
| Tool | Category | Severity | Issue | Suggested fix |
|------|----------|----------|-------|----------------|
| delete_message | Destructive-action safeguard | FAIL | No confirmation param; irreversible delete | Add a `confirm: boolean` required param, or require re-passing the message ID with an `are_you_sure` flag |
| ... | ... | ... | ... | ... |

## Summary
<N> FAIL, <N> WARN, <N> PASS-clean tools.

## Not covered by this review
This is a design/schema review only. Before publishing, also run a protocol-conformance/fuzz tool (e.g. mcp-assert, mcp-conform) and, if the server touches sensitive data, a dedicated security review — this skill does not test runtime behavior or hunt for vulnerabilities beyond what's visible in the schema.
```

If extraction failed (step 1) or permission-scope info was unavailable (step 3), say so plainly near the top of the report instead of producing a verdict table with gaps silently papered over.

## Guardrails
- Never issue an overall PASS/WARN/FAIL verdict for tools or files you weren't actually given access to — if a repo fetch fails partway, report exactly which files were reviewed and which weren't.
- Never invent a security vulnerability, CVE, or exploit scenario not directly evidenced in the provided manifest/source — this is a design review, not a penetration test, and fabricated security claims are worse than no claim.
- Never apply a checklist item to a tool it doesn't logically apply to (e.g. don't FAIL a read-only `get_status` tool for "missing destructive-action safeguard").
- Never claim this review is equivalent to or a substitute for `mcp-assert`/`mcp-conform`-style protocol conformance testing — always surface that distinction in the output.
- Never inflate WARN findings to FAIL (or the reverse) to make the review look more or less thorough than it is — severities must follow the rubric in step 5 exactly.
