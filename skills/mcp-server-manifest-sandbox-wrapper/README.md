# MCP Server Manifest → Sandbox Policy Draft

A self-contained prompt template for drafting a default-deny sandbox policy for a third-party MCP (Model Context Protocol) server, based only on what that server itself declares it can do. Paste this whole document into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with the manifest described below — no prior context about this repo is needed.

## Why this exists

An installed MCP server runs with the full privileges of whatever host process launches it — full filesystem, network, and command-execution access — regardless of what its tools actually claim to do. Most people installing a third-party MCP server have no way to know, before running it, what a reasonable set of permissions for it would even look like. This skill reads the server's own self-description (its declared tool list) and derives the narrowest allowlist those declared tools plausibly require, plus flags anything that looks mismatched.

This is a **policy drafting aid**, not a running sandbox. It doesn't install, launch, or enforce anything — it hands you a policy to apply with whatever enforcement mechanism you use (bubblewrap, seccomp, Landlock, a container's network/filesystem flags, or a host application's own permission system).

## What to hand over

**Data source: Connected, with a manual fallback.** The preferred input is the server's own tool manifest, obtained by calling its standard MCP `tools/list` method (every MCP server implements this — it's part of the protocol, not a custom integration). If you can't run the server yet, or it's not installed, paste the manifest JSON directly instead — the array of tool definitions, each with `name`, `description`, and `inputSchema`. Either way, the output is identical.

Optional: the server's GitHub (or other source) repo URL, if you want a secondary cross-check of declared tools against what the actual code touches.

If you have none of the above — no live server, no pasted manifest, no repo — this skill cannot produce anything. Don't let it guess.

## What happens with your input (the procedure)

1. The tool manifest is read in full — nothing is sandboxed or executed, just the declared metadata.
2. Every tool is classified by what it plausibly needs: filesystem, network, exec, or none — based on its name, description, *and* its parameter schema together (never name alone, since names can be misleading).
3. For each inferred capability, the narrowest scope mentioned anywhere in the tool's description or schema is extracted (a specific directory, a specific domain, a specific command). If nothing specific is stated, that's recorded honestly as "unstated" rather than guessed.
4. The allowlist is the union of the narrowest-plausible scopes across all tools — it is never widened beyond what some declared tool actually implies it needs.
5. Any tool whose declared purpose doesn't obviously justify the capability its schema implies (e.g., a "get the weather" tool that also takes a filesystem path) gets called out by name as a flag — this is usually the single most useful thing the report produces.
6. If a repo URL was provided, the source is checked for capabilities (hardcoded paths, domain calls, exec/spawn calls) that show up in code but were never declared in the manifest — these get flagged separately as "undeclared capability."
7. If more than roughly a third of the tools end up "unstated," the report says so plainly instead of quietly filling in a confident-looking but made-up answer.

## Output you'll get

A single report with, in order:

1. **Summary** — server name, number of tools, and an overall confidence rating (High/Medium/Low).
2. **Policy table** — one row per distinct capability: type (filesystem/network/exec), scope, which tool(s) imply it, and confidence.
3. **Flags** — a plain list of any tool whose declared purpose doesn't match its implied permissions, or any capability found in source but not in the manifest.
4. **Raw policy block** — the same allowlist as a JSON object (`{"fs": [...], "net": [...], "exec": [...]}`), ready to paste into a bubblewrap arg list, a seccomp profile, or any sandboxing tool's config format.

## What this will never do

- Invent a path, domain, or command not actually present in the manifest, descriptions, schemas, or source. "Unstated — flagged, not guessed" is always the correct fallback.
- Present itself as an active security boundary. It is a draft for a human (or a separate enforcement tool) to review and apply — it does not itself block or allow anything.
- Widen a tool's apparent scope just to make the policy look cleaner. A tool that plausibly needs broad access gets flagged as needing broad access, not quietly narrowed.
- Actually run, call, or exercise the target server's tools beyond the one standard introspection call (`tools/list`) needed to read its declared manifest.
- Produce a policy from an empty or malformed manifest. If the server declares nothing usable, the correct output is "stop — I have nothing to work from," not a fabricated allowlist.
