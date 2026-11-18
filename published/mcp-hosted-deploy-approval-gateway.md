# One Path: A Consolidated Hosted Deployment + Approval Gateway for Internal MCP Servers

MCP crossed into mainstream enterprise production this year — Stacklok's July 2026 survey of 100 senior engineers found 41% already running it internally — and the tooling that should have matured alongside it hasn't. Ask around and you'll find two separate, unsolved fights: where do you actually host one of these things, and who signs off on letting it touch anything real. Right now, teams fight both battles from scratch, every time.

## The Gap

The complaint shows up in the wild in exactly the shape you'd expect from something genuinely unsolved. A Hacker News commenter, surfaced via WebSearch, asked plainly: "anyone else hosting MCP servers in a generally available way? ... everything I find requires running locally or hosting your own instance." The same search turned up an r/mcp poster asking "anyone here struggling to get MCPs approved in their companies?" and another r/mcp commenter calling the whole space "so fragmented... not a single way to deploy them."

What makes this a real gap rather than just griping is what a deeper search for existing fixes turned up: plenty. Speakeasy, Arcade, Prefect Horizon, Cloudflare Workers, Composio, Modal, Render, Vercel, FastMCP Cloud, MintMCP on the hosting side; vendor guides, Kiro's shipped MCP allowlisting registry, and governance platforms like Gravitee, Akto, and TrueFoundry on the approval side. Ten-plus competing, non-interoperable options — and not one of them has become the thing either users or the community point to as *the* answer. Stacklok's same survey backs this up at scale: among companies already running MCP in production, governance (34%) and security/compliance (49%) are the top-cited implementation obstacles. That's the Hacker News complaint and the r/mcp complaint, independently, showing up as the two biggest friction points in a 100-engineer survey.

## The Project

The idea is an opinionated CLI/service that collapses "where do I host this" and "who approves this" into one flow instead of two unrelated ones. `mcp launch` takes an existing MCP server repo and deploys it through one recommended default backend — Cloudflare Workers to start, with pluggable Fly.io/Modal adapters for teams that need them — wired with secure defaults (TLS, scoped auth, structured logging) baked in, and hands back one URL. No more evaluating ten-plus non-interoperable options from a blank slate every time someone wants to stand up a server.

The deploy step itself is gated behind a structured GitHub PR. Requesting a new internal MCP server opens a PR carrying a governance checklist — requested scopes, auth type, data the server touches, a named maintainer — auto-runs existing third-party trust/scanner checks against the candidate rather than reinventing them, and only triggers the actual deploy once a named approver merges. Getting hosted and getting approved become the same action, by construction, not by discipline.

Components: a deploy CLI with a default plus pluggable hosting adapters, a GitHub-PR approval template and bot, an allowlist registry tying every live deployment back to its approving PR, and a post-deploy health-check runner.

## Tangible Impact

**Population**: platform/DevEx and security engineering teams at the companies now running MCP internally — concretely the ~41% of enterprises in Stacklok's July 2026 survey (n=100 senior engineers) already past the "whether" question and into the "how do we host and approve this without rebuilding both from scratch every time" question, where governance and security/compliance are the top two named obstacles.

**Mechanism**: today a team picks a hosting backend from ten-plus non-interoperable options with no consensus, then separately has to get security/governance to bless the server with no shared checklist, scanner integration, or audit trail — most teams solve each ad hoc, or skip the second one entirely. A flow where deploy literally cannot happen until the checklist is satisfied and merged makes every live internal MCP server traceable to an approval record by construction.

**Measure**: (1) time from "we want to run this internally" to "it's live and approved," before vs. after; (2) fraction of a company's internally-run MCP servers with a traceable approval record (target: 100% via the gate, vs. today's ad hoc/undocumented baseline); (3) number of distinct hosting configurations a company ends up maintaining before vs. after adopting one default path.

## Try It

A companion skill already exists at [`skills/mcp-hosted-deploy-approval-gateway/`](../skills/mcp-hosted-deploy-approval-gateway/): "Drafts the governance checklist and PR body needed to approve a new (or changed) internal MCP server before it deploys, flags missing/overbroad fields, and recommends approve/escalate/block." It's the standalone, one-shot version of the approval half — no deploy-and-merge infrastructure required. Paste the server's manifest/tool list, auth type, data touched, and maintainer into any AI chat tool using the skill's README, or drop the `skills/mcp-hosted-deploy-approval-gateway/` folder into `~/.claude/skills/` for Claude Code, and it'll hand back a scored checklist, a flagged scope-risk table, and a ready-to-paste PR body.

## Why Risks Remain Open

This isn't a lock. Any of the named hosting vendors — Cloudflare, Modal, FastMCP Cloud — could ship this exact consolidation-plus-governance wrapper themselves and close the gap from the vendor side overnight. An opinionated single default hosting backend may also not fit companies with existing cloud or compliance constraints, which could limit early adoption to teams without strong infra preferences already in place. And the approval half risks becoming pure theater if the checklist isn't backed by real automated checks rather than a shallow form — it needs to integrate with real scanners, not invent its own. GitHub-PR-based approval also assumes a GitHub-centric workflow out of the gate; GitLab and Bitbucket shops would need a second adapter, which is real early maintenance surface, not a footnote.

---

Surfaced from `research/2026-11-18-tool-use-mcp-ecosystem.md`, pattern `P5`.
