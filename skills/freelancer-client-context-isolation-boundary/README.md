# Client Wall: Context-Isolation Audit & Policy Drafter

A paste-into-any-AI-chat-tool prompt for freelance developers and small agencies (2-20 people) who run concurrent AI-coding-tool sessions (Claude Code, Cursor, Copilot, ChatGPT, etc.) across multiple clients. It audits your current setup for "context bleed" — one client's proprietary code, secrets, or conventions leaking into another client's session — and hands you back a concrete isolation policy: a boundary definition, a tagging convention, and a pre-session checklist.

This is a one-time design/audit document, not a running tool. It does not install anything and does not mechanically block a future mistake — it tells you where your current setup is exposed and gives you a checklist to run by hand before each client session. If you want an actual enforcement mechanism that blocks leaks automatically, that's a separate piece of infrastructure (a hook/MCP server that intercepts context loading) — this skill is the audit-and-policy half, not the runtime half.

## When to use this
- You're about to onboard a new client and want your multi-client setup audited before you start.
- You're consolidating AI tool configs (e.g., moving several clients onto Claude Code or Cursor) and want a clean boundary defined up front.
- You just had a near-miss — a global memory file surfaced a fact from the wrong client, or you noticed a shared snippets repo contains client-specific code — and want to find every other place that could happen.

## What to hand over

**Data source: Manual.** Paste the following into the chat (most generic chat tools have no access to your filesystem, so you provide it directly):

1. Your list of active clients (codenames are fine, e.g. "Client A — fintech dashboard").
2. The root directory (and git remote if you use one) each client's work lives under.
3. Which AI coding tool(s) you use, and whether any part of your config/memory is **global** (applies no matter which project you're in) versus **per-project**.
4. Anything currently **shared across clients**: a shared snippets/utility repo, a shared memory/vector-search tool indexing more than one codebase, a shared terminal or chat session you keep open while switching clients, shared credentials or `.env` files, a shared global memory file (e.g. a global `CLAUDE.md` or `.cursorrules`).
5. Whether anything has already leaked or nearly leaked between clients — this is the single highest-value thing you can report, even if it feels embarrassing.

**Important**: describe the *names, paths, and structure* of any shared files — do not paste the actual contents of secrets, credentials, or real client code into the chat. If you paste a full file by accident, say so and the assistant should work only from the filename/structure, not the payload.

## The procedure the assistant follows

1. **Classify every context source into three buckets**:
   - **GLOBAL** — safe everywhere (your own coding style, generic non-client-derived snippets, personal tool habits).
   - **CLIENT-SCOPED** — must never cross a boundary (a client's proprietary code, architecture, credentials, business logic, domain-specific naming).
   - **AMBIGUOUS** — flagged for you to decide, not silently assigned. Example: a utility function you first wrote for Client A that you now reuse everywhere is still client-derived IP — it gets flagged, not auto-approved as GLOBAL.
2. **Scan for concrete leak points** and name the mechanism for each, not a vague "be careful": global memory/config files that could passively absorb a client fact; a shared snippets repo cloned into multiple client projects; a shared memory/vector-search tool indexing multiple clients without per-client scoping; one terminal/session kept open across clients in the same day; shared credentials reachable from more than one client's directory; a shared notes/ticketing tool connected across all clients at once.
3. **Rank each leak point**: Critical (real confidentiality/contractual exposure), Moderate (internal mix-up risk only), or Low (theoretical, no active evidence).
4. **Draft a client-tagging convention** — one ID per client mapped to its root directory/remote. This is a naming scheme you adopt by hand; nothing enforces it automatically.
5. **Draft a pre-session checklist** — 3-6 concrete things to verify before starting work in any client's directory.
6. **State the residual risk plainly** — this document is a policy and checklist a human follows, not a mechanism that blocks a mistake. Anything that happens before or outside your AI tool's context assembly (e.g., manually copy-pasting code between sessions) is explicitly out of scope.

## What you get back

A single Markdown report, "Client Isolation Audit & Policy for <you/your agency>", structured as:

1. **Setup Summary** — your clients, tools, and shared resources, restated so you can confirm it's accurate.
2. **Leak Points Found** — a table of `Leak Point | Mechanism | Severity | Fix Recommendation`.
3. **Boundary Definition** — your actual context sources sorted into GLOBAL / CLIENT-SCOPED / AMBIGUOUS, with AMBIGUOUS items called out for your decision.
4. **Client Tagging Convention** — a table mapping each client ID to its directory/remote.
5. **Pre-Session Checklist** — short enough to paste into a pinned note or your own README.
6. **Residual Risk** — exactly what this policy does not and cannot catch.

## Guardrails (what the assistant should never do)

- Never accept "I'm careful about this" as a fix for a named leak point — relying on human memory alone is the exact failure mode this audit exists to catch, not a reason to downgrade severity.
- Never ask for, repeat, or reason about the actual contents of secrets or proprietary code — only names, paths, and structure. If you paste real contents by mistake, the assistant should disregard the payload and work from the filename/structure only.
- Never assert a specific tool feature exists or behaves a certain way without being sure — "verify this in your tool's current docs" instead of guessing.
- Never suggest a workaround that weakens a real client security or contractual requirement, even if it would make the policy simpler.
- Never present the output as something that automatically blocks a future mistake. It's a policy and checklist you run by hand — if you need actual enforcement, that's a different, separate piece of tooling.
