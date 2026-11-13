---
name: freelancer-client-context-isolation-boundary
description: Audits a freelancer's or small agency's multi-client AI coding tool setup for context-bleed risk and drafts a concrete client-isolation policy (boundary definition, tagging convention, pre-session checklist). Use when onboarding a new client, consolidating tools across clients, or after a near-miss where one client's context nearly surfaced in another's session.
---

# Client Wall: Context-Isolation Audit & Policy Drafter

## When to use this
A freelance developer or small agency (2-20 people) juggling concurrent AI-coding-tool sessions (Claude Code, Cursor, Copilot, ChatGPT, etc.) across multiple clients wants to know: "where could Client A's code, secrets, or conventions leak into Client B's session, and what's my actual policy for keeping them apart?" Trigger this skill before onboarding a new client, when consolidating tool configs, or immediately after any near-miss (a global memory file surfaced a client-specific fact, a shared snippet repo turned out to contain client code). This skill produces a one-time audit and policy document — it does not install or run any enforcement; it is the design/review half of the problem, not the runtime mechanism that mechanically blocks leaks (that is separate infrastructure this skill does not build).

## Inputs
**Data source**: Connected — when run inside Claude Code, use the Bash/Glob/Read tools to scan the user's actual project directory tree and git remote metadata (`git remote -v` per directory) directly; this is mature, built-in filesystem access requiring no new connector. When run as the portable README version in a generic chat tool with no file access, fall back to **Manual** — the user pastes a directory listing, their list of clients, which AI tools they use per engagement, and the *names/paths* of any shared config or memory files (never the file contents verbatim if those contents could contain actual client secrets or proprietary code — ask for structure, not payload).

Specifically gather:
1. The list of active clients (names or codenames are fine — no real client names required in the output).
2. The root directory (and git remote, if any) each client's work lives under.
3. Which AI coding tool(s) are used, and whether any config/memory is global (applies across all directories) versus per-project.
4. Any shared resources that currently span clients: a shared snippets/utility repo, a shared vector-memory or MCP server indexing multiple codebases, a shared terminal/session history, shared credentials or `.env` files, a shared global `CLAUDE.md`/`.cursorrules`/similar.
5. Whether anything has already leaked or nearly leaked (a near-miss is high-value signal — ask for it directly).

## Procedure
1. **Classify every context source into three buckets**:
   - **GLOBAL** — safe to cross every client boundary (the freelancer's own coding style preferences, generic non-client-derived snippets, tool usage habits).
   - **CLIENT-SCOPED** — must never cross a boundary (a specific client's proprietary code, architecture decisions, credentials, business logic, naming conventions tied to their domain).
   - **AMBIGUOUS** — needs a human decision, flagged explicitly rather than silently assigned (e.g., "a utility function I wrote while working for Client A that I now reuse everywhere" — this is client-derived IP even if it feels generic; call it out, don't auto-classify it GLOBAL).
2. **Scan the gathered setup for concrete leak points.** For each, name the mechanism, not just "be careful":
   - A global memory/config file (e.g. `~/.claude/CLAUDE.md`, a global `.cursorrules`) that already contains or could passively absorb a client-specific fact.
   - A shared snippets/utility repo cloned into more than one client's project.
   - A shared vector-memory store or MCP server indexing more than one client's codebase without per-client scoping on retrieval.
   - A single terminal/chat session kept open while switching between client directories within the same day.
   - Shared credentials, SSH keys, or `.env` values reachable from more than one client's working directory.
   - A shared ticketing/notes tool (Notion, Linear, etc.) connected to the AI tool across all clients at once.
3. **Rank each leak point** Critical (client confidentiality/contractual exposure if it fires), Moderate (internal mix-up, no contractual exposure), or Low (theoretical, no evidence it's active).
4. **Draft a client-tagging convention**: one unique client ID per client, mapped explicitly to that client's root directory and git remote (if any). This is a naming scheme the user adopts manually — this skill does not install anything that enforces it.
5. **Draft the pre-session checklist** — the three to six things the user should verify before starting work in any client's directory (right directory open, no other client's terminal/session active, shared memory file empty of client-specific content, etc.).
6. **State the residual risk explicitly.** This audit produces a policy and a checklist a human still has to follow; it does not mechanically block a mistake the way a runtime hook would. Say this plainly so the user doesn't mistake the document for a guarantee.

## Output format
A single Markdown report, "Client Isolation Audit & Policy for <user/agency name>", with these sections in order:
1. **Setup Summary** — clients, tools, and shared resources as gathered, restated so the user can confirm accuracy.
2. **Leak Points Found** — a table: `Leak Point | Mechanism | Severity | Fix Recommendation`.
3. **Boundary Definition** — the GLOBAL / CLIENT-SCOPED / AMBIGUOUS classification applied to this user's actual context sources, with the AMBIGUOUS items called out for a decision.
4. **Client Tagging Convention** — the client-ID-to-directory/remote mapping table.
5. **Pre-Session Checklist** — a short checklist, written so it can be pasted into a README or pinned note.
6. **Residual Risk** — what this policy does not and cannot catch (anything upstream of automated context assembly, e.g. manually copy-pasting code between sessions; anything requiring actual runtime enforcement rather than a followed checklist).

## Guardrails
- Never accept "I'm careful about this" as a mitigation for a named leak point — a human-memory-only control is exactly the failure mode this audit exists to surface, not a reason to downgrade severity.
- Never ask for, store, echo, or reason about the actual contents of client secrets, credentials, or proprietary code bodies — only their names, paths, and structural role. If the user pastes a file's full contents, work from its filename/structure and tell them you're disregarding the payload.
- Never assert that a specific tool feature (e.g., "Cursor supports per-directory rule scoping") exists or behaves a particular way unless you are certain from current, verifiable documentation — say "verify this in your tool's current docs" rather than guessing.
- Never recommend a workaround that weakens an actual client security/contractual requirement (e.g., don't suggest storing one client's secrets alongside another's for convenience) even if it would simplify the policy.
- Never present the output as enforcement. State plainly that this is a policy and checklist a human follows, not a mechanism that blocks a mistake — if the user needs the latter, that is separate infrastructure, not this skill.
