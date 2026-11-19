# Continuity Desk: A Manager-Agent + Shared Notes Store So Per-Client Agent Context Survives Resets

Ask anyone running more than one AI-agent engagement at once — a freelancer juggling three clients, a small agency running concurrent builds — what actually eats their day, and it's rarely the AI being wrong. It's re-explaining what the AI already knew an hour ago, because the session reset and the context went with it.

## The Gap

An "Ask HN" thread — "How do you manage your AI agents' context across clients and projects?" (103 points, 71 comments, 2026-11-07) — reads less like a question and more like a support group. Commenters describe running one agent per client, supervised by a hand-rolled "manager" agent, with project state dumped into raw SQLite or ad hoc notes files just so it survives the next session reset. Indie Hackers posts from the same window corroborate it directly: "context management is honestly the biggest bottleneck right now," and "context gets lost between sessions... have to re-feed it." Even the dedicated tools aren't solving the whole problem — a Product Hunt launch for a memory product ("pmb") scopes memory per-workspace specifically so one client's context doesn't bleed into another's, and its own maker admits that "provenance... is still missing across most tools."

That last point is the tell. The building blocks exist — Cloudflare ships an Agent Memory service, Anthropic has a Managed Agents memory beta, AWS AgentCore does session isolation, PraisonAI has a `MultiAgentContextManager`, and generic "blackboard" shared-notepad repos are easy to find. But none of them combine a supervising manager-agent with a shared, per-project notes store that survives resets *and* tells you where each note came from. The HN thread's actual daily workflow — raw SQLite, ad hoc notes, re-pasted context — is still exactly that: hand-rolled, every time, by every person independently re-solving the same problem.

## The Project

Continuity Desk is a lightweight manager-agent runtime paired with a shared, per-project notes store that any sub-agent session reads from and writes to. Each client or project gets its own SQLite+full-text-search partition, persisted independently of any one agent session. A manager agent sits above the sub-agents, routing new work to the right partition — and, critically, logging *why* each note exists: which sub-agent wrote it, which session it came from, what triggered it. That's the piece the Product Hunt maker flagged as missing even in a dedicated memory product. When a session resets, or a new sub-agent spins up on the same project, it reads the notes store first instead of starting cold.

The components are deliberately unglamorous: a per-project SQLite+FTS store with a simple read/write API; a manager-agent process that dispatches sub-agent sessions and tags every note with its originating session/agent; a provenance log tying each note to a timestamp and source session; a CLI to search notes per project; and a transcript-ingestion adapter that auto-extracts durable facts from a sub-agent's session into the store when that session ends. None of these pieces is individually novel. Nobody has shipped them *together*, as one thing, which is exactly why the HN thread is full of people building the same half-solution alone.

## Tangible Impact

**Population**: Independent consultants, freelance developers, and small agencies — roughly the 2-20-person scale the HN thread and Indie Hackers posts describe — running concurrent AI-agent engagements across multiple clients or long-running internal projects, where every session reset currently means re-explaining project state from scratch.

**Mechanism**: Right now, a session reset (context window fills, a sub-agent starts, a different tool opens) means either manually re-pasting prior context or watching the agent silently lose it — both described directly in the HN thread as the actual daily grind. A provenance-tagged notes store that a manager agent routes reads and writes through turns "re-explain the project every reset" into "read the last three relevant notes automatically," and turns "why did the agent do that" from a chat-log grep into a traceable note-to-session lookup.

**Measure**: (1) Time spent manually re-feeding context per session reset, before vs. after, self-reported by a pilot group of freelancers and agencies. (2) How often a sub-agent re-derives a fact or decision already recorded for the same project — a measurable redundancy count. (3) Percentage of notes with a traceable provenance chain back to a source session, against a baseline of zero in hand-rolled SQLite setups today.

## Why Now

The HN thread, the Indie Hackers complaints, and the Product Hunt "pmb" launch all surfaced independently inside the same 30-day window — three unrelated sources naming the same gap without prompting each other. And the dependencies this needs (Claude Code's session hooks, mature SQLite FTS tooling) only matured enough this year that a manager-agent layer can be wired on top of them without anyone having to build the storage substrate from scratch first.

## Try It

A companion skill, `skills/manager-agent-shared-notes-continuity-store/`, already exists — and it's scoped narrower than the full runtime above, on purpose. Per its `SKILL.md`: "Audits a freelancer's or small team's current multi-client/multi-project AI agent setup and designs a concrete manager-agent + shared notes-store architecture (schema, routing rules, provenance tagging) so context survives session resets. Use when someone describes re-explaining project state every time an agent session resets, or running several AI-agent engagements in parallel with only ad hoc notes."

In practice: describe your current setup — which agents run where, how (if at all) you're keeping notes today, and where context loss has actually bitten you — and it produces a concrete layout: which facts belong in the shared store versus stay session-local, a minimal schema for the notes partition, and a provenance-tagging convention. It's useful as a one-off design review whether or not you ever build the full runtime.

To use it: paste the `README.md` into any AI chat tool (ChatGPT, Claude, Copilot) and describe your setup directly in the conversation, or — if you're running Claude Code — drop the `manager-agent-shared-notes-continuity-store/` folder into `~/.claude/skills/` so it activates automatically next time you describe the problem.

Two honest caveats from the idea file's own risk list, carried over rather than smoothed out: this is adjacent to a separate idea ("Client Wall," targeting cross-client *leak prevention* rather than context *continuity*) — the two could eventually compose, but neither replaces the other, and building this alone doesn't address leakage. And the hardest unsolved piece is auto-extracting which facts from a raw transcript are actually worth persisting — too aggressive and the store fills with noise, too conservative and it misses what people actually needed re-fed. A well-resourced memory vendor could also just ship this exact combination as a platform feature before an independent project gets traction — that's the real competitive risk, not a hypothetical one.

Surfaced from `research/2026-11-19-agentic-ai-autonomous-agents.md`, pattern `P1`.
