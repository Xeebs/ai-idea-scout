---
name: shared-memory-write-conflict-resolver
description: Drafts a conflict-resolution policy for a multi-agent system's shared/global memory layer — which fact categories auto-resolve by recency or confidence, which escalate to an arbiter agent or a human, and what provenance metadata each decision requires. Use when a team is designing or hardening shared memory for 2+ agents that write to the same fact store, before building (or while reviewing) the enforcement middleware itself.
---

# Shared Memory Write-Conflict Resolver

## When to use this
Reach for this when someone describes a multi-agent setup where two or more agents write facts into one shared/global memory layer (a "scope-chain" global tier, a shared fact table, an org-memory product) and either (a) they've already hit a case where two agents' writes contradicted each other and don't know who should have won, or (b) they're about to build or adopt shared memory and want a written policy before wiring up enforcement. This produces a **policy document a human can review and sign off on** — it does not write code, does not connect to any live memory backend, and does not resolve a conflict happening right now in a running system. If the ask is "here are two contradictory memory values right now, which one is correct" rather than "what should our general rule be," this is the wrong tool — that is a live operational decision, not a policy-drafting task.

## Inputs
**Data source**: Manual — the user describes or pastes their shared-memory setup directly (which agents write to it, what kinds of facts, any past conflict examples, existing write rules). There is no live connector to a memory backend in this skill; the runtime version that intercepts live writes against a backend like a Postgres fact table or Mem0's Organizational Memory (still in private beta as of this writing) is a separate, persistent middleware build — not this skill.

Collect, if not already given, before drafting:
1. **The agents that write to the shared layer** — name and role of each (e.g., "sales-ops agent," "support-triage agent," "research agent"), and roughly what each one writes.
2. **The fact categories stored** — the distinct kinds of facts in the shared layer (e.g., "customer tier," "deal stage," "contact preferred channel," "known outstanding issues"). If the user only has a loose description, ask them to list the 5-15 categories that actually matter rather than drafting against an abstraction.
3. **Any real or hypothetical conflict history** — specific past instances where two writes disagreed (what the two values were, which agents wrote them, how it was discovered or resolved, if at all). If none exist yet, say so explicitly rather than inventing examples — the draft will mark those categories as untested assumptions.
4. **Existing write-authority rules**, if any (e.g., "only the CRM-sync agent may write deal_stage").
5. **Compliance or risk constraints** — any categories where a wrong value has regulatory, financial, or safety consequences (these almost always require human escalation, never pure auto-resolution).

If item 2 (fact categories) is missing entirely, do not draft a policy — ask for it first. A policy with no named categories is not a usable output.

## Procedure
1. **Build the fact-category inventory.** One row per category: name, which agent(s) write it, how often it's written (rough frequency if known), and the cost of a wrong value propagating downstream (low/medium/high, justified in one clause — e.g. "high: a wrong deal_stage triggers an automated discount email").
2. **Separate single-writer categories from multi-writer categories before classifying anything.** A category written by only one agent in the described system has no write-write conflict to resolve — mark its Resolution Tier as "N/A — single writer" and move on; do not force it into AUTO-RESOLVE, ESCALATE, or any other tier just to fill the table. Only categories written by 2+ agents proceed to step 3.
3. **Classify each multi-writer category's conflict-resolution strategy** using this rubric, applied per category, not globally:
   - **AUTO-RESOLVE (recency-only)** — only when the fact is naturally time-decaying and a newer write is always more correct than an older one regardless of source (e.g., "last known location," "current ticket status"), AND the cost of a wrong value is low.
   - **AUTO-RESOLVE (confidence-weighted)** — when sources differ in reliability and that difference is knowable at write time (e.g., a verified-document extraction should outrank an inferred guess); state the specific provenance signals that drive the weighting (source type, agent-reported certainty, document vs. inference).
   - **ESCALATE-TO-ARBITER** — a named agent or role is designated the tie-breaker for this category; use when a clear subject-matter-authoritative agent exists (e.g., the CRM-sync agent is authoritative for deal_stage over an inferring sales agent) but a fully automatic rule would still be too risky to leave unreviewed on first conflict.
   - **ESCALATE-TO-HUMAN** — mandatory whenever cost-of-wrong-value is high, the category is compliance/risk-flagged, or no agent has clear authority. Never downgrade a category the user flagged as compliance-sensitive to an auto-resolve tier, regardless of how clean the data looks.
   - Default when evidence is thin: escalate, not auto-resolve. A category with no conflict history and no stated authority gets ESCALATE-TO-HUMAN with a note that it can be revisited once real conflict data exists — never default to "last write wins" as a silent fallback.
4. **Specify the provenance metadata each category's strategy actually requires to execute** — e.g., confidence-weighted resolution needs a source-type field and a certainty score on every write; arbiter escalation needs the arbiter agent's identity and a way to page it. If the described system doesn't currently capture a required field, flag that as a prerequisite gap, not an assumption.
5. **Write the explicit tie-break rule per multi-writer category** in one sentence each, concrete enough to implement later (e.g., "deal_stage: CRM-sync agent's write is authoritative; a conflicting sales-ops inference is held as proposed and escalated to a human for confirmation, never auto-applied" — not "use judgment").
6. **Define the audit-trail requirement** once, applying to every multi-writer category regardless of tier: what gets logged for every resolution (both competing values, both source agents, timestamps, the tier applied, the final value, and — for escalations — who resolved it and when).
7. **Flag every category where the supplied conflict history contradicts or isn't covered by the drafted rule** — if a past conflict wouldn't have been caught by the proposed strategy, say so explicitly rather than quietly drafting around it. If no conflict history was supplied at all, say that plainly instead of fabricating an illustrative incident and presenting it as reported.
8. **List open questions for human sign-off** — anything the draft had to assume because the input didn't specify it (e.g., "no stated authority for 'company_summary' — defaulted to ESCALATE-TO-HUMAN; confirm or name an arbiter").

## Output format
A single Markdown document with these sections, in order:
1. **Policy Summary** — 2-3 sentences stating what's covered and what isn't (a policy draft, not enforcement).
2. **Fact Category Table** — columns: Category | Writing Agent(s) | Cost if Wrong | Resolution Tier | Tie-Break Rule | Required Provenance Fields. Single-writer categories get a row with Resolution Tier "N/A — single writer" and blank Tie-Break Rule/Provenance columns — include them for completeness, don't omit them, but don't force a conflict strategy onto them either.
3. **Audit Log Schema** — the fixed fields every resolution event must record, as a short bulleted list or code block.
4. **Conflict History Cross-Check** — for each supplied past conflict example, state whether the drafted policy would have resolved it correctly, and if not, what's missing.
5. **Open Questions for Sign-Off** — every assumption made due to missing input, each phrased as a question a human can answer in one line.

## Guardrails
- Never invent conflict history, agent names, or fact categories the user didn't provide — if an example is needed to illustrate a rule, label it clearly as illustrative, not reported.
- Never default a category to "last write wins" or any auto-resolve tier without a stated justification tied to cost-of-wrong-value and source-authority; silent defaults are exactly the failure mode this policy exists to prevent.
- Never mark a category the user identified as compliance/risk-sensitive as anything other than ESCALATE-TO-HUMAN, regardless of how clean its conflict history looks.
- Never present this output as implemented or enforced — it is a draft for human review; always say explicitly that wiring it into a live write-intercept layer is a separate build.
- If the user's description has fewer than 2 distinct writing agents, say this skill doesn't apply — a single-writer system has no write-write conflict to resolve (that's a different problem: validating one agent's own writes over time).
