# Perimeter: A Governance and Provenance Layer for Organizational Agent Memory

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-11-context-engineering-and-memory.md · P10
- **Maturity verdict**: PARTIAL — funded vendors (Supermemory's "Company Brain," SkyBrain, Mem0's Organizational Memory beta) already ship shared org memory, but a Vectorize industry analysis (Oct 2026) concludes "most production company brains are still custom builds today" and names context-graph governance and agent permissioning as unsolved — the specific gap is access control and provenance, not shared memory itself.
- **Format**: BOTH — the permissioning/policy enforcement service is runtime infrastructure; drafting an org's memory-access policy is a one-shot design task.

## The Gap
Hacker News's "Ask HN: Are you building an AI company brain?" (2026-11-05) drew active, unsettled discussion (16 comments on 7 points — high disagreement relative to engagement). The gap-analyst found that while several vendors already ship shared organizational memory, the piece that's genuinely unsolved is *who can read and write what*: existing company-brain products pool institutional knowledge across employees' agents but don't yet solve fine-grained permissioning, provenance (who/what agent contributed a given memory), or redaction for sensitive content before it enters a shared pool.

## The Project
A governance layer that sits in front of existing or custom organizational memory stores (mem0, Zep, a custom vector/graph DB) rather than replacing them: every memory write carries a provenance record (which employee, which agent, which source document) and an access policy (which roles/teams/agents can read it), enforced at query time, with a redaction step for content tagged sensitive (PII, legal, financial) before it's eligible to be surfaced to a broader audience. The policy enforcement and provenance tracking is the centerpiece — a thin layer that makes any existing memory backend auditable and access-controlled, rather than another memory store competing on recall quality.

Components: a provenance-tagged write API (wraps existing memory backends); a role/policy engine for read-time filtering; a redaction pre-processor for sensitive-content detection before storage; an audit log answering "who could see this memory, and who actually did."

## Tangible Impact
**Population**: Mid-size organizations (roughly 50–2,000 employees, per the scale typically cited in company-brain vendor case studies) in compliance-sensitive industries — healthcare, finance, and legal — adopting multiple AI agents across teams, where pooling institutional knowledge without access control creates a real liability (a support agent's memory surfacing a legal team's confidential decision, for example).
**Mechanism**: Today, organizations either avoid shared agent memory to sidestep the liability, or adopt a shared pool with no enforced boundaries between teams; a governance layer lets them get the compounding benefit of shared institutional memory while keeping the same access boundaries their existing role-based systems (e.g., their SSO/RBAC setup) already enforce elsewhere, converting "we can't risk sharing this" into "we can share it to exactly the right audience."
**Measure**: (1) Number of cross-boundary memory leaks (a team's agent surfacing another team's restricted memory) caught in pre-launch red-teaming, driven to zero before go-live. (2) Time for a compliance/security reviewer to audit who could access a given memory, versus no audit trail today. (3) Adoption: organizations willing to turn on org-wide shared memory specifically because the governance layer exists, versus a stated unwillingness without it (survey/pilot interviews).

## Why Now
Multiple funded vendors shipping company-brain features in 2026 without a settled governance answer — and an industry analysis in the same month explicitly naming this as the unresolved piece — means the market has validated demand for shared org memory but not yet solved the part that gates enterprise adoption in regulated industries.

## Skill Angle
Given a description of an organization's teams, data sources, and existing access-control model (e.g., their RBAC/SSO roles), draft a memory-access policy: what categories of memory exist, which roles can read/write each, what triggers redaction, and what provenance metadata should be captured. This is independently useful as a planning/design exercise before any org commits to standing up the enforcement infrastructure.

## MVP Sketch
A thin wrapper API around one existing memory backend (e.g., mem0) that tags every write with a provenance record and enforces a simple role-based read filter defined in a policy file, plus a basic PII/sensitive-content classifier run before writes are accepted. Experiment: simulate 3 teams with different access levels writing and querying a shared memory pool; verify zero cross-boundary leaks occur and measure the added write/query latency from the policy checks. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- Supermemory, Mem0, or SkyBrain could add governance/permissioning to their existing company-brain products directly, which is the most direct competitive risk given they already have the memory layer and the customer relationships.
- Redaction/sensitivity classification is itself an imperfect judgment task; false negatives (missed sensitive content) undermine the entire value proposition.
- The Vectorize analysis notes most company brains today are custom builds — meaning the governance layer may need to integrate with bespoke, non-standard memory backends rather than a clean common API.
- Fine-grained permissioning adds query-time latency and complexity that could make the shared memory feel slower or less useful than an ungoverned pool, creating pressure to loosen policies over time.
