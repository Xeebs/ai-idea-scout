# Voice Agent Memory Retention & Redaction Policy Drafter

A paste-anywhere prompt for drafting a retention schedule and redaction ruleset before you ship caller/cross-call memory on a voice agent — Vapi, Retell, Pipecat, Mem0, or a bespoke Redis/Postgres pair. It doesn't matter which backend you're building on: the policy question ("what do we remember, for how long, and what can never be stored verbatim") is the same, and almost every team skips writing it down before shipping memory.

## When to use this

You're adding (or already shipped) a feature where your voice agent recalls something about a repeat caller on their next call — last appointment, a stated complaint, a preference, a promise-to-pay amount. Before (or shortly after) that ships, you need a concrete answer to: which fields get kept, for how long, in what form, and what happens when a caller asks you to forget them. This produces that document. It does not scan real calls or write any code — it's a policy draft for your team (and your legal/compliance reviewer) to adopt or revise.

## What to hand over

This only ever needs field *names*, never real caller data. Give the assistant:

1. **The list of fields you intend to remember about callers** — plain labels, not real values. Example: "caller name, phone number, last appointment type and date, stated allergies, billing complaints, preferred callback time."
2. **Your platform/stack**, if known — Vapi, Retell, Pipecat, or a custom build. (Doesn't block the exercise if you don't know yet.)
3. **Your callers' primary jurisdiction(s)** — e.g., "US, no specific state," "EU," "California," or "not sure yet."
4. **Your industry/use case in one line** — e.g., "dental scheduling," "debt collection follow-up," "general customer support." This determines which sensitive-data flags apply.

Important: if you catch yourself about to paste an actual caller's name, phone number, or a real transcript snippet instead of a field label, stop — replace it with the generic field name first. This exercise never needs or wants real caller data, and the assistant should refuse and ask you to redact it if you paste it by mistake.

## What the assistant should do

Paste this whole section (or just point the assistant at this file) along with your answers to the four items above, and ask it to:

1. **State the scope up front, every time**: this produces a *draft* policy for human/legal review — not a compliance certification — and it never touches real caller data.
2. **Classify every field** you listed into one of: `Identity` (name, phone/caller ID, account number), `Transactional` (appointment ID, order number, call outcome), `Behavioral` (stated preference, sentiment, requested callback time), or `Sensitive/Special-category` (health conditions, financial hardship amounts, anything protected-class-adjacent, or generally anything that would count as "special category data" under GDPR Art. 9 or an equivalent sensitive-data law). Ambiguous fields (e.g., a generic "notes" field) should prompt a clarifying question rather than a guess.
3. **Draft a retention-schedule row per field**: a default retention window, what event triggers deletion, the stated legal/business reason for keeping it that long, and whether it's stored verbatim, summarized, or as a redacted pattern only. Defaults to use unless you give a reason to extend: Identity/Transactional fields → 90 days; Sensitive/Special-category fields → 30 days, and always flagged for extra scrutiny regardless of window length.
4. **Draft a redaction ruleset**: for each field or pattern, decide `Never store verbatim` (full SSNs, full card numbers, full date of birth, an exact dollar figure tied to a named sensitive condition), `Store redacted/summarized` (e.g., "mentioned financial hardship" rather than the amount and reason verbatim; "has a food allergy" rather than the full sentence a caller used), or `Store as-is` (low-risk operational fields like appointment type). A Sensitive/Special-category field should never default to "store as-is."
5. **Flag jurisdiction-specific obligations** based on what you stated: EU/UK callers → GDPR right-to-erasure and a documented legal basis per field; a named US state with its own privacy law (e.g., California) → the specific erasure/opt-out mechanism by name; health-adjacent fields anywhere → a HIPAA-adjacency flag with an explicit "this needs a legal check" note rather than a claim either way; if you said jurisdiction is unknown, the assistant should default to the stricter GDPR-style baseline and say plainly that this is a conservative placeholder, not a legal determination.
6. **Call out compounding risk**: any combination of an identity field with a sensitive field (e.g., name + health complaint, phone number + financial hardship amount) should be flagged explicitly, even when each field looked minor on its own.
7. **Deliver the output in this exact structure**:
   - **Retention Schedule** — a table: Field | Category | Retention Window | Deletion Trigger | Legal/Business Basis | Storage Form
   - **Redaction Ruleset** — a table: Field/Pattern | Action (Never Store / Store Redacted / Store As-Is) | Rationale
   - **Jurisdiction & Compliance Flags** — one bullet per applicable jurisdiction/regulation, naming the specific mechanism (e.g., "GDPR Art. 17 — must support an erasure request; recommend handling within 30 days")
   - **Compounding-Risk Call-Outs** — bulleted ("None identified" is fine if genuinely none)
   - **Pre-Launch Checklist** — 4–6 bullets: a call-opening disclosure line that memory is being kept, an erasure-request handling process, audit logging of what was read/written per call, and a scheduled review date for the policy itself
   - A closing one-line disclaimer that this is a drafting aid for legal/compliance review, not a certification

## Guardrails — tell the assistant to follow these strictly

- Never accept or act on real caller data — names, numbers, transcripts. If any appears, stop and ask for the field label instead.
- Never claim a retention window or redaction rule "is compliant" with a named law. Always frame it as a draft needing legal sign-off, even for a clearly stated jurisdiction.
- Never default a sensitive field to "store as-is" or to more than 30 days' retention without an explicit business reason you provided.
- Never silently assume a jurisdiction when you haven't stated one — it should ask once, then fall back to the conservative GDPR-style default and say so if you still don't know.
- Never produce integration code, webhook configs, or a database schema in this exercise — that's a separate, implementation-level task; this is policy text only.

## Example

**You provide**: "Fields: caller name, phone number, last appointment type and date, stated allergies, billing complaints. Platform: Vapi. Jurisdiction: US, no specific state given. Use case: dental scheduling."

**You should get back**: a Retention Schedule table marking "stated allergies" as Sensitive/Special-category with a 30-day window and a HIPAA-adjacency flag, "caller name" and "phone number" as Identity at 90 days, a Redaction Ruleset marking allergy details as "Store redacted/summarized" (category only, not the caller's exact wording), a Jurisdiction flag noting no state-specific law was named so a conservative baseline was applied, a Compounding-Risk call-out on name + allergy together, and a Pre-Launch Checklist including a disclosure line and an erasure process — closing with the legal-review disclaimer.
