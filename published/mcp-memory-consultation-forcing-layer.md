# Make It Stick: A Cross-Host Consultation-Forcing Layer for MCP Memory Servers

You stood up an MCP memory server. You wired it into your host. You tested it once, saw it work, and moved on — and somewhere in the following week, it quietly stopped being called at all. Not broken. Not misconfigured. Just never consulted, turn after turn, while your agent cheerfully re-asks you things it was supposed to remember.

That is not a hypothetical. It is a filed Claude Desktop bug report showing zero tool-calls to a registered memory server across a full session, a matching Cursor forum thread, and a small pile of "my agent has amnesia" posts — three independent channels, same root cause, inside the last 30 days.

## The Gap

Registering a memory layer as an MCP server tells the host that a tool exists. It does nothing to force the host's turn loop or system prompt to actually call that tool. MCP is a registration mechanism, not a guarantee of use — so a perfectly correct, perfectly reachable memory server can sit completely idle unless the host application happens to be separately wired to invoke it every turn, and most aren't. The Claude Desktop bug report is the sharpest version of this: a user with a registered server, confirmed reachable, and a transcript showing it was never called once. The Cursor forum thread describes the identical shape of problem on a different host, and a cluster of DEV.to "my agent has amnesia" posts shows the same failure being independently rediscovered by people who assumed registering the server was the whole job.

The one fix anyone has actually found in the wild is a single commenter's hand-rolled trick: using Claude Code's HTTP hooks to force a retrieval call themselves. It works, for them, on that one host. It isn't a library, an adapter, or anything another MCP memory server author or user could pick up and use. Searching GitHub for "MCP memory server" turns up plenty of servers that store memory — and nothing that solves the separate problem of making sure memory actually gets *read*.

## The Project

A host-agnostic middleware layer that sits between an MCP memory server and whatever host is running it, and converts "the server is registered" into "the server was actually called this turn" — every turn, regardless of whether the host's own wiring would have bothered.

On hosts that expose a hook or extension system — Claude Code's HTTP hooks today — the layer registers itself there and issues retrieval/write calls directly, rather than hoping the model decides the tool is worth calling. On hosts with no such hook, it runs as a thin proxy in the MCP transport path, injecting a synthetic "check memory now" call ahead of the model's real turn whenever the host hasn't already made one recently.

Four pieces make up the system: a per-host adapter registry (Claude Code's HTTP hooks first, since that's the only proven extension point today); a transport-level proxy fallback for hosts without native hooks; a per-turn consultation ledger, so a user or server author can verify consultation actually happened rather than just that the server is theoretically reachable; and a configurable firing policy — every turn versus a staleness/keyword trigger — to keep the fix from trading "never remembers" for "always slow."

## Tangible Impact

**Population**: Developers and power users who have deployed an MCP memory server — mem0's MCP server, OpenMemory, or something custom — expecting real cross-session recall, and are hitting the specific, now-repeatedly-reported failure where the server is correctly registered but simply never called. This is the exact population behind the Claude Desktop bug report, the Cursor forum thread, and the "my agent has amnesia" post cluster.

**Mechanism**: Right now, a correctly configured MCP memory server delivers zero practical benefit the moment the host's model declines to invoke it — and the only known escape hatch is rebuilding one commenter's HTTP-hooks trick from scratch, for your own host, yourself. A packaged forcing layer removes that rebuild step entirely: install it, and "registered" starts meaning "consulted."

**Measure**: (1) Tool-call invocation rate to the memory server per session, before vs. after — directly answering the Claude Desktop bug report's "zero calls" finding. (2) Recall accuracy on a held-out cross-session fact-recall task, with vs. without the layer installed. (3) Added per-turn latency from the forced check, to confirm the fix doesn't just swap one failure mode for another.

## Why Now

Three independent channels — a filed bug report, a separate forum thread, and multiple blog posts — converged on the same diagnosis within the last 30 days, which is a stronger signal than any one of them alone. And the one proven workaround, Claude Code's HTTP hooks, is already a mature, documented extension point, so a first real adapter can ship today on at least one major host without waiting on any vendor to add new capability.

## Try It

No companion skill exists yet for this idea — it's tagged **BOTH** (the forcing layer itself is PROJECT-shaped persistent middleware; a separable SKILL would diagnose why a specific user's existing MCP memory setup isn't being consulted and draft the host-specific fix), but the skill side hasn't been synthesized yet. Check back on `skills/mcp-memory-consultation-forcing-layer/` once it lands.

## Risks & Open Questions

Host vendors could simply ship native "always consult registered memory tools" behavior directly — the correct fix, and one that would make the Claude Code adapter obsolete overnight, though the no-hook-host proxy fallback would likely stay useful longer. Forcing a consultation call every turn has a real latency and token cost even on turns where memory isn't relevant, and the staleness/keyword-triggered alternative to a fixed interval is unproven. The transport-level proxy for hosts without native hooks is the harder, riskier half of the build — it may require intercepting traffic in ways a host's terms of service or sandboxing don't cleanly permit, which needs checking per host before committing real engineering time. And the evidence for the hooks-based approach generalizing beyond one person's setup is currently a single informal comment — thin enough that the MVP's held-out recall experiment is the first real test of whether it holds up.

---

Surfaced from `research/2026-11-20-context-engineering-memory.md`, pattern `P4`.
