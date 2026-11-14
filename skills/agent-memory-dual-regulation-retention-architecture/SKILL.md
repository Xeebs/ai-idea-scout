---
name: agent-memory-dual-regulation-retention-architecture
description: Drafts a working-memory vs. decision-record classification map and tiered retention policy for an agent's memory store, so a team can honor a GDPR Article 17 erasure request without destroying the EU AI Act Article 12 decision records they're legally required to keep. Use when a team is designing or auditing memory retention for a memory-enabled agent that makes high-risk-adjacent decisions (credit, hiring, benefits, etc.) in an EU-market deployment.
---

# Agent Memory Dual-Regulation Retention Architecture

## When to use this
Reach for this skill the moment a team hits (or anticipates) the collision between two EU obligations on the same memory store:

- **GDPR Article 17** — a data subject has requested erasure of their personal data, and the agent's memory system holds conversational/embedding content about them.
- **EU AI Act Article 12** — the same agent is "high-risk" (it makes or materially informs a credit, hiring, benefits-eligibility, or similarly consequential recommendation about a person) and is legally required to keep records of the decision logic, inputs, and model version for a retention period.

Typical trigger phrasings: "we got a GDPR erasure request and I don't know if we can honor it without breaking our AI Act logging," "we're about to launch a memory-enabled agent in the EU and need a retention policy before legal signs off," "our memory backend (Mem0/Letta/Zep) doesn't tell us what's safe to delete." If the agent in question is not high-risk under the AI Act and has no EU exposure, this skill is overkill — a plain TTL on all memory is sufficient and this skill should say so rather than force the framework.

## Inputs
**Data source**: Connected — the parent idea classifies this as Connected: the team's existing memory-backend API (Mem0, Letta, or Zep — all mature, documented write/read/delete APIs) plus whatever trace/event store the agent framework already emits (OTel GenAI spans, or the framework's own tool-call log). In Claude Code, with repo access, that means: **read the actual integration code** — the files that call `.add()`/`.insert()`/memory-write methods, the schema/config for those calls, and a sample of real trace/log entries — directly with the Read/Grep tools, rather than asking the user to re-describe their architecture from memory. Do not substitute a free-text prose summary for this when the code is available; the classification must trace to real write sites, not a guess.

If this skill is being run from a plain chat tool with no file access (the portable README version), the user must paste the *actual* artifacts instead of a verbal description: the memory-write call sites (code or config), the schema/fields stored per write, and a few representative trace/log entries showing what each write actually contains. A paragraph like "we store conversations and some decisions" is not sufficient input — ask for the real snippets before classifying anything.

Also required, and this cannot be inferred from code alone: which action categories the agent performs are **high-risk under the EU AI Act** (e.g., Annex III categories — credit scoring, employment/recruitment, benefits eligibility, biometric ID, etc.). If the user hasn't stated this, ask before classifying — do not assume.

## Procedure
1. **Enumerate every memory write site.** From the connected code/config (or pasted snippets), list each distinct place the agent writes to memory: what triggers the write, what data it contains, and which user-facing feature it supports. Do not invent write sites that aren't evidenced in the code/traces/pasted artifacts.
2. **Confirm the high-risk action categories** with the user if not already stated. Do not guess whether an action is "high-risk" under the AI Act — this is a factual/legal determination the user or their counsel must supply or confirm.
3. **Classify each write site** as one of:
   - **Working memory** — ordinary conversational, exploratory, or session content with no causal link to a high-risk action. Erasable on request; expires on a bounded TTL.
   - **Decision record** — the structured reasoning, inputs, or policy basis behind an action gated by a confirmed high-risk category. Must be retained per Art. 12 regardless of a later erasure request, with personally-identifying conversational content stripped where feasible so the rationale, timestamp, and model version survive intact.
   - **Ambiguous / needs counsel review** — any write site where the line between the two isn't clear from the evidence (e.g., content that informs a high-risk decision but isn't itself the decision rationale). Never force these into working-memory or decision-record silently — flag them explicitly.
4. **Draft the retention policy per category**: a TTL for each working-memory category (ask the user for their existing policy/jurisdictional default; if none exists, mark as "TBD — needs a stated default, do not assume 30/90 days without confirmation") and the survive/redact-on-erasure rule for each decision-record category (what gets stripped — direct identifiers, free text — versus what must survive: decision rationale, timestamp, model version, input summary).
5. **Map each category to its legal basis** — cite GDPR Art. 17 for erasable categories and AI Act Art. 12 for retained categories, in plain language, not as a legal conclusion ("this satisfies Art. 12" is not something this skill can assert — "this targets the Art. 12 record-keeping requirement; confirm with counsel" is the correct framing).
6. **Propose a deletion-audit-log schema**: the fields that should be written on every erasure request to prove, after the fact, exactly what was deleted/redacted and what was retained and why (request timestamp, category classification at time of request, fields stripped, fields retained, retained-record legal basis, operator/system identity).
7. **Write the handoff note**: this skill determines *what* should and shouldn't be deletable. It does not execute deletion or prove physical purge from a vector store — that is a separate concern (e.g., an erasure-verification pipeline). State this boundary explicitly in the output.

## Output format
A single Markdown report with these sections, in this order:

1. **Classification Map** — table: `Write Site | Trigger | Example Content | Classification | Confidence`. Confidence is `Confirmed` or `Needs counsel review`.
2. **Retention Policy** — table: `Category | Retention Rule | On-Erasure-Request Behavior | Legal Basis`.
3. **Open Legal Questions** — bullet list of every ambiguous write site, stating exactly why it's ambiguous (never silently resolved).
4. **Deletion Audit Log Schema** — field list with a one-line purpose per field.
5. **Handoff Note** — one paragraph stating this is a design artifact for engineering + legal to review together, not a compliance certification, and naming the downstream step (deletion execution / physical-purge proof) this does not cover.

## Guardrails
- Never classify a write site that wasn't evidenced in actual code, config, trace, or pasted artifacts — no inventing categories from a generic mental model of "what agents usually store."
- Never assert that a classification or retention duration is legally correct or AI-Act-compliant. The output drafts a defensible structure for counsel to review; it is never a legal opinion or a compliance certification.
- Never silently resolve an ambiguous write site into "working memory" (the easy, erasure-friendly answer) or "decision record" (the easy, retention-safe answer) — always surface it in Open Legal Questions instead.
- Never invent a specific retention duration (e.g., "retain for 6 years") without the user supplying a jurisdictional or policy basis for it — mark as TBD instead.
- Never propose or execute an actual deletion, redaction, or data migration — this skill produces a policy design and an audit-log schema, not a destructive operation.
- Never treat this as covering physical/vector-store purge verification — that is explicitly out of scope and must be named in the Handoff Note.
