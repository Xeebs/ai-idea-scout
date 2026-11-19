# Gatekeep: A Pre-Publish Quality & Design-Review Gate for Narrow MCP Servers

Anyone can wrap an API in an MCP server and ship it to the world in a weekend — and increasingly, that's exactly what's happening. The tools to catch the mistakes already exist. Nobody has wired them to the one moment that would actually matter: the moment before a server goes live.

## The Gap

In a single month, three unrelated developers independently launched narrow, single-purpose MCP servers on Show HN: a WhatsApp wrapper (3 points, 6 comments), an eSIM-purchasing server from a startup called Atli (6 points, 1 comment), and a weather-data server from Meteosource (3 points, 1 comment). None of them shared a scaffold, a linter, or a design-review checklist. Each author built their tool definitions from scratch and shipped whatever passed their own manual testing.

Meanwhile, Metabase — not a hobbyist, a company with an actual engineering team — published a blog post titled "Rebuilding the Metabase MCP server: lessons for MCP tool design." The post is a retrospective on having to *redo* their own server because they got the tool design wrong the first time. If a company with engineering resources and the benefit of hindsight still shipped a flawed first attempt, the odds that three independent weekend-project authors landed on correct tool design by instinct are not good.

The frustrating part is that the detection problem is already solved. `blackwell-systems/mcp-assert` — a 27-star linter — found 4,794 schema issues across just 55 real-world servers it was pointed at. `mcp-conform` exists as a pre-publish conformance checker against the MCP spec. Glama runs its own per-server quality and security ratings. None of this tooling is obscure or vaporware. But none of it is referenced or required by the narrow servers surveyed. The official MCP registry only checks namespace and metadata — not safety or design quality. And `awesome-mcp-servers`, the de facto community directory, tells users in its own README to vet servers themselves. The tooling exists. The enforcement point does not.

## The Project

Gatekeep is a pre-publish gate any MCP server author — or the official registry itself, as an opt-in badge — can run against a candidate server before it goes live. It pulls the server's tool manifest and source via the GitHub API, runs it through the existing schema and conformance linters (`mcp-assert`-style checks, `mcp-conform`'s spec rules), layers on a design-mistake checklist distilled from documented retrospectives like Metabase's, and returns a pass/warn/fail verdict with specific, line-level fixes.

This is deliberately not a new linting engine competing with `mcp-assert` or `mcp-conform` — it's the missing glue that turns "tooling exists somewhere" into "tooling runs on every submission." A lightweight hosted badge/API lets a registry or an `awesome-mcp-servers`-style list display the result next to each listing, giving installers a quality signal the registry itself currently doesn't provide.

## Tangible Impact

**Population**: solo/small-team MCP server authors publishing single-purpose wrapper servers (the three Show HN launches are representative of a much larger steady stream given 20,000–30,000 listed servers by Sept 2026), and — on the consumer side — developers deciding which of those servers to install into their own agent stack.
**Mechanism**: Today an author ships whatever passes their own manual testing, and a known class of schema/description mistakes (the kind `mcp-assert` found 4,794 instances of across just 55 servers) ships to users who have no visible signal to distinguish a carefully-designed server from a weekend hack. A pre-publish gate catches the mistakes before they reach a user, and a visible badge gives installers a quality signal the registry itself doesn't provide.
**Measure**: % of submitted servers failing the gate on first run (expected high, proving the gap is real); reduction in post-publish "redesign" incidents like Metabase's when authors run the gate before shipping; adoption — number of real community servers voluntarily running the badge within 3 months of launch.

## Try It

A standalone Claude Code skill version of this is already written: [`skills/mcp-narrow-server-publish-quality-gate/`](../skills/mcp-narrow-server-publish-quality-gate/). Its one-line description: *"Pre-publish design-quality review for a Model Context Protocol (MCP) server — audits tool manifest/schema for ambiguous descriptions, permission scope creep, pagination/unit inconsistencies, and missing error-handling guidance, returning a pass/warn/fail verdict with line-level fixes. Use before submitting a new MCP server to the official registry, an awesome-mcp-servers-style list, or any Show-HN-style launch."*

It takes either a public GitHub repo URL or a pasted tool manifest/schema — no hosted service required. To use it:

- **With Claude Code**: drop the `mcp-narrow-server-publish-quality-gate/` folder into `~/.claude/skills/`, then ask Claude to review your MCP server before you publish it.
- **With any other AI chat tool**: paste the contents of the skill's `README.md` into the chat, then hand over your repo URL or tool manifest.

It's explicitly a design-review companion, not a replacement for `mcp-assert` or `mcp-conform` — it checks tool naming, description clarity, schema typing, unit ambiguity, pagination, error-handling guidance, destructive-action safeguards, and permission scope creep against the manifest you give it, and tells you plainly when it can't check something (e.g. if you don't hand over permission-scope info) rather than guessing.

One honest caveat, carried straight from the idea's own risk list: if the official MCP registry ever ships its own quality gate, this project is absorbed overnight — that's a real, not hypothetical, risk given how actively the registry is still evolving. There's also no mechanism today to make any registry *require* the badge; adoption depends entirely on voluntary buy-in or a registry partnership, and the "design-mistake checklist" itself currently rests on a single documented retrospective (Metabase's) rather than a broad case-study base.

---

Surfaced from `research/2026-11-19-tool-use-mcp-ecosystem.md`, pattern `P6`.
