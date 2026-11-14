---
name: mcp-tool-call-compensating-action-layer
description: Reviews an MCP server's tool manifest and classifies each mutating tool as REVERSIBLE (names the compensating action), IDEMPOTENT-SAFE (names the natural key), or IRREVERSIBLE/UNKNOWN (must gate behind human confirmation). Use before exposing a new MCP tool to an autonomous agent, or when auditing an existing server's manifest for undo/retry safety.
---

# Undo Audit: MCP Tool Manifest Reversibility & Idempotency Reviewer

## When to use this
Someone has written, or is about to expose, one or more MCP tools that have real-world side effects (payments, refunds, CRM writes, email/SMS sends, database mutations) and wants a one-shot answer to: "if an agent calls this wrong, calls it twice, or needs to undo it, what actually happens — and which of these tools need a human in the loop before an autonomous agent gets to call them unsupervised?" This is a design-time audit, not a runtime system — it produces a classification and a recommendation, not an actual undo mechanism.

## Inputs
**Data source**: Manual — the user pastes their MCP server's tool manifest: tool names, parameters (with types), and a plain-language description of what each mutating tool actually does downstream (what system it writes to, what side effect it causes outside the agent's own sandbox). If the manifest's descriptions don't say what happens downstream, the user must supply that detail per tool — the skill does not guess at undocumented side effects.

Optional, improves accuracy:
- Any existing retry/idempotency-key handling already in the tool's implementation.
- Any existing compensating/undo endpoint already in the same API surface (e.g., a `refund.create` next to `payment.charge`).

## Procedure
1. **List every tool** in the manifest. Mark each **read-only** (no side effect outside the agent's own context — skip, no further classification needed) or **mutating** (writes, charges, sends, deletes, or otherwise changes state outside the current conversation).
2. **For each mutating tool**, evaluate three independent axes — never conflate them:
   - **Reversibility**: Does an inverse operation exist that undoes this tool's effect? Only answer yes if the manifest/description *explicitly* states or clearly implies the inverse exists (e.g., a `charge` next to a `refund` in the same manifest, or the description says "can be cancelled within X days"). A tool that merely *sounds* reversible (`cancel_order`) is not automatically reversible — a cancelled order may not auto-refund an already-captured payment; treat that gap as a separate, unverified claim.
   - **Idempotency**: Does the tool's parameters include, or could the caller supply, a natural idempotency key (order ID, request ID, an externally-unique identifier) such that calling it twice with the same key is safe? If the manifest doesn't mention dedup/key behavior, mark it unconfirmed rather than assuming the underlying API handles it.
   - **Irreversibility**: If no inverse operation can be identified and none is claimed, the tool is irreversible by default. This includes anything where the real-world effect already happened before any undo could apply (a sent email already read, an SMS already delivered, a shipped package).
3. **Apply the default-to-caution rule**: a tool only earns REVERSIBLE or IDEMPOTENT-SAFE when there is explicit evidence in the manifest/description. Everything else — including anything merely plausible-sounding — is classified IRREVERSIBLE/UNKNOWN and flagged for human-confirmation gating. Never let an inferred or assumed compensation pass as confirmed.
4. **Derive a recommendation per tool**: REVERSIBLE tools get "safe for autonomous use once the named compensating action is wired up and tested"; IDEMPOTENT-SAFE tools get "safe to retry automatically using the named key"; IRREVERSIBLE/UNKNOWN tools get "gate behind explicit human confirmation before any autonomous agent is allowed to call this — do not expose it as auto-approved."
5. **Produce the output** (format below), including a ready-to-paste compensation-registry stub for any tool that got a confirmed compensating action named, so the classification can be carried directly into config if the user later adopts a runtime enforcement layer.

## Output format
A single Markdown report:

```
## Tool Manifest Audit — <server name, if given>

| Tool | Mutating? | Classification | Compensating action / idempotency key | Recommendation |
|------|-----------|-----------------|------------------------------------------|-----------------|
| <name> | Yes/No | REVERSIBLE / IDEMPOTENT-SAFE / IRREVERSIBLE-UNKNOWN | <named action or key, or "none found"> | <gate / auto-retry-safe / safe-once-wired> |

### Per-tool notes
<name>: <2-4 sentences — the evidence (or lack of it) from the manifest that drove the classification; name explicitly if this is an assumption that needs the user to confirm>
...

### Compensation-registry stub (for confirmed REVERSIBLE tools only)
​```yaml
<tool_name>:
  compensates: <inverse_tool_name>
  idempotency_key: <field name, or "none confirmed">
​```

### Open questions
- <any tool where the manifest didn't give enough detail to classify confidently, and exactly what detail is missing>
```

If every tool is read-only, report that directly and skip the table.

## Guardrails
- Never mark a tool REVERSIBLE or IDEMPOTENT-SAFE without the manifest or user explicitly confirming the inverse operation or key exists — a plausible-sounding tool name is not evidence.
- Never treat "cancel" or "void" as automatically meaning "fully reverses all downstream effects" — a cancellation and a refund/reversal can be two different operations; call this out by name whenever a tool's name implies more reversal than its description confirms.
- Never conflate idempotency with reversibility — a tool can be safely retriable (idempotent) and still have zero undo path (irreversible), or vice versa.
- Always flag IRREVERSIBLE/UNKNOWN tools for human-confirmation gating explicitly; never leave a tool unclassified or silently default it to safe.
- State plainly that this is a one-time design review, not an enforcement mechanism — it does not implement idempotency keys, journaling, or undo logic; it tells the user which tools need that work before being exposed autonomously.
