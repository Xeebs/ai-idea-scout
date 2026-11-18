# Compensate: A Cross-Domain Effect-Journal and Compensating-Action Layer for MCP Tool Calls

Your agent framework can roll back a bad edit to a local file in milliseconds. It cannot roll back the email it just sent, the payment it just charged, or the CRM record it just overwrote — because "undo" for an MCP tool call currently means "nothing happens, and a human goes spelunking through logs and the counterparty's own dashboard to fix it by hand." That gap is no longer theoretical: five different developers have independently built narrow slices of a fix within weeks of each other, and none of them talk to each other.

## The Gap

Agent checkpoint/restore — shadow files, git snapshots — only resets local state. Once an MCP tool call has sent an email, moved money, or written to an external database, nothing generalizes the fix. A dev.to post from ACRFence argues plainly that local checkpoint/restore "can't reverse effects like payments or emails"; a Strayspark post independently names the exact failure mode that follows from this — a timed-out call getting retried and double-applying — and proposes idempotency keys plus an effect journal as the remedy. Neither post points to an existing framework that closes the gap; both treat it as open.

The proof that the gap is real and currently being worked on, badly, in parallel: five scattered single-author repos — `agent-undo`, `react-agent-compensation`, `mcp-compensator`, `ModelActionProtocol`, and `walkback` — each attempt a piece of this. `agent-undo` does saga-style journaling with reverse-order undo across MCP tools. `react-agent-compensation` auto-discovers compensation pairs via tool annotations. `mcp-compensator` is a proxy that journals mutating calls and flags irreversible ones. `ModelActionProtocol` builds a reverser registry for CRUD APIs. None of them is maintained, cross-domain, or adopted beyond its own author — several are days-to-weeks old, and at least one cites unverifiable details in its own README. The underlying primitive is clearly feasible; nobody has consolidated it.

## The Project

Compensate is an MCP-aware proxy/gateway that sits between the agent (or host) and the MCP servers it talks to. For every mutating tool call, it writes an effect-journal entry — tool, parameters, idempotency key, timestamp — before forwarding the call. Tool authors declare, via a compensation-registry entry, the inverse operation for each mutating tool where one exists: a payment charge compensates with a refund; a CRM write compensates by restoring the prior value; an email send has no inverse and is marked irreversible, full stop. On failure, retry, or an operator-triggered undo, the layer either replays idempotently off the same key (no double-apply) or invokes the registered compensation — and anything with no registered compensation routes to human review instead of pretending to undo something that can't be undone.

The pieces: an effect-journal store; a compensation-registry format that tool authors declare explicitly rather than the layer guessing at; idempotency-key enforcement at the proxy layer; an undo/replay CLI and API; and an audit log of every compensation attempt and its outcome.

## Tangible Impact

**Population**: developers and platform teams operating MCP servers whose mutating tools trigger real-world side effects — payments, refunds, CRM writes, outbound email or SMS. The same population independently building five different partial point-solutions within weeks of each other — concrete evidence teams are hitting this now, not hypothetically.

**Mechanism**: without a compensation layer, a bad or misfired mutating tool call means a human combing logs and the counterparty's own dashboard to manually reverse it. With the layer, a failed or retried call either safely no-ops via idempotency or triggers its registered reversal automatically — and anything with no safe reversal gets flagged before the damage compounds, instead of discovered after the fact.

**Measure**: (1) mean time to detect and reverse a bad mutating tool call, manual log-diving versus the layer's automatic/flagged path; (2) percentage of a pilot deployment's mutating tool calls with a registered compensating action versus correctly flagged as irreversible; (3) count of duplicate side effects — double charges, double emails — prevented by idempotency enforcement, before versus after adoption.

## Why Now

MCP tool calls are moving out of read-only demos and into real payment, CRM, and communication systems through 2026. Five independent single-author point solutions have all surfaced in the same narrow window — proof the underlying primitive (effect journal plus compensation registry) is feasible right now, but none has consolidated into a maintained, cross-domain, adopted framework.

## Try It

A companion skill already exists: **Undo Audit: MCP Tool Manifest Reversibility & Idempotency Reviewer** (`skills/mcp-tool-call-compensating-action-layer/`) — "Reviews an MCP server's tool manifest and classifies each mutating tool as REVERSIBLE (names the compensating action), IDEMPOTENT-SAFE (names the natural key), or IRREVERSIBLE/UNKNOWN (must gate behind human confirmation)." It's a design-time audit, not a runtime system, and it's useful today whether or not anyone ever builds the full Compensate layer: paste your MCP server's tool manifest into the README's prompt template in any AI chat tool, or drop the `skills/mcp-tool-call-compensating-action-layer/` folder into `~/.claude/skills/` for Claude Code.

## The Catch

This exact space already has five occupants, however thin. Real differentiation — maintained, cross-domain, actually adopted — is required here, not a greenfield claim; any one of those repos consolidating, or a vendor shipping this natively, could undercut a standalone build fast. A wrong or missing compensation declaration is also worse than none if a system trusts it blindly, so the registry needs a strict default-to-irreversible-unless-proven-safe posture, not an optimistic one. Preventing double-apply via idempotency alone is a narrower problem this repo already has a separate idea tracking (`agent-side-effect-idempotency-ledger.md`) — this project's real differentiator is the generalized compensating-action half, which no named implementation generalizes across domains today. And some side effects — an email already read, a package already shipped — have no possible compensation no matter how good the tooling gets; the project has to be honest about that boundary rather than pretend at universal reversibility.

---

Surfaced from `research/2026-11-14-tool-use-mcp-ecosystem.md`, pattern `P1`.
