# Gatekeep: A Pre-Publish Quality & Design-Review Gate for Narrow MCP Servers

- **Status**: EXPLORING
- **Date**: 2026-11-19
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-19-tool-use-mcp-ecosystem.md · P6
- **Maturity verdict**: PARTIAL — real linters/scorers exist (`blackwell-systems/mcp-assert`, 27★, found 4,794 schema issues across 55 real servers; `mcp-conform`; Glama's per-server ratings) but none is referenced or required by the narrow Show-HN servers surveyed, the official registry only checks namespace/metadata not safety, and `awesome-mcp-servers` tells users to vet servers themselves. Tooling exists; enforcement doesn't.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the submitted MCP server's own repository via the GitHub API (mature, existing) to pull its tool manifest/schema and run the linting checks (wrapping `mcp-assert`/`mcp-conform`-style rules) against it; also reads the official MCP registry's submission metadata (the registry and its submission flow already exist today) to attach a pass/warn/fail badge at listing time. No user-pasted input required for the project's automated path.

## The Gap

Three independent Show HN launches in one month — WhatsApp MCP (3pts/6cmt), Atli eSIM MCP (6pts/1cmt), Meteosource weather MCP (3pts/1cmt) — each ship a single-API wrapper server with no shared scaffold or review checklist, while Metabase's own engineering blog describes having to *redo* their first MCP server because they got the tool design wrong the first time. Real linting/scoring tools now exist (`mcp-assert`, `mcp-conform`, Glama ratings) but nothing wires them into the point where a new server actually gets published, so each author keeps rediscovering the same mistakes Metabase already documented.

## The Project

A pre-publish gate that any MCP server author (or the official registry itself, as an opt-in badge) can run against a candidate server before it goes live: it pulls the server's tool manifest and source via the GitHub API, runs it through the existing schema/conformance linters (`mcp-assert`-style checks, `mcp-conform`'s spec rules) plus a design-mistake checklist distilled from documented retrospectives like Metabase's, and returns a pass/warn/fail with specific line-level fixes — not a new linter engine, but the missing enforcement point that turns "tooling exists" into "tooling runs on every submission." A lightweight hosted badge/API lets a registry or `awesome-mcp-servers`-style list display the result next to each listing.

## Tangible Impact

**Population**: solo/small-team MCP server authors publishing single-purpose wrapper servers (the three Show HN launches are representative of a much larger steady stream given 20,000–30,000 listed servers by Sept 2026), and — on the consumer side — developers deciding which of those servers to install into their own agent stack.
**Mechanism**: Today an author ships whatever passes their own manual testing, and a known class of schema/description mistakes (the kind `mcp-assert` found 4,794 instances of across just 55 servers) ships to users who have no visible signal to distinguish a carefully-designed server from a weekend hack. A pre-publish gate catches the mistakes before they reach a user, and a visible badge gives installers a quality signal the registry itself doesn't provide.
**Measure**: % of submitted servers failing the gate on first run (expected high, proving the gap is real); reduction in post-publish "redesign" incidents like Metabase's when authors run the gate before shipping; adoption — number of real community servers voluntarily running the badge within 3 months of launch.

## Why Now

The pattern tools (`mcp-assert`, `mcp-conform`) only shipped in the last 30 days and nothing has yet wired them to an enforcement point; the registry itself is new enough (post-Sept-2026 scale) that a submission-time gate could still become a default norm before thousands more narrow servers ship without one.

## Skill Angle

A standalone "review my MCP server before I publish it" skill: hand Claude a server's tool manifest/schema (or a repo URL), and it runs the same design-mistake checklist one-shot — ambiguous tool descriptions, over-broad declared permissions vs. actual function, missing error-handling guidance, pagination/unit inconsistencies — and returns a structured review with fixes. This is usable by an author who never touches the hosted gate or registry badge, and differs from the project by being a one-time pre-publish review rather than an always-on registry-integrated service.

## MVP Sketch

2–3 weeks, 1–2 people: a CLI that clones a target repo via the GitHub API, runs `mcp-assert`/`mcp-conform` (or reimplements their core checks if licensing blocks reuse) plus a curated checklist, and emits a markdown report + pass/warn/fail badge. Experiment: run it against the three Show HN servers named in this digest plus 10 more pulled from `awesome-mcp-servers`, and count how many fail — validating that the enforcement gap, not the detection gap, is what's missing.

## Risks & Open Questions

- If the official registry adds its own quality gate, this is absorbed overnight — a real risk given the registry is actively evolving.
- Linter false positives on legitimately unusual but correct designs could create authority-fatigue if the gate is ever made mandatory rather than advisory.
- No enforcement mechanism exists today to make any registry *require* the badge — adoption depends entirely on voluntary author buy-in or a registry partnership.
- The "design-mistake checklist" beyond Metabase's single retrospective is thin; needs more documented case studies to stay evidence-based rather than opinion-based.
