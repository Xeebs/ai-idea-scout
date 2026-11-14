# Driftwatch: Continuous Supply-Chain Drift Monitoring for MCP Server Dependencies

- **Status**: PUBLISHED (promoted 2026-11-13 cycle 66: recurrence; published cycle 66, see [writeup](../published/mcp-dependency-drift-auditor.md))
- **Date**: 2026-11-11
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-11-tool-use-mcp-ecosystem.md · P3
- **Maturity verdict**: PARTIAL — GitHub search found four dedicated attempts beyond the digest's `Bharath-code/sentris` PR (`onicarps/mcpcheck`, `ookini-kawaii/mcp-security-scanner`, `9zj5yyz6v2-blip/skillscan`, `Rinkia/bastionsupply`), all created mid-to-late 2026, all at 0 stargazers. Real implementations exist (tool-poisoning/rug-pull detection, SARIF output, hash pinning) but none has adoption, maintenance history, or community validation.
- **Format**: PROJECT

## The Gap

`Bharath-code/sentris` PR #19 (2026-11-05, 2 reactions, 1 comment) proposes "a 2026 AI/MCP supply-chain firewall, Docker Ghost Layer scanner, Vault Coverage drift auditor & Agent CLI" — one contributor's PR to a niche repo. The verdict search found four *more* independent, near-identical attempts spun up in the same window, all at zero traction: five teams converging on the same unsolved niche in roughly a month is strong demand signal with no maintained winner yet.

## The Project

A continuously-running drift auditor: at install time it snapshots every MCP server an org runs (dependency tree, container layers, declared tool schemas), hash-pins that baseline, then re-scans on a schedule to catch "rug pull" drift — a dependency silently swapped for a malicious one, a tool schema quietly widened to request new permissions, an injected container layer post-approval. Findings emit in SARIF format for existing CI/security dashboards, and any detected drift blocks the server from running with live credentials until re-approved.

## Tangible Impact

**Population**: Platform/security engineering teams running fleets of MCP-integrated agent hosts or CI runners — specifically orgs installing MCP servers once and trusting them indefinitely, a pattern the registry's own scale (20,000–30,000 listed servers by Sept 2026) makes common once a team runs more than a handful.
**Mechanism**: Without continuous drift detection, a compromised or rug-pulled dependency change goes unnoticed until it's exploited with live credentials. Scheduled re-scanning against a pinned baseline catches the change at the next scan interval and blocks execution before it runs again — shrinking the exposure window from indefinite to one scan cycle.
**Measure**: Median time-to-detection of a planted malicious dependency swap in a test fleet; drift events caught vs. missed against a red-team corpus; false-positive rate on legitimate version bumps.

## Why Now

Five independent teams built some version of this in the last 30 days alone — real, urgent demand with no consolidated winner yet, and an early-mover window before the official registry or a funded vendor bundles equivalent coverage in.

## MVP Sketch

2–4 weeks, 1–2 people: a scanner CLI plus a lightweight scheduled job storing a hash/schema baseline per installed server in SQLite, diffing against re-fetched manifests/dependency trees nightly, emitting SARIF. Experiment: stand up 10 real MCP servers, plant 3 "rug pull" mutations over a week, measure catch rate and time-to-flag.

## Risks & Open Questions

- Crowded, fast-moving niche (5 attempts in 30 days) — high chance a funded entrant or the official registry absorbs this before an indie project gains traction.
- No mature MCP-specific vulnerability feed exists yet; likely has to build on top of imperfect general feeds (OSV, npm audit).
- Drift detection is inherently reactive (catches change after it happens), not preventive.
- Requires orgs to already pin/snapshot at install time — itself a behavior change needed to drive adoption.
