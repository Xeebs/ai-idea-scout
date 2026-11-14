---
name: agent-labor-marketplace-escrow-protocol
description: Turns a seller's plain-language description of an AI agent service into an escrow-ready listing — price, deliverable spec, and machine-checkable acceptance criteria — that can be loaded into an agent labor marketplace / escrow protocol (e.g. WorkLedger-style, Stripe Connect-backed). Use when someone wants to sell agent-to-agent or agent-to-human task work and needs the listing in a form a payment-release check could actually enforce, not just a sales blurb.
---

# Agent Labor Listing & Escrow-Spec Drafter

## When to use this
The user has built an agent or automated service (a research agent, a data-extraction pipeline, a review/QA bot, a content-generation service, etc.) and wants to sell access to it — to another agent, another builder, or a marketplace — but what they have today is informal ("my agent does X for $Y, message me"). Reach for this skill when they need that turned into a listing precise enough that payment could be released automatically against a completion check, rather than on trust or a human eyeballing it after the fact. This is a one-shot drafting task — it produces listing text, it does not run escrow, hold funds, or resolve disputes.

## Inputs
**Data source**: Connected — the parent WorkLedger protocol this skill supports reads/writes via Stripe Connect's API (mature, widely used today for marketplace escrow holds and releases) and the protocol's own listing registry for discovery. This skill itself does not call either API: it is a drafting aid that produces the listing/acceptance-criteria text a seller then loads into a marketplace protocol or escrow registry (WorkLedger or any compatible one) — the actual fund-holding and release still happens in that connected system, not here.

What the seller hands over (manual, pasted in this conversation):
1. A plain-language description of what the agent/service does — inputs it takes, outputs it produces.
2. How they currently price it, if at all (per-task flat fee, per-unit, subscription, or "no idea yet").
3. 1-3 examples of a completed deliverable, or a description of one, if available.
4. Typical turnaround time.
5. Any past disputes or complaints about the work, if this isn't the first time they've sold it (optional but valuable — it tells you what criteria were missing).

## Procedure
1. **Classify the deliverable type** from the description: (a) structured data output (JSON/CSV/schema-conformant), (b) a generated artifact (document, image, code, report), (c) a binary action completed (a task performed in an external system), or (d) a judgment call (quality/relevance assessment with no hard schema). This classification determines how strict the acceptance criteria can be.
2. **Draft the price.** If the seller gave a number, use it and state the unit (per task / per 1,000 units / per month). If they didn't, do not invent one — compute a cost-basis estimate only from numbers they gave (e.g. turnaround time, stated compute/API cost) and mark it `[NEEDS SELLER CONFIRMATION]`, don't present a guess as the price.
3. **Draft the deliverable spec**: the exact shape of what gets delivered — field names and types for structured output, file format and required sections for an artifact, or the specific external-system state change for an action. Pull this directly from the seller's description and examples; don't add fields they never mentioned.
4. **Draft machine-checkable acceptance criteria** as a numbered checklist. For each criterion, state the automated check that would verify it (schema validation passes, required field non-empty, numeric value within stated range, deliverable received before stated deadline, no error/exception state returned). For deliverable type (d) or any criterion that is inherently a judgment call ("the writing is engaging," "the analysis is correct"), do not disguise it as machine-checkable — tag it explicitly `[NOT MACHINE-CHECKABLE — requires human or AI-judge review]` and say what a reviewer would need to check.
5. **Draft the escalation note**: one sentence stating what happens if an automated check fails or a `[NOT MACHINE-CHECKABLE]` item is disputed — route to manual/human review before any fund release, since this skill does not resolve disputes itself and should not imply automatic refund/release logic it hasn't verified exists in the target protocol.
6. **Flag open items**: list anything the seller didn't provide that the listing needs before it's truly escrow-ready (missing price confirmation, missing turnaround, ambiguous deliverable format).
7. Return the full listing in the Output format below. Do not submit it anywhere — the user copies it into their marketplace/protocol of choice.

## Output format
A single Markdown block, ready to paste elsewhere:

```
## Listing: <short service name>

**Price**: <amount + unit, or [NEEDS SELLER CONFIRMATION]>
**Turnaround**: <stated turnaround>
**Deliverable type**: <structured data | artifact | action | judgment call>

### Deliverable Spec
<exact output shape: fields/types, file format + required sections, or action + target system>

### Acceptance Criteria
1. <criterion> — automated check: <what gets verified>
2. <criterion> — automated check: <what gets verified>
...
N. <criterion> — [NOT MACHINE-CHECKABLE — requires human/AI-judge review: <what a reviewer checks>]

### Escalation
<one sentence: what happens on a failed/disputed check>

### Open Items Before This Listing Is Escrow-Ready
- <anything missing or ambiguous, or "None — ready as drafted" if nothing is outstanding>
```

## Guardrails
- Never invent a price the seller didn't give or derive from numbers they stated — mark it `[NEEDS SELLER CONFIRMATION]` instead of guessing.
- Never label a subjective, judgment-based criterion as machine-checkable. If an automated check can't actually verify it, say so explicitly rather than producing a listing that looks enforceable but isn't.
- Never claim this skill holds funds, executes escrow, or resolves disputes — it drafts listing text only; the actual escrow/payment rail is a separate connected system (Stripe Connect-backed per the parent idea) that this skill does not call.
- Never add deliverable fields, capabilities, or claims the seller did not state — draft from what they gave you, flag gaps instead of filling them with assumptions.
- If the seller's description is too vague to classify the deliverable type, ask one clarifying question before drafting rather than guessing and producing a listing that doesn't match what they actually sell.
