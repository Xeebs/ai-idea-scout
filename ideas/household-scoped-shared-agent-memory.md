# House Rules: An Owner-Scoped, Role-Based Shared Memory Architecture for Household AI Agents

- **Status**: EXPLORING (promoted 2026-11-14 cycle 75: evidence density — 4 independent sources in the digest — Cogitator, zackproser write-up, ZimaSpace blog, ActingWeb Show HN post — all independently converging on the same owner-scoped household-memory gap)
- **Date**: 2026-11-14
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-14-context-engineering-and-memory.md · P4
- **Maturity verdict**: PARTIAL — real but narrow/early implementations exist: Cogitator ships admin/moderator/user roles and private-chat exclusion but is macOS-beta-only with no independent reviews; Mem0's shipped feature is only a binary private/public visibility label per user/agent ID, no role-based access or departure-triggered removal; a Sept 2026 arXiv paper (AIM) describes visibility-labeled memory as research only; Domus Next's "Nori" is in public preview. No mature, widely-adopted, fully-featured implementation closes the gap.
- **Format**: BOTH — the scope-enforcement layer is runtime infrastructure that must stay up between invocations; drafting a household's memory-partition scheme is a one-shot design task.
- **Data Sources**: CONNECTED — the household assistant's existing per-message sender/user-ID metadata (already present in any multi-user chat session a shared agent runs), plus the memory backend's own write/read/delete API (Mem0, Letta, or Zep — all ship mature, documented SDKs for scoped writes and deletion). No new connector needs to be built; this project adds a policy layer on top of calls these backends already expose.

## The Gap
Independent small projects are each re-deriving the same owner-scoping idea from scratch: Cogitator's product page describes one shared household agent instance with "nothing from a private chat enters the shared knowledge base" and departure-triggered data removal; a separate personal-context-engine write-up (zackproser) describes a "database-enforced scope wall" keeping legal/financial/family context out of work-facing agents; a ZimaSpace design essay argues household memory "should be modeled as scoped records with explicit owners and access rules, not one shared transcript"; ActingWeb's Show HN targets the adjacent individual-not-household case. No shared library or widely-adopted product exists — every team is solving the same problem solo.

## The Project
A middleware layer that sits in front of an existing memory backend (Mem0, Letta, or Zep) and enforces household-scoped access instead of a single undifferentiated pool: every write carries an owner tag and a default visibility (shared vs. private), reads are filtered per the querying member's role (admin/adult/teen/guest), and a departure command purges every record tagged to a leaving member in one call. The scope-enforcement and departure-removal workflow is the centerpiece — not another memory store competing on recall quality, but a policy layer any household-facing agent product can drop in front of the backend it already uses.

Components: scope-tagging write wrapper (owner ID, default visibility); a role-based read filter; a departure/removal command with verification; a cross-member leak scanner for pre-launch red-teaming.

## Tangible Impact
**Population**: Households running a shared, always-on AI assistant — the majority of U.S. households (Census Bureau: ~80% of households have more than one person) that adopt a shared smart-speaker or app-based family assistant, specifically multi-person households where at least one member (a partner, a teenager) wants private content (a private chat, search history) to stay private while the same device still handles shared household tasks (a dinner reservation, a grocery list).
**Mechanism**: Today's products either blend every member's input into one profile — risking a partner's private chat or a teen's search history surfacing to the rest of the household — or force each person onto a fully separate assistant, losing the convenience of shared context the household wanted in the first place. An owner-scoped layer lets one shared agent serve the household while mechanically walling off private content and cleanly removing a departing member's data, instead of relying on hope that no one looks.
**Measure**: (1) cross-member leak incidents caught in pre-launch red-team testing, driven to zero before any pilot household goes live. (2) Time to fully remove a departed member's data — target one command, under a minute, versus manual untangling today. (3) Household retention/satisfaction in a pilot, compared against a single-shared-profile baseline product.

## Why Now
Four independent teams (Cogitator, zackproser, ZimaSpace, ActingWeb) converged on the same owner-scoping need within the same research window, and the raw primitives — mature memory-backend SDKs (Mem0, Letta, Zep) and familiar RBAC patterns from SSO systems — are already available to combine; nobody has packaged this as a reusable layer rather than a bespoke, product-specific build.

## Skill Angle
Given a description of a household's members and roles plus a few examples of sensitive vs. shared content types, draft a memory-partition scheme: which categories are shared vs. private by default, what triggers reclassification, and a departure-removal checklist — a one-shot design aid usable before any infrastructure is built.

## MVP Sketch
Wrap Mem0 with owner/visibility tags enforced at read time, plus a CLI `remove-member <id>` command that purges every record tagged to that ID. Experiment: simulate a 3-person household (2 adults + 1 teen); verify a private chat never surfaces to the shared pool, and that a simulated "teen moves out" command fully purges their data on the first try. 3 weeks for 1-2 people.

## Risks & Open Questions
- Cogitator, Mem0, or Domus Next could ship this natively first — they already own the memory layer and the household-product relationship.
- Identifying "who is speaking right now" to apply the correct scope is itself a hard, unsolved sub-problem for voice-first shared devices (speaker ID), and this project assumes it's solvable or already solved upstream.
- Classification of what counts as "sensitive" is an imperfect judgment task; a false negative (missed-private content wrongly shared) undermines the whole value proposition.
- Legal/ethical questions about whose data is whose inside a household (a teen's privacy rights vs. a parent's access expectations) are unresolved and should be checked against real family-law guidance before marketing any privacy claim.
