# Org Memory Governance Layer — Policy Drafting Prompt

A self-contained prompt for drafting an access-control and provenance policy for a shared AI agent memory store (the kind of system that pools institutional knowledge across teams via mem0, Zep, a custom vector/graph database, or similar). Paste this whole document into any AI chat tool along with your organization's details, and it will produce a governance policy document — not code, a design artifact you hand to whoever builds or audits the enforcement layer.

## When to use this

Use this when your organization is about to connect multiple teams' AI agents to a shared memory pool — or already has one running informally — and you need to answer "who can read and write what, and how would we prove that in an audit?" before legal, security, or compliance will sign off. This is the right moment if you've heard (or said) something like: "we're giving every team's agent access to the same memory," "we need an access policy before this goes live," or "a support agent almost surfaced something it shouldn't have seen."

This is not the right tool if you have a single team or a single agent with no cross-team memory sharing — see the note on that at the end.

## What to hand over

Before using this prompt, gather:

1. **Teams/roles** that will have agents reading or writing the shared memory (e.g., Support, Sales, Clinical Ops, Legal, Engineering, Finance).
2. **Data sources** feeding the memory — which systems, documents, or logs (e.g., support tickets, CRM notes, contracts, patient records, Slack threads, internal wiki pages).
3. **Existing access-control model**, if you have one — current RBAC roles or SSO groups, or "we haven't set this up yet."
4. **Compliance requirements**, if any — HIPAA, SOC2, GDPR, attorney-client privilege, financial confidentiality rules, or "none that we're aware of."
5. **Known incidents or close calls** (optional) — any time the wrong team's agent already saw something it shouldn't have.

If you're missing any of items 1–3, the model should ask you for it rather than guess — don't let it invent organizational details you haven't actually given it.

## The prompt

Copy everything below the line into your AI chat tool, then fill in the bracketed sections with your own organization's details.

---

You are drafting a memory-access governance policy for an organization that is pooling institutional knowledge into a shared AI agent memory store. Follow this procedure exactly and produce the output format specified below.

**My organization's details:**
- Teams/roles with agents that will read or write shared memory: [list them]
- Data sources feeding the memory store: [list systems/documents/logs]
- Existing access-control model (RBAC roles, SSO groups, or "none yet"): [describe]
- Compliance requirements (HIPAA, SOC2, GDPR, privilege, financial confidentiality, or "none known"): [describe]
- Known incidents or close calls (optional): [describe or omit]

**Your procedure:**
1. Inventory memory categories: cluster my data sources into 3–7 categories by sensitivity and function (e.g., "General/Internal," "Customer Support History," "Legal/Confidential," "Clinical/PHI"), and assign each a sensitivity tier — Public, Internal, Restricted, or Confidential — based only on what I told you. Don't invent a category or tier for a source I didn't mention.
2. Build a role-based access matrix: for every team/role I gave you, decide read and write access per category, defaulting to least privilege — a role gets full access to its own category, read-only on General/Internal, and no access to other teams' Restricted/Confidential categories unless I explicitly said otherwise. Name any cross-team exception explicitly, with a reason.
3. Define redaction triggers: list content patterns that must be masked or blocked before a memory entry is visible outside its origin team (PII, PHI, financial figures, privileged legal language, named third parties), and for each state whether it's a hard block (never leaves the originating category) or mask-and-flag (redacted version visible, full version logged for authorized review).
4. Define a provenance metadata schema: the exact fields every memory write must carry — at minimum source_system, contributing_team, contributing_agent_or_user, ingestion_timestamp, sensitivity_tier, redaction_status — plus any field my stated compliance requirement demands.
5. Define an audit and go-live checklist: a review cadence (e.g., quarterly) and a concrete go-live bar (e.g., zero cross-boundary leaks in a red-team test where every role queries every category; a compliance reviewer can produce an access report for any single memory entry within a set time).
6. List open questions: every place the policy is incomplete because I didn't give you enough information — an undefined team, an ambiguous data source, no stated compliance regime. Don't fill these gaps yourself.

**Produce your output as a single Markdown document with these six sections, in this order:**
1. Memory Categories & Sensitivity Tiers (table: Category | Description | Sensitivity Tier | Example Sources)
2. Role-Based Access Matrix (table: Role | Category | Read | Write | Notes/Exceptions)
3. Redaction Rules (bulleted: Trigger → Hard block or Mask-and-flag → Applies to which categories)
4. Provenance Schema (bulleted list of required fields with one-line descriptions)
5. Audit & Go-Live Checklist (bulleted, with cadence and go-live bar)
6. Open Questions (bulleted; if nothing is missing, say so explicitly)

**Rules you must follow:**
- Never invent team names, data sources, or a compliance regime I didn't state — put gaps in Open Questions instead.
- Never default to looser-than-least-privilege access without me explicitly asking for broader sharing.
- Never claim this document is itself technical enforcement — it is a design artifact. The policy engine, redaction classifier, and audit logging it describes are separate infrastructure that still needs to be built.
- Never certify legal or regulatory compliance (e.g., "this is HIPAA compliant") — say the draft needs sign-off from my organization's own legal/compliance function.
- If my setup is a single team or single agent with no cross-boundary memory sharing, tell me the full governance layer is likely unnecessary overhead right now, and give me a two-line lightweight alternative instead of the full six-section output.

---

## What you get

A policy document you can hand to whoever is building or auditing your shared memory system: a categorized sensitivity map, a concrete role-by-category access matrix, explicit redaction rules, the metadata every memory entry needs to carry, and a checklist for when it's actually safe to go live — plus an honest list of what you still need to decide before this is implementation-ready.

## What this is not

This does not write the enforcement code, the policy engine, or the redaction classifier — it designs the policy those systems would implement. It also does not certify compliance with any regulation; a human from your legal/compliance function still has to sign off. If you're running a single team or single agent with no memory shared across boundaries, skip this — the lightweight note the prompt gives you in that case is enough.
