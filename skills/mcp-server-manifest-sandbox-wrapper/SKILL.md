---
name: mcp-server-manifest-sandbox-wrapper
description: Drafts a default-deny sandbox policy (filesystem/network/exec allowlist) for a third-party MCP server by reading its own declared tool manifest. Use before installing or granting host-process trust to any MCP server whose code you haven't audited.
---

# MCP Server Manifest → Sandbox Policy Draft

## When to use this

The moment right before you (or a teammate) install a third-party MCP server into Claude Code, Claude Desktop, or any other MCP host — the point where that server is about to run with the full filesystem/network/exec privileges of your host process, by default, regardless of what its tools claim to do. Also use it retroactively on any already-installed third-party server you've never reviewed, to see what it *could* be doing versus what it says it does.

This is a one-shot policy-drafting aid, not an enforcement process. It does not run, sandbox, or modify the target server — it only reads what the server declares and hands you a policy to apply with whatever sandboxing mechanism you already use (bubblewrap, seccomp, Landlock, a container's `--read-only`/network flags, or a host's own permission prompts).

## Inputs

**Data source**: Connected — reads the target MCP server's own declared tool list directly over the MCP protocol's standard `tools/list` call (every MCP server implements this; it is a mature, already-available interface, not a custom integration). Manual fallback: if the server isn't installed yet or can't be reached live, paste its tool manifest JSON (the array of tool objects with `name`, `description`, and `inputSchema`) directly — same output either way.

Optional extra input: the server's source repo URL (GitHub), used only to cross-check declared tools against what the code actually touches (hardcoded paths, domains, `exec`/`spawn` calls) — this step is a secondary flag, not required for the core policy draft.

## Procedure

1. **Get the manifest.** If the server is running/installed, call its `tools/list` method and capture the full JSON response. If not, take the pasted manifest JSON from the user. If neither is available, stop and say so — never invent a manifest.
2. **Classify each declared tool** by what it plausibly needs, using its `name`, `description`, and `inputSchema` parameter names together (never name alone):
   - Parameters/description mentioning a path, file, directory → filesystem capability. Note the narrowest plausible scope (a specific declared directory if named; otherwise flag as "scope unstated").
   - Parameters/description mentioning a URL, domain, endpoint, API → network capability. Extract literal domains if present in examples/defaults; otherwise flag as "domain unstated."
   - Parameters/description mentioning a command, shell, binary, script path → exec capability. List the literal binary/command if named.
   - Tools with none of the above (e.g. pure computation, in-memory transforms) → no privileged capability; explicitly mark "no fs/net/exec implied."
3. **Build the allowlist** as the union of the narrowest-plausible scope from step 2 across all tools — never widen beyond what at least one declared tool's description/schema actually implies.
4. **Flag mismatches**: any tool whose declared function (per its description) doesn't obviously justify the capability its schema implies — e.g., a tool named/described as "get current weather" taking a `path` parameter, or a "format text" tool taking a `command` parameter. These are the highest-value output of the whole exercise; call them out by tool name, not buried in the table.
5. **Optional source cross-check** (only if a repo URL was given): search the repo for path literals, `fetch`/`http` calls to domains, and `exec`/`spawn`/`child_process` calls. List anything found that touches a capability no declared tool's manifest entry accounts for, as "undeclared capability — found in source, not in manifest."
6. **Self-limit**: if more than ~30% of tools land in "scope/domain unstated," say so plainly in the summary rather than guessing a specific path or domain to fill the gap. An honest "insufficient evidence" is the correct output far more often than a confident wrong allowlist.

## Output format

A single markdown report with four parts, in this order:

1. **Summary line** — server name (or "unnamed — pasted manifest"), tool count, overall confidence (High/Medium/Low, driven by how much of step 6's "unstated" fraction there was).
2. **Policy table** — columns: `Capability type | Scope (path/domain/command) | Source tool(s) | Confidence`. One row per distinct capability, not per tool.
3. **Flags** — bullet list, one per mismatch or undeclared-capability finding from steps 4–5, each naming the specific tool and the specific concern.
4. **Raw policy block** — the same allowlist as a fenced JSON object (`{"fs": [...], "net": [...], "exec": [...]}`) so it can be pasted directly into a bubblewrap arg list, a seccomp profile, a container's allow-list config, or any other enforcement mechanism the user already has.

## Guardrails

- Never fabricate a path, domain, or command that isn't present in the manifest, its descriptions/schemas, or (when used) the cross-checked source — "unstated" is always a valid, preferred answer over a guess.
- Never treat this report as an enforced security boundary — it is a draft for a human (or a separate enforcement tool) to apply and review, not a running sandbox. Say this explicitly in the summary line if the user's phrasing suggests they think it's already protecting them.
- Never silently widen scope to "make the tool work" — if a declared tool plausibly needs broad filesystem or network access, say so and flag it for human judgment rather than narrowing it arbitrarily to look safer than it is.
- Never execute, run, or exercise the target server's actual tool calls as part of drafting the policy — the only live interaction with the server is the standard `tools/list` introspection call; everything else is static analysis of declared metadata (and optionally source text).
- If the manifest is empty, malformed, or the server declares zero tools, say so and stop — do not produce a policy from nothing.
