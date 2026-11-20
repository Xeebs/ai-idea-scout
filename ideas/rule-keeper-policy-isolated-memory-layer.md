# Rule Keeper: A Policy-Isolated Memory Layer That Stops Static Rules From Being Treated as Mutable Preferences

- **Status**: PUBLISHED
- **Date**: 2026-11-20
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-20-context-engineering-memory.md · P1
- **Maturity verdict**: PARTIAL — mature, widely-used tiered-memory frameworks exist (mem0ai/mem0, production-used; Letta/MemGPT's core/archival/recall split; EngramX, GraphMem, ReasoningBank), so "layered memory beyond one window" is well covered in general. But none of them carve out a distinct, write-protected **policy** layer (static CLAUDE.md/AGENTS.md-style rules) that is structurally separate from preference/fact/trace memory — every named framework treats rules, preferences, and facts as the same kind of record differing only by tier/recency, not by mutability class.
- **Format**: BOTH — the storage/enforcement wrapper is PROJECT-shaped (persistent middleware in front of an existing memory backend); auditing an existing memory dump for policy-layer leakage is a separable one-shot judgment task.
- **Data Sources**: CONNECTED — reads the user's existing CLAUDE.md/AGENTS.md-style rules file (already present in their repo, no new upload needed) and wraps their existing memory backend via its native, mature API: mem0's REST/Python API, Letta's REST API, or Zep's SDK. No new external data source is introduced; this sits as an enforcement layer in front of connectors that already exist and are production-grade.

## The Gap
Two independent practitioner sources in the last 30 days (a DataCamp essay and an IndieHackers interview with Sreekanth Ramakrishnan) independently argue that "give the model everything we have" is the wrong default and propose splitting agent memory into policy, preference, fact, and trace layers instead of one undifferentiated store. The gap-analyst confirmed every major open-source memory framework already does *some* tiering (recency, archival vs. working, scope), but none treats a static policy rule as a structurally distinct, write-protected class from a learned preference or an extracted fact — so a rule like "never commit directly to main" lives in the same kind of record as "user prefers terse commit messages," and nothing stops a relevance-scored eviction or a write from one layer silently clobbering the other.

## The Project
A thin enforcement layer that sits in front of an existing memory backend (mem0, Letta, or a flat file store) and classifies every memory record into one of four typed buckets at write time: **policy** (parsed from CLAUDE.md/AGENTS.md, immutable except by an explicit human edit to the source file — never written by the agent itself), **preference** (mutable, agent-writable, versioned), **fact** (mutable, agent-writable, provenance-tagged), and **trace** (append-only, eligible for eviction/summarization). The centerpiece is the write-path guard: any agent-initiated write or automatic compaction pass that targets the policy bucket is rejected outright, and any read-path merge that would let a preference override a policy rule in the assembled context is flagged before it reaches the prompt.

Components: a classifier that tags incoming writes by source (file-parsed vs. agent-generated) and target bucket; a write-guard enforcing policy immutability; a context-assembly step that always places policy entries last-written (anti-recency-bias) and conflict-checks preference/fact entries against them; adapters for mem0 and Letta's existing APIs.

## Tangible Impact
**Population**: Teams already running production agent memory on mem0 or Letta/MemGPT — per the digest's own gap-analyst verdict, both are production-used/widely-adopted frameworks — who also maintain a static CLAUDE.md/AGENTS.md rules file alongside that memory store. This is the specific, growing overlap of "has a tiered memory backend" and "has static rules" rather than either population alone.
**Mechanism**: Today a static rule and a learned preference are stored and evicted by the same relevance/recency logic, so a policy constraint can be summarized away during compaction or quietly outranked by a more-recently-reinforced preference; a structurally separate, write-protected policy bucket means the rule is never a candidate for eviction and never loses a merge conflict to a preference, converting a silent policy violation into an impossible write.
**Measure**: (1) Count of "agent violated a documented rule it had previously followed" incidents per long session, before vs. after. (2) Rate of policy-bucket writes rejected by the guard (confirms the failure mode is real and being caught, not just theorized). (3) Context-assembly latency overhead of the classification/guard step versus unguarded memory assembly.

## Why Now
Two independent "context ≠ memory" essays converging on the same four-layer split within the last 30 days, combined with mem0/Letta already being production infrastructure that teams won't want to rip out, makes a thin compatibility-layer wrapper — rather than a new memory store from scratch — the first viable version of this idea.

## Skill Angle
Given a pasted CLAUDE.md/AGENTS.md file plus a dump or export of an agent's accumulated memory entries (mem0/Letta export, or a flat log), classify each entry into policy/preference/fact/trace and flag any entry that looks like it should be policy-immutable but was written by the agent itself (a leak), or any preference/fact that contradicts a stated policy rule. Useful standalone as a one-time audit before adopting the full enforcement layer.

## MVP Sketch
A classifier (rule-based: parse CLAUDE.md for policy entries; everything else tagged by write-source) plus a write-guard wrapping mem0's Python SDK, and a CLI that runs the classification audit on an existing memory export. Experiment: take 2-3 teams' real CLAUDE.md + mem0 history, run the audit, and count how many existing entries are misclassified leaks (policy content an agent wrote, or preference content contradicting a stated rule) — if the count is near zero across real data, the gap may be smaller in practice than the conceptual essays suggest. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- The conceptual essays are opinion pieces, not measured failure data — the MVP's own audit step is the first real test of whether policy-layer leakage happens often enough in practice to justify the guard.
- mem0 or Letta could ship a native "immutable policy tier" feature directly, absorbing this as a wrapper is no longer needed.
- Parsing CLAUDE.md/AGENTS.md into discrete, checkable policy rules (vs. free-text prose) is itself a non-trivial NLP step that could introduce false "policy" classifications.
- The anti-recency-bias context-assembly change could itself introduce new context-budget pressure if policy entries accumulate without their own pruning discipline (which, by design, they're exempt from).
