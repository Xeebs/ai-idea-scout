Four months ago, the Model Context Protocol spec quietly fixed one of the uglier security holes in its OAuth-style authorization flow. Last month, an independent test of 119 live MCP servers found that 114 of them — 96% — are still wide open to it.

That's not a slow rollout. That's a fix nobody installed.

## The Gap

The hole is a classic open-redirect: when an MCP client does OAuth-style authorization against a self-hosted server, the server is supposed to check that the `redirect_uri` the client hands back matches one it already knows about. If it doesn't check — or checks loosely, with a prefix match or a wildcard — an attacker can swap in their own redirect target and walk away with a stolen authorization code. The MCP spec's 2026-07-28 revision tightened this up on paper: exact pre-registered-URI matching, SEP-837 guidance for localhost redirects used by CLI and desktop clients, and SSRF considerations for Client ID Metadata Documents. What it still leaves undefined, by its own admission, is trust for *self-hosted servers doing dynamic client registration from anonymous clients* — the exact scenario a growing share of the MCP ecosystem runs on.

A Hacker News post from a security-minded blogger ("Letting users trust their own MCP clients, without opening a phishing hole," 2026-11-04, 35 points / 6 comments) spelled this out and then did the thing almost nobody does with a theoretical vulnerability: tested it. The author scanned 119 live, registry-listed MCP servers and found 114 still accepting arbitrary redirect URIs. A related Claude Code issue asking for a fix was closed "not planned." The spec-level patch exists. The install base hasn't moved.

That combination — a real spec fix, a near-total implementation gap, and a single-post disclosure with no follow-up tooling — is exactly the shape of gap this project is built to close before it becomes something worse than a blog post.

## The Project

Two pieces, aimed at the two different audiences who need to act before this turns into an incident.

The first is a drop-in validation middleware for MCP server authors, shipped for Node and Python — the two dominant MCP server runtimes — that enforces exact pre-registered-redirect-URI matching plus the SEP-837 localhost exception by default. The pitch to a server author isn't "go read the spec's security-considerations section and implement it correctly yourself," it's "install this dependency." That's the gap between a fix existing and a fix actually landing in the 114 vulnerable servers' codebases.

The second is a public, re-runnable scanner modeled directly on the blog author's one-off probe — except maintained and automated, checking live registry-listed servers for arbitrary-redirect-URI acceptance and other known authorization misconfigurations, and publishing a scored, dated audit. Think Qualys SSL Labs for MCP authorization: something a server operator or a downstream client author can check *before* trusting a server, not something that only gets discovered after a phishing incident makes the news. Right now that visibility doesn't exist at all — the only number anyone has is one person's manual test of 119 servers, run once.

## Tangible Impact

**Population**: Operators of the self-hosted and dynamically-registered MCP servers in the 20,000–30,000-server official registry (as of September 2026) that support OAuth-style client authorization — concretely, the 114 of 119 servers the blog author found vulnerable, and by extension the much larger unscanned population behind them — plus every end user who authorizes an MCP client against one of those servers and is thereby exposed to redirect-based authorization-code theft.
**Mechanism**: Today a server author has to independently read and correctly implement the spec's security-considerations section to avoid the vulnerability, and nothing tells a user or downstream integrator whether a given server did; the middleware collapses "correctly implement redirect-URI validation" into "install this dependency," and the public scanner turns an invisible, unverifiable security posture into a checkable, dated score before anyone authorizes against it.
**Measure**: Re-run of the 119-server-style scan at intervals, tracking the % of scanned servers accepting arbitrary redirect URIs over time (baseline: 96% vulnerable); number/% of registry-listed servers that adopt the middleware within 6 months of launch; red-team success rate of a scripted open-redirect phishing PoC against servers before vs. after middleware adoption.

## Try It

A companion Claude Code skill already exists at [`skills/mcp-redirect-uri-trust-scanner/`](../skills/mcp-redirect-uri-trust-scanner/) — a point-in-time code review, distinct from the always-on middleware or the continuously-run public scanner described above. Its one-line description: "Audits a self-hosted MCP server's OAuth-style authorization code (redirect-URI validation, localhost/SEP-837 handling, dynamic-client-registration trust gaps) against the MCP spec's 2026-07-28 security considerations and the open-redirect pattern found vulnerable in 114 of 119 live servers. Use when a user is building, reviewing, or about to expose a self-hosted MCP server that implements OAuth/dynamic client registration and wants a one-time check before shipping."

To use it: paste the skill's `README.md` into any AI chat tool along with your server's `/authorize` and `/register` handler source (it needs the actual code, not a description — it won't guess), or drop the `skills/mcp-redirect-uri-trust-scanner/` folder into `~/.claude/skills/` if you're working in Claude Code. It runs five concrete checks — exact-match validation, SEP-837 localhost handling, dynamic-client-registration trust binding, URL-parsing correctness against host-confusion bypasses, and authorization-code binding at redemption — and returns a PASS/WARN/FAIL verdict with file-level evidence and a runnable fix, never defaulting an unresolved check to a pass.

Worth knowing before you build on this: the gap this targets could shrink fast on its own. If the MCP Registry or a major host ships this validation as a built-in default, or the next spec revision defines "trust" for dynamic registration directly, the middleware's value drops to "reference implementation of the spec" rather than filling an open hole. And the public scanner, by design, surfaces vulnerable servers before they've patched — treat that as a responsible-disclosure problem to solve up front, not an afterthought.

Surfaced from `research/2026-11-12-tool-use-mcp-ecosystem.md`, pattern `P3`.
