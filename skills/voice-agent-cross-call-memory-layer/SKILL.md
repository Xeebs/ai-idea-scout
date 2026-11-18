---
name: voice-agent-cross-call-memory-layer
description: Drafts a field-by-field retention schedule and redaction ruleset for a voice agent's caller/cross-call memory before it ships, flagging sensitive-category fields and jurisdiction-specific erasure obligations. Use when a builder is about to add caller memory (Vapi, Retell, Pipecat, or custom telephony stack) and needs to decide what to remember, for how long, and what must never be stored verbatim — not for live PII detection or real-time call processing.
---

# Voice Agent Memory Retention & Redaction Policy Drafter

## When to use this
A builder is adding (or already has) a cross-call memory feature to a voice agent — the thing that lets the agent recall a repeat caller's prior appointment, complaint, or preference on the next call — and needs a written retention/redaction policy before shipping it, during a privacy review, or after an incident where the memory store held something it shouldn't have. This applies whether the memory is built on Vapi/Retell webhooks, Pipecat, Mem0, or a bespoke Redis/Postgres pair — the policy question is the same regardless of backend.

This is a **policy-drafting exercise**, not a live redaction pipeline. It does not touch real call data, does not run NER/regex against live transcripts, and does not replace legal sign-off.

## Inputs
**Data source**: Manual — the user describes, in plain text, the list of fields they intend to remember about a caller (e.g., "name, phone number, last appointment type, stated allergies, billing complaints") plus context about jurisdiction and industry. No connector, call recording, or live transcript access is used. (Note: the parent project this skill accompanies reads/writes actual caller memory via the Vapi/Retell webhook APIs — that connector is mature today — but this skill itself only ever sees a human-written field list, never real caller data, because it produces the policy that governs that connector, not a call against it.)

Required from the user:
1. The list of fields intended to be remembered about callers (plain names, not real values).
2. The platform/stack in use, if known (Vapi, Retell, Pipecat, custom) — affects what's already configurable at the platform layer vs. needs custom handling.
3. Primary jurisdiction(s) of the callers (e.g., "US, no specific state," "EU," "California," "unknown").
4. Industry/use case in one line (e.g., "dental scheduling," "debt collection follow-up," "general customer support") — this determines which sensitive-category flags apply.

**Guardrail on input**: if the user pastes an actual caller transcript, a real name, phone number, or any other real identifying value instead of a field *name*, stop and ask them to replace it with the generic field label before continuing. This skill never processes real caller data.

## Procedure
1. **Confirm scope out loud, every time, before producing output**: state that this produces a draft policy for human/legal review, not a compliance certification, and that it never touches real caller data.
2. **Classify each submitted field** into one of: `Identity` (name, phone/ANI, account/caller ID), `Transactional` (appointment ID, order number, call outcome), `Behavioral` (stated preference, sentiment, callback time), `Sensitive/Special-category` (health condition, financial hardship amount, protected-class-adjacent statement, anything that would be "special category data" under GDPR Art. 9 or similarly sensitive under a US state law). If a field is ambiguous (e.g., "notes"), ask what it typically contains rather than guessing a category.
3. **Draft a retention schedule row per field**: default retention window, the event that triggers deletion (e.g., "90 days after last contact" or "on service completion + 30 days"), the stated legal/business basis for keeping it that long, and the storage form (verbatim, summarized, or redacted-pattern-only). Default windows: Identity/Transactional → 90 days unless the user states a business reason for longer; Sensitive/Special-category → 30 days unless the user justifies longer, and always flagged for extra review regardless of window.
4. **Draft a redaction ruleset**: for each field or field-pattern, classify as `Never store verbatim` (SSNs, full card numbers, full DOB, exact dollar amounts tied to a named sensitive condition), `Store redacted/summarized` (e.g., "mentioned financial hardship" instead of the dollar figure and reason verbatim; "stated allergy: category only" instead of a full medical sentence), or `Store as-is` (low-risk operational fields like appointment type or preferred callback time). Never default a Sensitive/Special-category field to `Store as-is`.
5. **Apply jurisdiction flags** based on what the user stated: EU/UK callers → note GDPR right-to-erasure and the need for a documented legal basis per field; any US state the user names with its own law (e.g., California/CCPA-CPRA) → note the specific erasure/opt-out mechanism by name; health-adjacent fields in any jurisdiction → flag HIPAA-adjacency even if the business likely isn't a covered entity, and say explicitly that this needs a legal check rather than asserting coverage either way; unknown/unstated jurisdiction → default to the GDPR-style baseline (shortest reasonable retention, explicit erasure path) and say plainly that this is a conservative default pending clarification, not a determination of what law actually applies.
6. **Call out compounding risk**: if the field set combines an identity field with a sensitive field (e.g., name + health complaint, phone number + financial hardship amount), flag that combination explicitly as elevated risk even if each field alone seemed minor.
7. **Produce the output** (format below) plus a one-line disclaimer that this is a drafting aid, not a legal opinion, and must be reviewed by the team's legal/compliance function before being adopted as policy.

## Output format
A single markdown response with these sections, in order:

1. **Retention Schedule** — table: `Field | Category | Retention Window | Deletion Trigger | Legal/Business Basis | Storage Form`
2. **Redaction Ruleset** — table: `Field/Pattern | Action (Never Store / Store Redacted / Store As-Is) | Rationale`
3. **Jurisdiction & Compliance Flags** — bulleted, one bullet per jurisdiction or regulation that applies, naming the specific mechanism (e.g., "GDPR Art. 17 — must support a caller erasure request; recommend a documented process for this within 30 days of request").
4. **Compounding-Risk Call-Outs** — bulleted; empty/"None identified" is a valid result if genuinely none exist, but don't skip the section.
5. **Pre-Launch Checklist** — 4–6 bullets covering: call-opening disclosure line about memory being kept, erasure-request handling process, audit logging of what was read/written per call, and a review date for the policy itself.
6. One-line disclaimer: this is a drafting aid for human/legal review, not a compliance certification.

## Guardrails
- Never accept, request, or process real caller data (names, numbers, transcripts) — only field *labels*. If real data appears in the input, stop and ask for it to be replaced before continuing.
- Never assert that a given retention window or redaction choice "is compliant" with a named law — always frame it as a draft starting point requiring legal review, even when a jurisdiction is clearly stated.
- Never default a Sensitive/Special-category field to `Store as-is` or to a retention window longer than 30 days without an explicit business justification the user supplies.
- Never silently pick a jurisdiction when the user hasn't stated one — ask once; if still unknown, use the conservative GDPR-style default and say so explicitly rather than treating it as a real determination.
- Never produce integration code, webhook configs, or database schemas — this skill outputs policy text only; implementation is a separate task.
