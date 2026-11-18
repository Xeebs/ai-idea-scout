# One Path: A Consolidated Hosted Deployment + Approval Gateway for Internal MCP Servers

- **Status**: EXPLORING
- **Date**: 2026-11-18
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-18-tool-use-mcp-ecosystem.md · P5
- **Maturity verdict**: PARTIAL — the hosting half has no shortage of options (Speakeasy, Arcade, Prefect Horizon, Cloudflare Workers, Composio, Modal, Render, Vercel, FastMCP Cloud, MintMCP) and the governance half has vendor guides and one shipped enterprise feature (Kiro's MCP allowlisting registry) plus platforms (Gravitee, Akto, TrueFoundry governance tooling). But no implementation has become the de facto standard either users or the community point to — 10+ competing, non-interoperable options confirms the fragmentation the HN/Reddit commenters complained about, so the specific gap ("one standard path," "one approval workflow") remains real.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the deploy path wraps existing, mature hosting-provider APIs directly (Cloudflare Workers' deploy API as the default backend; Fly.io/Modal as optional adapters), and the approval workflow rides on the GitHub Pull Request API (mature, used exactly as intended) rather than inventing a new review system. No pasted data is required for the core gateway; the Skill Angle accepts a pasted or live-read tool manifest.

## The Gap
A WebSearch-surfaced Hacker News commenter asked "anyone else hosting MCP servers in a generally available way? ... everything I find requires running locally or hosting your own instance." The same search found an r/mcp poster asking "anyone here struggling to get MCPs approved in their companies?" and another r/mcp commenter calling the space "so fragmented... not a single way to deploy them." The gap-analyst confirmed both halves are real complaints with no converged winner: Stacklok's July 2026 survey of 100 senior enterprise engineers found 41% already running MCP in production, with governance (34%) and security/compliance (49%) the top-cited implementation obstacles — the exact friction the complaints describe, at scale.

## The Project
An opinionated CLI/service that collapses two separate fights — "where do I host this" and "who approves this" — into one flow. `mcp launch` takes an existing MCP server repo, deploys it through one recommended default backend (Cloudflare Workers to start, with pluggable Fly.io/Modal adapters for teams that need them) with secure defaults wired in (TLS, scoped auth, structured logging), and returns one URL — instead of making the developer evaluate 10+ non-interoperable options from scratch. Deploy is gated behind a structured GitHub PR: requesting a new internal MCP server opens a PR carrying a governance checklist (requested scopes, auth type, data the server touches, named maintainer), auto-runs existing third-party redirect-URI/trust scanners against the candidate server rather than reinventing them, and only triggers the actual deploy step once a named approver merges. Getting hosted and getting approved become the same action instead of two unrelated ones.

Components: deploy CLI with a default + pluggable hosting adapters · GitHub-PR approval template and bot · allowlist registry tying live deployments back to their approving PR · post-deploy health-check runner.

## Tangible Impact
**Population**: platform/DevEx and security engineering teams at the companies now running MCP internally — concretely the ~41% of enterprises in Stacklok's July 2026 survey (n=100 senior engineers) already past the "whether" question and into the "how do we host and approve this without rebuilding both from scratch every time" question, where governance and security/compliance are the top two named obstacles.
**Mechanism**: today a team picks a hosting backend from 10+ non-interoperable options with no consensus, then separately has to get security/governance to bless the server with no shared checklist, scanner integration, or audit trail — most teams solve each ad hoc or skip the second one entirely. A single flow where deploy literally cannot happen until the checklist is satisfied and merged makes every live internal MCP server traceable to an approval record by construction, not by discipline.
**Measure**: (1) time from "we want to run this internally" to "it's live and approved," before vs. after; (2) fraction of a company's internally-run MCP servers with a traceable approval record (target: 100% via the gate, vs. today's ad hoc/undocumented baseline); (3) number of distinct hosting configurations a company ends up maintaining before vs. after adopting one default path.

## Why Now
MCP crossed into mainstream production this year (41% of surveyed enterprises per Stacklok, corroborated by a cited 97M-install figure) while the hosting and governance tooling around it stayed fragmented into 10+ non-interoperable point solutions with no consensus winner — exactly the condition the gap-analyst confirmed by searching and finding real options but no de facto standard either half of the complaint names.

## Skill Angle
"Review a proposed MCP server before it goes live": hand the skill a server's manifest/README plus the standard checklist fields (requested scopes, auth type, data touched, maintainer); it drafts the governance PR body, flags missing or over-broad fields, and recommends approve/escalate — using the same checklist schema the always-on gateway enforces. This is a one-shot authoring/review aid for a human preparing a request; the project is the deploy-and-merge infrastructure that gates on it.

## MVP Sketch
2–4 weeks, 1–2 people. A CLI wrapping Cloudflare Workers' existing deploy API as the single default hosting backend (defer Fly.io/Modal adapters past MVP), plus a GitHub Action scaffolding the approval PR template and blocking a merge label until a named reviewer approves. Experiment: deploy 3 real internal MCP servers through the tool at a willing small team, measure time-to-live-and-approved against their prior ad hoc process.

## Risks & Open Questions
- Any of the named hosting vendors (Cloudflare, Modal, FastMCP Cloud) could ship this exact consolidation-plus-governance wrapper itself, closing the gap from the vendor side.
- An opinionated single default hosting backend may not fit companies with existing cloud/compliance constraints, limiting early adoption to teams without strong infra preferences already.
- The approval half risks becoming theater if the checklist isn't backed by real automated checks — it should integrate with existing scanners (e.g., this repo's own redirect-URI trust scanner idea) rather than inventing a shallow checklist.
- GitHub-PR-based approval assumes a GitHub-centric workflow; GitLab/Bitbucket shops need a second adapter, adding early maintenance surface.
