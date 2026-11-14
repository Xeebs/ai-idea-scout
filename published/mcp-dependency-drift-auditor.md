# Driftwatch: Continuous Supply-Chain Drift Monitoring for MCP Server Dependencies

You install an MCP server once, review what it asks for, click approve — and then trust it forever. Nothing re-checks that server next week, next month, or the week after someone quietly swaps a dependency, widens a tool's declared permissions, or slips a new container layer past the point where anyone was still looking. That one-time-approval model is the default for essentially every MCP integration running today, and in the last month alone, five separate teams independently built some version of a fix for it — with zero consolidated winner among them.

## The Gap

The clearest signal is a single pull request: `Bharath-code/sentris` PR #19, opened 2026-11-05, pitching "a 2026 AI/MCP supply-chain firewall, Docker Ghost Layer scanner, Vault Coverage drift auditor & Agent CLI." It landed quietly — two reactions, one comment — the kind of PR that's easy to scroll past. But a broader search turned up the real story: four more independent, near-identical attempts at the same problem, spun up in the same roughly 30-day window — `onicarps/mcpcheck`, `ookini-kawaii/mcp-security-scanner`, `9zj5yyz6v2-blip/skillscan`, and `Rinkia/bastionsupply`. Every one of them was created mid-to-late 2026. Every one of them sits at zero stargazers.

That pattern — five teams, one gap, no shared solution, no traction for any of them — is rarely a coincidence. It usually means the problem is real and newly felt, but nobody has yet built the version that sticks. A separate research pass a few days later found the same underlying mechanism described from the security-research side rather than the builder side: write-ups on "MCP approval fatigue" and "MCP confused deputy" problems, and an argument from christian-schneider.net that MCP needs a defense-first, per-client consent architecture instead of its current one-time-approval default. One study cited in that pass found that MCP clients forced re-approval in zero of eight tested rug-pull techniques. Zero of eight. The rug-pull isn't a hypothetical attack scenario — it's a documented, repeatable gap in how the ecosystem currently works, and the registry's own scale (20,000–30,000 listed MCP servers as of September 2026) means it's not a one-server problem for any team running more than a handful.

What exists today — on both research passes — are narrow individual attempts: tool-poisoning and rug-pull detectors, SARIF output, hash-pinning gists, consent-audit repos. Real techniques, genuinely applicable pieces. None of them has adoption, a maintenance history, or community validation behind it yet.

## The Project

Driftwatch is a continuously-running drift auditor for MCP server fleets. At install time, it snapshots everything about an MCP server that a security team actually cares about — its dependency tree, its container layers, its declared tool schemas — and hash-pins that snapshot as the trusted baseline. From then on, it re-scans on a schedule, diffing the live server against that baseline to catch exactly the failure mode nobody currently guards against: a dependency silently swapped for a malicious one, a tool schema quietly widened to request new permissions it didn't have at approval time, a container layer injected after the fact.

When drift is detected, the server doesn't just get flagged in a dashboard somewhere — it gets blocked from running with live credentials until a human re-approves it. Findings emit in SARIF format specifically so they plug into security tooling teams already run, rather than asking anyone to adopt yet another dashboard. The core idea is simple and not currently automated anywhere with any traction: "approved once" should mean "approved as of this exact baseline," not "approved indefinitely regardless of what changes underneath it."

## Tangible Impact

**Population**: Platform/security engineering teams running fleets of MCP-integrated agent hosts or CI runners — specifically orgs installing MCP servers once and trusting them indefinitely, a pattern the registry's own scale (20,000–30,000 listed servers by Sept 2026) makes common once a team runs more than a handful.
**Mechanism**: Without continuous drift detection, a compromised or rug-pulled dependency change goes unnoticed until it's exploited with live credentials. Scheduled re-scanning against a pinned baseline catches the change at the next scan interval and blocks execution before it runs again — shrinking the exposure window from indefinite to one scan cycle.
**Measure**: Median time-to-detection of a planted malicious dependency swap in a test fleet; drift events caught vs. missed against a red-team corpus; false-positive rate on legitimate version bumps.

## Try It

No companion skill exists for this idea yet — it's scoped as PROJECT only, not something a single prompt-driven Claude Code skill can meaningfully reproduce, since the value here is a persistent, scheduled scanning service with a live baseline store, not a one-shot analysis.

## The Honest Caveats

This is a crowded, fast-moving niche — five attempts in thirty days means a funded entrant, or the official MCP Registry itself, could absorb this before an indie build gets any traction. There's also no mature MCP-specific vulnerability feed to build on yet, so an early version is stuck leaning on imperfect general feeds like OSV and npm audit. And by design, drift detection is reactive — it catches a change after it's already happened, not before — with the added catch that it only works if an org adopts the discipline of pinning and snapshotting at install time in the first place, which is itself a behavior change nobody's being forced into today.

None of that makes the gap less real. It makes the build window narrower.

---

Surfaced from `research/2026-11-11-tool-use-mcp-ecosystem.md`, pattern `P3`.
