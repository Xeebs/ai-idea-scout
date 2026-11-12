# Client Wall: An Enforced Context-Isolation Boundary for Freelancers and Agencies

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-memory-ii.md · P5
- **Maturity verdict**: PARTIAL — three independent blogs (MindStudio, DEV.to/martinlepage26bit, Unabyss) propose slightly different ad hoc global/client/project folder taxonomies for the same named problem, but none describe tooling that mechanically enforces the boundary. The one real shipped product targeting this (Felo-Inc/memclaw, 43★) is stale (last pushed April 2026, >6 months); its actively-maintained successor (caura-ai/caura, 557★, "formerly MemClaw") pivoted upmarket to enterprise multi-tenant memory, abandoning the freelancer/agency framing. What's left serving this population is organizational discipline, not an enforced mechanism.
- **Format**: BOTH — the enforcement hook is runtime infrastructure; auditing an existing freelancer's setup and drafting a client-isolation policy is a one-shot design task.
- **Data Sources**: CONNECTED — reads the user's local project/client folder hierarchy and git remote metadata directly (which repository and directory the current agent session is rooted in) to classify global vs. client vs. project scope. No third-party API is needed; the connector is a Claude Code/Cursor hook or local MCP server that intercepts context-loading calls, which needs to be built since no existing tool enforces this today.

## The Gap
Freelancers and small agencies juggling multiple clients' codebases with the same AI coding tools face "context bleed" — one client's proprietary conventions, secrets, or architecture leaking into another client's session. Three independent 2026 posts (MindStudio's folder-structure guide, a DEV.to piece on avoiding context bleed, Unabyss's freelancer/agency-specific write-up) converge on the same problem and propose similar global/client/project folder taxonomies, but none ships a mechanism that actually prevents leakage — it's organizational discipline (remembering to keep folders separate) rather than an enforced boundary, and the one product built for exactly this population (MemClaw) went stale and its successor walked away from the freelancer market entirely.

## The Project
A lightweight hook that sits in front of a coding agent's context-loading step and mechanically enforces a declared global/client/project boundary: the user tags each project directory (or git remote) with a client ID once, and the hook refuses to let context, files, or memory tagged to Client A ever enter a session rooted in Client B's directory — not a convention the user has to remember, a check the tool runs every time. Global facts (the freelancer's own coding style, tool preferences) are explicitly allowed to cross boundaries; client-tagged facts are not. The centerpiece is the enforcement check itself, not the folder convention, which several blogs have already proposed without building the part that makes it stick.

Components: a per-directory/per-repo client-tagging config; a Claude Code/Cursor hook (or standalone MCP server) that intercepts context assembly and strips any client-tagged content that doesn't match the current session's tag; a CLI to tag/list/audit client boundaries across a freelancer's project directory; a leak-detection test mode that simulates cross-client context assembly and reports what would have leaked.

## Tangible Impact
**Population**: Freelance software developers and small agencies (2–20 people) who maintain concurrent engagements for multiple clients using the same AI coding tools across those engagements — a population large enough that three independent blogs targeted it with distinct guides in the same period, and one dedicated (now-abandoned) product was built specifically for it.
**Mechanism**: Today, preventing cross-client leakage depends entirely on the freelancer remembering to keep tool configs, memory files, and context separate per client — a single slip (opening the wrong project, a shared global memory file picking up a client-specific fact) becomes a confidentiality breach with real contractual consequences. A mechanically enforced boundary converts "I hope I kept these separate" into "the tool refuses to let them mix," removing the single point of human-memory failure.
**Measure**: (1) Rate of simulated cross-client leaks caught by the leak-detection test mode, versus a measured baseline rate of actual leaks in freelancers' current ad hoc setups (self-reported in a pilot). (2) Time freelancers spend manually re-establishing per-client context when switching clients within a day, before versus after adoption. (3) Adoption among the ~600 stars' worth of users MemClaw/Caura's pivot left without a maintained tool.

## Why Now
Three independent blog posts naming the same problem in the same 30-day window, plus a real product (MemClaw) going stale right as its successor explicitly abandoned this exact population, means the demand is validated and freshly unserved at the same time — no incumbent is currently building for freelancers/agencies in this space.

## Skill Angle
Given a description of a freelancer's or agency's current tool setup and client list (which clients, which tools, how context is currently organized), audit the setup for likely leak points and draft a client-isolation policy: what counts as global versus client-scoped, a folder/tagging convention, and a checklist to verify before starting each client session. Useful immediately as a one-off setup review, independent of whether the enforcement hook is adopted.

## MVP Sketch
A YAML config mapping project directories to client IDs, a Claude Code hook that reads the config and filters any loaded context/memory file not tagged for the current client, and a CLI leak-detection test that opens a session rooted in Client A's directory while Client B's memory file exists on disk, asserting it never appears in the assembled context. Experiment: run the test across 5 simulated multi-client setups and verify zero leaks versus a baseline run with no hook; also measure hook latency overhead on context assembly. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Caura could reverse its enterprise pivot or a new entrant could rebuild for freelancers specifically, occupying the niche before independent adoption.
- Freelancers may resist a tagging step if it adds friction to starting a new client engagement — the config overhead needs to be near-zero to beat "just remembering."
- Enforcement at the context-loading layer can't catch leakage that happens before the hook runs (e.g., a freelancer manually copy-pasting Client A's code into a Client B session) — the mechanism only covers automated context assembly, not human error outside it.
- The actual legal/contractual stakes (an NDA breach) may be rare enough in practice that freelancers underinvest in this even when the tool exists, limiting adoption to the already-careful.
