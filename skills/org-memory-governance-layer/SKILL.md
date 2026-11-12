---
name: org-memory-governance-layer
description: Drafts a memory-access governance policy (categories, role-based read/write matrix, redaction rules, provenance schema, audit checklist) for an organization standing up or auditing shared AI agent memory across teams. Use when a team is about to pool institutional knowledge into a shared memory store (mem0, Zep, a custom vector/graph DB) and needs a concrete access-control design before building the enforcement layer.
---

# Org Memory Governance Layer

## When to use this
Reach for this skill the moment someone is planning to connect multiple teams' AI agents to a shared or org-wide memory store — or is already running one informally and wants to tighten it up before an audit, a compliance review, or a security incident. Signs this is the right moment: "we're giving every team's agent access to the same memory pool," "we need to figure out who can see what before legal signs off," or "a support agent almost surfaced something it shouldn't have." This is a design/planning task, not a coding task — it produces a policy document, not working enforcement code.

Do not use this for a single-team or single-agent memory setup with no cross-boundary sharing — say so and skip the heavy process (see Guardrails).

## Inputs
Ask the user for (or work from what they've already supplied):
1. **Teams/roles** — the list of teams, departments, or job roles whose agents will read or write the shared memory (e.g., Support, Sales, Clinical Ops, Legal, Engineering).
2. **Data sources** — what feeds the memory store: which systems, documents, or conversation logs (e.g., Zendesk tickets, CRM notes, contracts, EHR summaries, Slack threads, internal wiki).
3. **Existing access-control model**, if any — their current RBAC roles, SSO groups, or "nobody has thought about this yet."
4. **Compliance requirements**, if any — HIPAA, SOC2, GDPR, attorney-client privilege, financial confidentiality, or "none that we know of."
5. **Known incidents or close calls** (optional) — any time the wrong team's agent already saw something it shouldn't have.

If any of 1–3 is missing, ask before drafting rather than inventing details.

## Procedure
1. **Inventory memory categories.** Cluster the named data sources into a small number of categories (typically 3–7) by sensitivity and function — e.g., "General/Internal," "Customer Support History," "Sales/CRM," "Legal/Confidential," "Clinical/PHI," "Financial." Assign each a sensitivity tier: `Public`, `Internal`, `Restricted`, or `Confidential`. Base the tier on what the user told you about the source and any compliance requirement named — never invent a tier for a source the user didn't mention.
2. **Build the role-based access matrix.** For every team/role given, decide read and write access per category. Default to least privilege: a role gets read/write on its own category, read-only on "General/Internal," and no access to other teams' Restricted/Confidential categories unless the user explicitly says otherwise. Call out any cross-team exception as a named rule with a reason (e.g., "Clinical Ops gets read-only on Legal's incident-response category during active compliance investigations").
3. **Define redaction triggers.** List the content patterns that must be masked or blocked before a memory entry becomes visible outside its origin team: PII (names, SSNs, emails tied to individuals), PHI, financial figures, attorney-client-privileged language, named third parties. For each trigger, state whether it's a **hard block** (never leaves the originating category) or **mask-and-flag** (redacted version visible, full version logged for authorized review).
4. **Define the provenance schema.** Specify the exact metadata fields every memory write must carry so an audit can reconstruct who could see what and why. Minimum fields: `source_system`, `contributing_team`, `contributing_agent_or_user`, `ingestion_timestamp`, `sensitivity_tier`, `redaction_status`. Add fields the user's compliance requirement demands (e.g., `legal_hold_flag` for litigation contexts).
5. **Define the audit and go-live checklist.** State a review cadence (e.g., quarterly) and a concrete go-live bar: e.g., "zero cross-boundary leaks in a red-team test simulating each role querying every category" plus "a compliance reviewer can produce an access report for any single memory entry in under 5 minutes."
6. **Flag open questions.** List, explicitly, every place the policy is incomplete because the user didn't provide enough information — an undefined team, a data source with unclear sensitivity, no stated compliance regime. Do not silently fill these gaps.

## Output format
A single Markdown document with these sections, in this order:

1. **Memory Categories & Sensitivity Tiers** — table: Category | Description | Sensitivity Tier | Example Sources.
2. **Role-Based Access Matrix** — table: Role | Category | Read | Write | Notes/Exceptions.
3. **Redaction Rules** — bulleted list: Trigger pattern → Hard block or Mask-and-flag → Applies to which categories.
4. **Provenance Schema** — bulleted list of required metadata fields with a one-line description of each.
5. **Audit & Go-Live Checklist** — bulleted checklist with the review cadence and the go-live bar.
6. **Open Questions** — bulleted list of what the user must clarify before this policy is implementation-ready. If nothing is missing, state that explicitly rather than omitting the section.

## Guardrails
- Never invent team names, data sources, or a compliance regime the user didn't state. If information is missing, put it in "Open Questions" instead of guessing.
- Never default to a looser-than-least-privilege access rule without the user explicitly asking for broader sharing.
- Never claim this document provides technical enforcement. State plainly that it is a design artifact — the policy engine, redaction classifier, and audit logging it describes are separate infrastructure that still needs to be built.
- Never certify legal or regulatory compliance ("this is HIPAA compliant"). Say the draft needs sign-off from the organization's own legal/compliance function.
- If the described setup is a single team or single agent with no cross-boundary memory sharing, say the full governance layer is likely unnecessary overhead right now, and offer a two-line lightweight alternative instead of forcing the full six-section output.
