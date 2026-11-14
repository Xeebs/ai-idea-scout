# Compensate: A Cross-Domain Effect-Journal and Compensating-Action Layer for MCP Tool Calls

- **Status**: EXPLORING (promoted cycle 76: evidence density — ≥2 independent threads in the source digest)
- **Date**: 2026-11-14
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-14-tool-use-mcp-ecosystem.md · P1
- **Maturity verdict**: PARTIAL — at least five named point solutions exist (`agent-undo`, `react-agent-compensation`, `mcp-compensator`, `ModelActionProtocol`, `walkback`), but every one is single-author, days-to-weeks old, or filesystem-only; both ACRFence and Strayspark's own commentary treat cross-domain compensation (payments, email) as unsolved rather than pointing to an incumbent that closes it.
- **Format**: BOTH — the effect-journal/compensation runtime is persistent middleware; reviewing a tool manifest to decide which tools are reversible, idempotent-safe, or must be gated as irreversible is a separable one-shot design task.
- **Data Sources**: CONNECTED (project) — intercepts live MCP tool-call requests/responses via a client- or gateway-side MCP proxy; this specific generalized proxy doesn't exist maturely today (it's what this project builds), though the MCP transport it hooks into is mature and stable. MANUAL (skill) — the user pastes their MCP server's tool manifest (names, parameters, and a plain description of what each mutating tool does downstream).

## The Gap
Agent checkpoint/restore (shadow files, git snapshots) only resets local state; once an MCP tool call has sent an email, charged a payment, or written to an external database, nothing generalizes the fix. A dev.to post (ACRFence) argues local checkpoint/restore "can't reverse effects like payments or emails"; a Strayspark post independently names the retry-double-apply failure mode and proposes idempotency keys plus an effect journal; and five scattered single-author repos (`agent-undo`, `react-agent-compensation`, `mcp-compensator`, `ModelActionProtocol`, `walkback`) each attempt a narrow slice of this — none a maintained, cross-domain, adopted framework.

## The Project
An MCP-aware proxy/gateway middleware sitting between the agent/host and MCP servers. For every mutating tool call it writes an effect-journal entry (tool, params, idempotency key, timestamp) before forwarding the call. Each mutating tool registers, via a declarative compensation-registry entry, its inverse operation where one exists (`refund.create` compensates `payment.charge`; a CRM write's compensation is "overwrite with prior value"; an email send has none and is marked irreversible). On failure, retry, or an operator-triggered undo, the layer either replays idempotently (same key, no double-apply) or invokes the registered compensation; anything with no registered compensation is routed to human review instead of a false "undo."

Components: an effect-journal store; a compensation-registry format that individual tool authors declare rather than the layer guessing; idempotency-key enforcement at the proxy; an undo/replay CLI and API; an audit log of every compensation attempt and outcome.

## Tangible Impact
**Population**: developers and platform teams operating MCP servers whose mutating tools trigger real-world side effects — payments, refunds, CRM writes, outbound email/SMS. This is the same population the gap-analyst found independently building five different partial point-solutions within weeks of each other — concrete evidence teams are hitting this now, not hypothetically.
**Mechanism**: without a compensation layer, a bad or misfired mutating tool call requires a human to manually comb logs and the counterparty's own dashboard to reverse it. With the layer, a failed or retried call either safely no-ops (idempotency) or triggers its registered reversal automatically, and anything with no safe reversal is flagged before more damage compounds instead of discovered after the fact.
**Measure**: (1) mean time to detect and reverse a bad mutating tool call, manual log-diving vs. the layer's automatic/flagged path; (2) percentage of a pilot deployment's mutating tool calls with a registered compensating action vs. correctly flagged irreversible; (3) count of duplicate side effects (double charges/emails) prevented by idempotency enforcement, before vs. after adoption.

## Why Now
MCP tool calls are moving from read-only demos into real payment, CRM, and communication systems in 2026 production deployments. Five independent single-author point solutions have all surfaced within the same narrow window — proof the underlying primitive (effect journal + compensation registry) is feasible, but none has consolidated into a maintained, cross-domain, adopted framework yet.

## Skill Angle
Given a pasted MCP server tool manifest, produce for each mutating tool: whether it's safely reversible (and what the compensating action would be), whether it's idempotent-safe via a natural key, or whether it's irreversible and must be gated behind human confirmation before being exposed to an autonomous agent. Useful today as a one-shot design review for any MCP server author deciding how to expose a new mutating tool safely, independent of whether they ever adopt the full runtime layer.

## MVP Sketch
2–4 weeks, 1–2 people: build a thin MCP proxy logging every tool call to a SQLite effect journal; implement a YAML compensation-registry for 3–4 example tools (a mock payment charge/refund pair, a mock email send with no compensation, a mock CRM write with an undo-by-overwrite compensation); demonstrate that a crashed-and-retried charge never double-fires, and an operator-triggered "undo last 3 calls" correctly reverses the refundable ones while flagging the email send as irreversible.

## Risks & Open Questions
- Several single-author repos already occupy this exact space; real differentiation (maintained, cross-domain, actually adopted) is required, not a greenfield claim — one of them consolidating, or a vendor shipping this natively, could undercut a standalone build quickly.
- A wrong or missing compensation declaration is worse than none if trusted blindly; the registry format needs a strict default-to-irreversible-unless-proven-safe posture.
- Preventing double-apply via idempotency alone is a narrower, already-partially-covered problem (see this repo's "Fire Once" idea, `agent-side-effect-idempotency-ledger.md`); this project's real differentiator is the generalized compensating-action/undo half, which no named implementation generalizes across domains.
- Some side effects (an already-read email, an already-shipped package) have no possible compensation regardless of tooling — the project must be honest about that boundary, not pretend universal reversibility.
