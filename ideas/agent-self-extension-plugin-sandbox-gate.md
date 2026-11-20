# Plugin Cage: An Enforced Capability-Tiered Sandbox Gate for Agent Runtimes That Let Agents Add Their Own Tools at Runtime

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-20-tool-use-mcp-ecosystem.md · P6
- **Maturity verdict**: PARTIAL — a broad generic ecosystem exists for agent tool sandboxing/approval in general (an arXiv survey, 2605.24309, catalogs 5 academic papers, 15 production systems, and 4 plugins shipping some runtime-approval mechanism; Gravitee's deny-by-default + ephemeral sandboxes and Snyk's access-hook for tool-list gating are shipped vendor products; a Brown University EuroMLSys'26 paper proposes context-specific sandboxes for tool combinations) — but none is purpose-built for the specific pattern here: plugins/tools an agent runtime adds to itself mid-session without a host fork. That narrow slice is still caught, if at all, by a repurposed generic PR-review bot rather than an enforced policy layer.
- **Format**: BOTH
- **Data Sources**: CONNECTED — hooks into the host runtime's own plugin-registration interface (the mechanism these runtimes already expose for a plugin to register new panels, commands, and agent tools — e.g. the pattern evidenced in `pingdotgg/t3code`'s own plugin PR) to read a plugin's declared capability surface live, at the moment it tries to load; no manual upload needed for the always-on enforcement path.

## The Gap

A `pingdotgg/t3code` PR ("feat(plugins): plugins add panels, commands, styles and agent tools without a fork," 2026-11-09, 9 reactions/9 comments) was flagged by an automated reviewer bot (Macroscope) with the verdict "Needs Human Approval" — specifically because the PR "adds trusted, unsandboxed plugins spanning server execution, agent tools and browser UI." The gate that caught this was a generic PR-review bot repurposed for the job, not a purpose-built sandboxing/approval layer for dynamically-added agent tools — the review comment itself reads as an ad hoc catch rather than an enforced policy, and nothing else in this research pass showed a runtime-level gate built specifically for "an agent adds its own capability mid-session, no fork required."

## The Project

A policy-enforcement gate purpose-built for agent runtimes with a self-extension plugin mechanism. When a plugin attempts to register a new capability — a new agent tool, a new UI panel, a new slash command — without going through the host's own build/fork/code-review pipeline, the gate reads the plugin's declared capability surface from the runtime's own registration call and classifies it against a blast-radius policy (UI-only vs. filesystem-touching vs. network-reaching vs. server-execution-capable), then requires tiered approval scaled to that classification before the plugin is allowed to load into a live session. This generalizes the ad hoc PR-bot catch into a structural, host-agnostic runtime check: instead of hoping a human reviewer notices "this plugin adds unsandboxed server execution" buried in a PR description, the runtime itself won't start the plugin until its declared surface clears policy.

## Tangible Impact

**Population**: Developers and teams building or operating agent-runtime platforms with a self-extension plugin mechanism — the T3 Code team's own admitted gap is the concrete seed case, and any coding-agent or agent-IDE runtime that lets third-party or user-authored plugins register new agent tools, panels, or commands without a host fork shares the identical exposure. Downstream, the end users of those runtimes who install a community plugin today with no enforced guarantee it was vetted for the unsandboxed server-execution, filesystem, or browser-UI-injection surface it might actually touch.
**Mechanism**: Today the only thing standing between a dynamically-added plugin and full unsandboxed execution is whether a human reviewer — or, as literally happened in T3 Code's own PR, a generically-repurposed PR bot — happens to flag it. An enforced runtime gate converts that into a structural check: a plugin's declared capability surface is classified and gated the moment it tries to register, so "a reviewer might catch this" becomes "the runtime won't load it otherwise" — the same shift admission-control patterns made for infrastructure deploys, applied here to an agent's own mid-session self-extension.
**Measure**: % of a planted test-plugin corpus (plugins declaring benign-sounding names but requesting server-exec/filesystem/network reach) correctly blocked or escalated to approval, versus a zero-enforcement baseline; time-to-detection for an over-privileged plugin compared to relying on ad hoc human/bot PR review; false-positive rate on legitimately UI-only, no-exec/no-network plugins, to confirm the gate discriminates rather than blocking everything.

## Why Now

Agent-runtime plugin systems that let an agent add its own tools/panels/commands without forking the host are a newly emerging pattern — T3 Code's own plugin PR is dated 2026-11-09 — so the design space is still forming and a purpose-built gate can become the default expectation before thousands of unreviewed self-extension plugins ship the way narrow MCP servers already have.

## Skill Angle

A standalone "review this plugin's declared capability surface before shipping" skill: hand Claude a plugin's source/manifest (the new tools, panels, or commands it registers and what fs/network/exec reach each one implies), and it returns a structured classification — which declared capabilities land in which blast-radius tier, which ones look over-broad relative to the plugin's stated purpose, and what a reasonable tiered-approval requirement would be before merge. Usable by a plugin author or reviewer with no runtime integration at all; differs from the project by being a one-time pre-merge review rather than an always-on, registration-time enforcement gate.

## MVP Sketch

3-4 weeks, 1-2 people: build a minimal plugin-registration hook for one real self-extension runtime (or a faithful reproduction of T3 Code's plugin API pattern), a capability classifier that reads a plugin's declared tool/panel/command surface and buckets it into UI-only / fs-touching / network-reaching / server-exec tiers, and an approval-gate stub that blocks load until a tier-appropriate sign-off is given. Experiment: reproduce T3 Code's own flagged plugin PR as a test case plus 5 planted benign-and-malicious variants, and show the gate correctly tiers and blocks the over-privileged ones while passing the UI-only ones without manual review.

## Risks & Open Questions

- The host runtime itself (T3 Code or any other) could ship its own purpose-built gate once this exact PR comment made the gap visible — a well-resourced maintainer team closing its own named gap is a real risk.
- Auto-classifying a plugin's true blast radius from its declared capability surface alone is inherently heuristic; a plugin that under-declares (claims UI-only but calls an exec primitive indirectly) could slip through without deeper static or runtime analysis.
- The broader generic sandboxing/approval ecosystem (Gravitee, Snyk, the arXiv survey's 15 production systems) could extend into this narrow slice first, since the underlying admission-control and sandboxing primitives aren't new — the differentiator here is being purpose-built for runtime self-extension specifically, which is a thin wedge if a generic vendor decides to cover it.
- Evidence for this pattern is currently a single PR and its review comment — real, but thin; broader adoption of agent self-extension plugin systems needs to materialize for the addressable population to grow past "a handful of early runtimes."
