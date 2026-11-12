# Carryover: A Portable Context Handoff Protocol for Cross-Tool Agent Work

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-11-context-engineering-and-memory.md · P2
- **Maturity verdict**: PARTIAL — 10+ small "portable-agent-memory" repos and several named point-solutions (Carryover, Continuity, BuildBetter CLI, Byterover, EverMemOS, Relay, Unabyss, ContextStream) exist, but none has independent adoption or benchmark validation, and the sourcing HN "Ask HN" thread (98 points, 60 comments — the highest-engagement cluster in the digest) got no canonical-answer reply. Real gap, no dominant winner.
- **Format**: BOTH — the sync/storage layer is PROJECT-shaped; drafting a portable context manifest for a specific multi-tool workflow is a one-shot judgment task.

## The Gap
Hacker News's "Ask HN: How do you manage your AI agents' context across clients and projects?" (2026-11-07) drew the single highest engagement of the whole research run with no settled answer — people who bounce between Claude Code, Cursor, and ChatGPT on the same project keep re-establishing architecture, conventions, and decision history from scratch in each tool. The gap-analyst found a crowded field of early, unvalidated attempts (several alpha-stage crates and CLIs) but no tool with independent adoption evidence.

## The Project
A single, versioned "context bundle" file (project architecture, recent decisions, open threads, file-level state) that lives in the repo or a user-level store, plus thin adapters that translate it into each tool's native context mechanism (Claude Code's CLAUDE.md/memory, Cursor rules, a ChatGPT custom-GPT system prompt). The adapters are the centerpiece, not the file format: the same bundle renders correctly whether the next session opens in Cursor or Claude Code, and a CLI (`carryover sync`) keeps the bundle current by diffing it against recent commits and session summaries rather than requiring manual re-entry.

Components: bundle schema (YAML/JSON, versioned); CLI for sync/diff/render; adapters for Claude Code, Cursor, and a generic system-prompt export; a "staleness" check that flags when the bundle hasn't been updated since N commits.

## Tangible Impact
**Population**: Developers — solo and small-team — who routinely work across 2+ AI coding tools on the same project within a week, the explicit audience of the 60-comment HN thread; a conservative proxy is the overlap of Cursor's and Claude Code's user bases, both independently reported in the hundreds-of-thousands in 2026 vendor disclosures.
**Mechanism**: Today, switching tools means re-typing or re-discovering project context, or working from a stale memory file only one tool reads; a synced, multi-tool bundle means the next tool a developer opens already knows what the last one decided, cutting the "re-orientation tax" every switch currently pays.
**Measure**: (1) Time from opening a new tool on an existing project to first useful agent action drops measurably in a pilot (self-reported before/after logs). (2) Rate of agents proposing something already decided/rejected in another tool's session drops. (3) Bundle staleness (commits since last sync) stays below a target threshold without manual nagging.

## Why Now
The HN thread's 98-point, 60-comment engagement is the clearest "no standard exists" signal in the digest, and the proliferation of alpha-stage point solutions in the last 30 days shows the community is actively duct-taping this — no one has shipped the cross-tool adapter layer that makes a single bundle actually render natively in each tool.

## Skill Angle
Given a description of a developer's current tools and the context they keep re-explaining (in their own words, or pasted from an existing CLAUDE.md/Cursor rules file), draft a portable context bundle: architecture summary, recent decisions with rationale, open threads, and tool-specific rendering notes. This is useful immediately, independent of whether the sync CLI exists — it's a one-shot consolidation task a developer can run before any multi-tool session.

## MVP Sketch
A YAML bundle schema, a CLI that renders it into a CLAUDE.md and a Cursor `.cursorrules` file, and a manual `sync` command that appends a dated decision entry. Experiment: have 3–5 developers who already switch tools weekly use the bundle for two weeks and self-report re-orientation time versus their prior workflow. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Any of the 8+ existing point solutions, or the tool vendors themselves (Anthropic, Cursor), could ship native cross-tool sync and absorb this overnight.
- A static bundle can drift from actual codebase state faster than developers remember to update it — staleness detection is unproven.
- Different tools' context mechanisms have different size/format limits; a single bundle may not render equally well everywhere.
- The HN thread's lack of a canonical answer could mean the problem resists a generic solution (too workflow-specific), not that no one has tried.
