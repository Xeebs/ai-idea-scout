# Agent Labor Listing & Escrow-Spec Drafter

A prompt template for turning an informal "my agent does X, message me for pricing" pitch into a precise, escrow-ready listing — the kind of listing a payment-release check could actually enforce, instead of relying on trust or a human eyeballing the work after it's done.

## When to use this

You've built an agent or automated service (a research agent, a data-extraction pipeline, a code-review bot, a content-generation service, anything that takes an input and produces a deliverable) and you want to sell access to it — to another AI agent, another builder, or on an agent labor marketplace — but right now your "listing" is a sentence in a README or a DM. You need the price, the exact deliverable shape, and acceptance criteria specific enough that an automated check (or a human judge, where it has to be) could decide whether the work was actually delivered before money changes hands.

This is a one-shot drafting task. It produces listing text. It does not hold funds, run escrow, process payment, or resolve disputes — those happen in whatever marketplace or escrow protocol you load the listing into (this was designed alongside a Stripe Connect-backed escrow protocol called WorkLedger, but the output works with any compatible system).

## Data source

**Connected, but not by this prompt.** The marketplace/escrow system this listing is meant for reads and writes through Stripe Connect's API (a mature, widely-used payment rail for marketplace escrow holds and releases) and its own listing registry. This drafting prompt itself doesn't call either API — you paste in your service description, it hands you back listing text, and *you* load that text into the connected system that actually holds and releases funds.

## What to hand over

Paste in, in plain language:

1. **What your agent/service does** — what input it takes, what output it produces.
2. **How you currently price it**, if at all — flat fee per task, per-unit, subscription, or "I haven't figured out pricing yet."
3. **1-3 examples of a completed deliverable**, or a description of one, if you have them.
4. **Typical turnaround time.**
5. (Optional but useful) **Any past disputes or complaints** about the work, if you've sold it informally before — this tells the drafter what criteria were missing last time.

## The procedure

When you give this prompt your service description, it will:

1. **Classify what you're actually delivering** — a structured data output (JSON/CSV/schema-shaped), a generated artifact (document, image, code, report), a binary action completed in some external system, or a judgment call with no hard schema (e.g. "quality" or "relevance" assessment). This decides how strict the acceptance criteria below can honestly be.
2. **Draft the price.** If you gave a number, it uses it with the stated unit. If you didn't, it will NOT invent one — it will either compute a cost-basis estimate strictly from numbers you gave, clearly marked `[NEEDS SELLER CONFIRMATION]`, or ask you for one. It will never hand you a guessed price disguised as a real one.
3. **Draft the deliverable spec** — the exact shape of what gets delivered: field names/types for structured output, file format and required sections for an artifact, or the specific state change for an action. This comes only from what you described — it won't add capabilities you never mentioned.
4. **Draft machine-checkable acceptance criteria** as a numbered checklist, each with the specific automated check that would verify it (schema validates, a field is non-empty, a number is in range, the deliverable arrived before the deadline, no error state was returned). Anything that's actually a subjective judgment call gets tagged `[NOT MACHINE-CHECKABLE — requires human/AI-judge review]` instead of being disguised as something a script could check.
5. **Draft an escalation note** — one line on what happens if an automated check fails or a non-machine-checkable item is disputed (route to manual review before any fund release). This prompt never implies it can auto-resolve a dispute itself.
6. **Flag open items** — anything you didn't provide that the listing still needs before it's genuinely escrow-ready (unconfirmed price, vague deliverable format, missing turnaround).
7. Hand back the full listing as one paste-able block. It does not submit or post the listing anywhere — that's on you.

## Output format

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

## Guardrails — what this will never do

- Invent a price you didn't give or derive from numbers you stated. Unconfirmed prices are always marked, never silently guessed.
- Label a subjective, judgment-based criterion as machine-checkable. If a script genuinely can't verify it, the listing says so instead of pretending otherwise.
- Claim to hold funds, run escrow, or resolve disputes. It drafts text; the connected payment rail (Stripe Connect or equivalent) and the marketplace protocol do the actual money-moving.
- Add deliverable fields, capabilities, or claims you didn't state. It only drafts from what you gave it, and flags gaps rather than papering over them with assumptions.
- Guess at a vague service description. If your description doesn't clearly fit one of the four deliverable types, it asks a clarifying question first instead of drafting a listing that doesn't match what you actually sell.

## How to use this with a plain AI chat tool

Paste this entire README into the chat, then paste your service description (the five items under "What to hand over") right after it, and ask for the listing. Any capable chat model can follow the procedure above directly from this text — no special tooling required.
