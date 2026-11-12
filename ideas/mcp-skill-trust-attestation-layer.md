# Provenance Gate: A Unified Trust Layer for MCP Servers and Agent Skills

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-11-tool-use-mcp-ecosystem.md · P2
- **Maturity verdict**: PARTIAL — `stacklok/toolhive` (2,339★, updated within the last day) is a real maintained trust layer for MCP server image verification, but it doesn't cover agent skills together with MCP servers. Cloud Security Alliance (Sept 2026) still frames combined MCP/skill trust as unsolved; only early/vendor-stage competitors exist (Credence, askalf/truecopy, mcpskills server at 0★). One serious implementation exists but the broader "vet skills + MCP servers together" scope remains open.
- **Format**: BOTH

## The Gap

HN's "USB: A trust layer for AI skills and MCP servers" (2026-11-09, 11 points, 3 comments, github.com/PeepSick/usbplus) treats this as a fresh proposal, not a pointer to an existing standard — and it's one of several thin attempts. Meanwhile `toolhive` proves the MCP-server half is buildable and adoptable, but nothing unifies it with skill vetting, and the Cloud Security Alliance still calls the combined problem open.

## The Project

A policy-enforcement gateway sitting in front of an agent's tool-loading step for both MCP server connections and skill installs. Before anything runs, it checks the artifact against layered policy: known-publisher allowlist, static manifest scan (declared permissions vs. declared function, network egress), signature/provenance check where available, and a community trust score. It defaults to warn, only promotes to enabled for vetted sources, and logs every decision to an auditable ledger a security team can review later.

## Tangible Impact

**Population**: Platform/security teams at organizations running Claude Code or other agent hosts with third-party MCP integrations who must approve what gets installed — a population that scales with the registry itself (20,000–30,000 listed MCP servers by Sept 2026, plus a growing skills ecosystem) and includes every org with a security review gate around agent tooling.
**Mechanism**: Replaces ad hoc or absent manual review with an automatic layered check at install time, turning "no one looked at this" or "someone eyeballed the README" into a documented allow/warn/block decision with reasoning — shrinking both approval latency and the chance an unreviewed server or skill slips through unexamined.
**Measure**: Median time from "developer requests a new server/skill" to "security-approved"; % of installs with a documented trust decision vs. none before adoption; detection rate of planted high-risk installs in a red-team test set (false-negative tracking).

## Why Now

The official registry now exists but only lists, it doesn't vet; `usbplus` (Nov 9) and the CSA's framing both show the community actively trying and failing to converge on a default layer, while `toolhive` proves the MCP-server half is technically feasible — nothing has unified it with skills yet.

## Skill Angle

A "vet this before I install it" skill: given a URL, repo, or manifest for an MCP server or skill, Claude performs a one-shot structured trust review — permissions requested vs. advertised function, declared network calls, signer/provenance, red flags against known attack patterns — and returns a pass/warn/fail verdict with reasoning. This is usable standalone without running the full gateway, and differs from the project by being a point-in-time review rather than an always-on enforcement service.

## MVP Sketch

2–4 weeks, 1–2 people: a CLI wrapping toolhive's verification primitives plus a new skill-manifest checker, driven by a YAML policy file defining allow/warn/block rules. Experiment: run it against 20 real community MCP servers/skills with known-good and planted known-bad examples, measure detection rate.

## Risks & Open Questions

- toolhive or the official registry could absorb this scope themselves given momentum, eroding differentiation quickly.
- Cryptographic provenance/signing isn't standardized across MCP yet, so verification may stay heuristic rather than cryptographically guaranteed.
- Overly strict defaults risk approval fatigue (warn-everything is as useless as vet-nothing).
- The policy layer is only as good as its allowlist/threat feed, which needs ongoing maintenance to stay current.
