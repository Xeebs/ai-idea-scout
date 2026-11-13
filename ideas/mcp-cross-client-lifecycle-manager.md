# Shelf Life: A Maintained Cross-Client MCP Server Lifecycle Manager

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-13-tool-use-mcp-ecosystem.md · P3
- **Maturity verdict**: PARTIAL — GitHub search surfaces a genuinely crowded field already attacking this exact niche (CC-Switch/farion1231's cc-switch for Claude Code+Codex+OpenCode+Gemini CLI; heyitsjakub/KyttoMCP for Claude Desktop+Claude Code+Cursor+VS Code+Codex with health checks and tool-safety scanning; mcp-hub-tui), but every one checked via `gh api` is brand-new (created/pushed within days, 0 stars, 0 forks), with no evidence of adoption or maintenance. Real, actively-attempted gap; nothing has executed well yet.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads and writes each installed AI coding client's local MCP configuration file directly from disk: Claude Code's `~/.claude.json` / project-level `.mcp.json`, Codex's `~/.codex/config.toml`, Cursor's `mcp.json`, and Gemini CLI's/OpenCode's native config files. No API or MCP connector is required — these are plain, already-present local files in documented locations; direct filesystem read/write *is* the connector here, and it's mature today (every cited competing attempt already does this).

## The Gap
A Show HN ("One TUI to Manage MCP Servers for Claude Code and Codex," toolshed.run, 2026-11-09, 7 points) surfaced a developer hand-rolling a fix for a problem that's apparently common enough to motivate a post but has no entrenched incumbent solution: each AI coding client (Claude Code, Codex, Cursor, Gemini CLI, OpenCode...) keeps its own separate MCP server registration, so running more than one client means installing, enabling, and updating the same servers redundantly, per client, by hand. The gap-analyst's own search found this isn't a lone complaint — it's being independently re-attempted by at least three other brand-new, zero-star, zero-fork solo projects within the same window, none of which has shown any sign of sticking.

## The Project
A single manifest (TOML/YAML) declares which MCP servers should exist, with what args/env/auth, across every client the developer has installed. Per-client adapter plugins translate that manifest into each client's native config format and back, so the tool can both push the desired state and detect drift — a server quietly removed from one client's config, a stale auth token in another, a version mismatch. Every sync is a dry-run diff by default, never a blind overwrite, and a health-check runner actually starts each server after a sync to confirm it works rather than just confirming the config line exists. The differentiator versus the three existing solo attempts isn't the core idea (they all have it) — it's committing to adapter coverage as new clients ship, a real drift-detection test suite pinned to client config-format versions, and reversible syncs, which is exactly the maintenance discipline none of the existing attempts has demonstrated yet.

Components: manifest schema · per-client adapter plugins (Claude Code, Codex, Cursor, Gemini CLI, OpenCode) · drift detector · health-check runner · CLI/TUI front end.

## Tangible Impact
**Population**: developers who run two or more AI coding agent CLIs side by side (e.g., Claude Code + Codex, or + Cursor, or + Gemini CLI) rather than committing to one. No reliable public figure exists for exactly how many of the tens of millions of Claude Code/Copilot/Cursor users fall into this multi-client subset, but the evidence itself is the size signal: three independent, unendorsed, brand-new solo projects (CC-Switch, KyttoMCP, mcp-hub-tui) all attacked the identical problem within days of each other, plus the toolshed.run Show HN — a pattern of repeated, independent reinvention that only happens when a pain point is widely felt, not idiosyncratic to one person.

**Mechanism**: Today, adding or updating an MCP server means manually re-entering the same args/env/auth separately into each client's own config file/format. This tool collapses that N-clients × M-servers manual edit matrix into one manifest edit, propagated and verified everywhere, and it surfaces drift (a server broken in one client but fine in another) that today only gets discovered when that specific client happens to be used and fails.

**Measure**: (1) time to add one new MCP server across all of a developer's installed clients, before vs. after; (2) count of drift incidents caught per week during a trial (servers present-but-broken in a secondary client); (3) 30-day retention of installers — the exact signal all three existing competing attempts have so far failed to generate (0 stars/forks days after creation).

## Why Now
MCP server counts per developer keep climbing (this digest's own P1 evidence: 50+-tool catalogs are now common), and 2026 has normalized running multiple competing AI coding CLIs side by side rather than picking one — the condition that produced three independent from-scratch attempts at this exact tool within the same search window.

## Skill Angle
The skill version needs no installed daemon: point it at a developer's machine and it reads (via local file access) each installed client's config file/directory, builds a one-shot reconciliation report — which servers exist where, which are duplicated/stale/misconfigured — and outputs a diff plus a plain sync script the developer runs by hand. It's a lighter "tell me what's inconsistent right now" companion to the persistent lifecycle-manager project, useful even to someone who never installs the full CLI/TUI.

## MVP Sketch
A single CLI with adapters for just the two clients named in the seed Show HN — Claude Code and Codex — reading/writing their native config formats, dry-run diff output only, no background daemon (run manually on demand). Validation experiment: recruit ~10 developers who already run both clients, have them add 3 new MCP servers using the tool, and measure configuration time and drift incidents against their prior manual process.

## Risks & Open Questions
- Each client's config format/location is undocumented and version-specific and can change without notice — the real ongoing cost is adapter maintenance, not the initial build; this is the single biggest reason the existing attempts may have stalled rather than failed on merit.
- The official MCP Registry (covered under this digest's P8, SATURATED) already addresses server *discovery*, not local per-client lifecycle sync — complementary today, but a future official cross-client config standard could collapse this niche fast.
- None of the three existing competing attempts has any stars/forks days after creation — evidence of a felt itch, not yet evidence of durable willingness to adopt a tool for it.
- Health-checking "does this server actually start with valid auth" needs per-server knowledge beyond config plumbing, a scope-creep risk past the MVP.
