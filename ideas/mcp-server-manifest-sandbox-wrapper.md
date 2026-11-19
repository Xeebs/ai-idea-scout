# MCP Cell: A Manifest-Driven Default-Deny Sandbox Wrapper for Third-Party MCP Servers

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-19-tool-use-mcp-ecosystem.md · P8
- **Maturity verdict**: PARTIAL — a crowded but fragmented field exists (GitHub's own `gh-aw-firewall`; OSS tools `ressl/mcp-firewall` 22★, `technosiveuk-ui/SentinelMCP` 14★, `caiovicentino/jev-shield` claiming 94% block recall/0 false positives, `jeliasson/mcp-sandboxd` Docker/K8s isolation, `mcp-hub-corp/mcp-cage`) but none is consolidated into a default hardened runtime, and the "ClawBleed" large-scale exploit claim traces to a single secondary summary, not a primary disclosure. Tie between PARTIAL/SATURATED resolved to PARTIAL per fragmentation.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the target MCP server's own declared tool manifest/schema directly over the MCP protocol's existing tool-list call (a mature, already-available interface every MCP server implements) to auto-derive a default-deny sandbox policy; optionally cross-checks against the server's source via the GitHub API where a repo is available. No manual policy-writing required from the user.

## The Gap

evokesecurity.com frames the core risk plainly: "an MCP server can do anything the host process can do" — full filesystem, network, and exec access, by default, for any third-party server a user installs. At least six independent OSS sandboxing/firewall projects were actively pushed in the last 30 days alone (`gh-aw-firewall`, `mcp-firewall`, `SentinelMCP`, `jev-shield`, `mcp-sandboxd`, `mcp-cage`), which is strong demand signal, but each is a standalone point solution — none has become the default a host application ships with, and none derives its policy automatically from what the server itself declares it needs.

## The Project

A lightweight, manifest-driven sandbox wrapper that sits between an MCP host (Claude Code, Claude Desktop, or any other client) and a third-party server's launch command. At install time, it reads the server's own declared tool definitions over the standard MCP tool-list call, auto-derives a default-deny policy (only the filesystem paths, network domains, and exec calls plausibly implied by the declared tools are allowed), and enforces it transparently via OS-level primitives (Linux namespaces/seccomp/Landlock — process-level, not a full VM, so it stays lightweight enough to wrap every server rather than requiring per-server container/K8s setup like the heavier existing tools). Every blocked attempt is logged to an auditable trail. This differentiates from the existing fragmented tools by being manifest-driven (no hand-written policy per server) and targeting the actual host-launch integration point directly, rather than a separate firewall proxy or a heavyweight container platform.

## Tangible Impact

**Population**: developers and teams running Claude Code, Claude Desktop, or other MCP hosts who install third-party (non-first-party) MCP servers locally — a population scaling with the registry itself (20,000–30,000 listed servers by Sept 2026) and every user who installs more than a first-party handful.
**Mechanism**: Without a default sandbox, an installed third-party server runs with the full privileges of the host process — able to read arbitrary files or make arbitrary network calls regardless of what its tools claim to do. A manifest-derived default-deny wrapper converts that open-ended privilege into a scoped, auditable set of actions matching what the server actually declared, without requiring the user to write a policy by hand per server — closing the exact gap evokesecurity's framing and the ClawBleed-style exfiltration concern describe.
**Measure**: % of a red-team corpus of planted malicious MCP servers (declaring narrow tools but attempting broader fs/network/exec access) blocked without breaking legitimate declared tool calls (false-negative vs. false-positive rate); added latency overhead per tool call; number of real third-party servers successfully wrapped with zero manual policy authoring.

## Why Now

Six independent sandboxing attempts shipped in the same 30-day window — the community is actively converging on "this needs solving" but no one has unified it into something a host ships by default; a manifest-driven approach is only crisply definable now that MCP's tool-list schema is standardized and widely implemented, which it wasn't a year ago.

## Skill Angle

A standalone "draft the sandbox policy for this MCP server" skill: given an MCP server's tool manifest (fetched live via its tool-list call, or pasted as JSON for a server not yet installed), Claude derives and returns the minimal filesystem-path/network-domain/exec allowlist its declared tools plausibly require, plus flags any tool whose declared function doesn't obviously justify the permissions implied. Usable standalone by someone who wants a policy to hand-apply without running the full wrapper; differs from the project by being a one-shot policy draft rather than an always-on enforcement process.

## MVP Sketch

3–4 weeks, 1–2 people: a CLI launcher that wraps a target server's start command in a Linux namespace/seccomp sandbox, derives its initial policy from the tool-list response via a simple heuristic (declared "read file" tools → read-only access to a declared directory; declared "fetch URL" tools → allowed domains from example calls), and logs denials. Experiment: wrap 10 real community MCP servers plus 3 planted malicious ones (declaring narrow tools, attempting broader access), and measure block rate and false-positive rate on the legitimate ones.

## Risks & Open Questions

- Six existing fragmented attempts could each independently converge toward the same manifest-driven approach, eroding differentiation quickly.
- Auto-deriving a correct policy from a declared tool manifest alone is inherently heuristic — a maliciously vague manifest could still slip a dangerously broad policy through.
- OS-level sandboxing primitives (namespaces/seccomp/Landlock) vary in support across host platforms (Linux vs. macOS vs. Windows), which could force a weaker or platform-specific enforcement model.
- The "ClawBleed" large-audit claim motivating urgency is unverified secondary-source information and should not be cited as confirmed without a primary disclosure.
