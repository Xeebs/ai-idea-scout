# Undo Audit: MCP Tool Manifest Reversibility & Idempotency Reviewer

A self-contained prompt template. Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.), fill in the manifest, and send it. No other context or setup is required.

## When to use this

You've written, or are about to expose, one or more MCP (Model Context Protocol) tools whose calls have real-world side effects — charging a card, sending an email, writing to a CRM, deleting a record — and you want a one-shot answer before you let an autonomous agent call them unsupervised: if this gets called wrong, called twice, or needs to be undone, what actually happens? Which of these tools need a human to confirm before an agent can fire them on its own?

This is a design-time audit. It does not build or run an undo system for you — it tells you, tool by tool, which ones are safe to automate and which ones need a human in the loop first.

## What to hand it

1. **The tool manifest**: for every tool, its name, its parameters (with types), and a plain-language description of what it actually does *downstream* — what external system it touches and what side effect it causes outside the current conversation. If your tool descriptions don't already say this, write one or two sentences per tool yourself before pasting.
2. *(Optional, improves accuracy)* Any retry/idempotency-key handling your tool implementation already has, and any existing "undo" or inverse endpoint in the same API surface (e.g. a `refund.create` next to a `payment.charge`).

Do not paste real production credentials or live customer data — tool names, parameter schemas, and descriptions of behavior are all that's needed.

## The prompt

```
You are auditing an MCP server's tool manifest for undo and retry safety before it gets exposed to an autonomous agent.

For every tool in the manifest below, first mark it read-only (no side effect outside this conversation) or mutating (writes, charges, sends, deletes, or otherwise changes state elsewhere). Skip read-only tools from further analysis.

For every mutating tool, evaluate three separate axes:

1. Reversibility — is there an inverse operation that undoes this tool's effect? Only answer yes if the manifest explicitly states or clearly implies the inverse exists (e.g. a refund operation next to a charge operation, or "cancellable within X days" stated in the description). A tool name that merely sounds reversible (like "cancel_order") is NOT automatically reversible — a cancellation may not refund an already-captured payment. Treat that as a separate, unconfirmed claim and say so.

2. Idempotency — does the tool accept, or could the caller supply, a natural idempotency key (an order ID, request ID, or other externally-unique identifier) such that calling it twice with the same key is safe? If the manifest doesn't mention this, mark it "unconfirmed" — do not assume the underlying system already deduplicates.

3. Irreversibility — if no inverse operation is identified or claimed, classify the tool as irreversible by default. This includes effects that are already final the moment they happen (an email already delivered and read, an SMS already sent, a package already shipped).

Default to caution: only classify a tool REVERSIBLE or IDEMPOTENT-SAFE when there is explicit evidence in the manifest. Everything else — including anything that merely sounds safe — gets classified IRREVERSIBLE-UNKNOWN and flagged for mandatory human confirmation before any autonomous agent may call it.

For each tool, give a recommendation:
- REVERSIBLE → "safe for autonomous use once the named compensating action is wired up and tested"
- IDEMPOTENT-SAFE → "safe to retry automatically using the named key"
- IRREVERSIBLE-UNKNOWN → "gate behind explicit human confirmation before any autonomous agent is allowed to call this"

Output format:

## Tool Manifest Audit

A markdown table: Tool | Mutating? | Classification | Compensating action / idempotency key (or "none found") | Recommendation

Then "Per-tool notes": 2-4 sentences per mutating tool explaining the evidence (or lack of it) behind the classification, explicitly flagging anything that's an assumption needing my confirmation.

Then a "Compensation-registry stub" in YAML for every tool you classified REVERSIBLE, in the form:
<tool_name>:
  compensates: <inverse_tool_name>
  idempotency_key: <field name, or "none confirmed">

Then "Open questions": any tool where the manifest didn't give you enough detail to classify confidently, and exactly what detail you need from me to finish the classification.

If every tool turns out to be read-only, just tell me that directly instead of producing an empty table.

Never mark a tool REVERSIBLE or IDEMPOTENT-SAFE on a guess — a plausible-sounding name is not evidence. Never conflate reversibility and idempotency; a tool can be retry-safe with zero undo path, or have an undo path but no safe retry behavior. This review doesn't implement anything — say so plainly — it only tells me which tools need engineering work (idempotency keys, a compensating action, or a confirmation gate) before I expose them to an autonomous agent.

Here is my tool manifest:

<PASTE TOOL MANIFEST HERE — name, parameters, and downstream behavior description per tool>
```

## What you get back

A markdown report: a summary table classifying every mutating tool as REVERSIBLE, IDEMPOTENT-SAFE, or IRREVERSIBLE-UNKNOWN with a named compensating action or idempotency key where one was confirmed; per-tool reasoning notes that call out unconfirmed assumptions by name; a ready-to-paste YAML compensation-registry stub for confirmed-reversible tools; and an open-questions list for anything the manifest didn't say enough about to classify with confidence.

## What this does not do

It does not implement idempotency keys, an effect journal, or an actual undo/compensation runtime — it is a point-in-time design review that tells you where that engineering work is needed before you let an agent call these tools unsupervised. If you want the running system, that's a separate build (an MCP-aware proxy with an effect journal and a compensation registry), not this skill.
