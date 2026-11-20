# Rule Keeper: A Policy-Isolated Memory Layer That Stops Static Rules From Being Treated as Mutable Preferences

Ask most teams running a production agent memory stack whether their CLAUDE.md rules can get silently evicted during a context compaction pass, and they'll say no, of course not — rules are different from preferences. Then ask them to point to the code that enforces that difference. Usually there isn't any. The rule and the preference sit in the same memory store, scored by the same recency and relevance logic, evictable by the same compaction pass. Nothing in the pipeline actually knows one is a static policy and the other is a guess the agent made about what you like.

## The Gap

In the last 30 days, two practitioners independently arrived at the same conclusion from different directions. A DataCamp essay on context engineering argued that "give the model everything we have" is the wrong default and proposed splitting agent memory into policy, preference, fact, and trace layers. An IndieHackers interview with Sreekanth Ramakrishnan made the identical "context ≠ memory" argument, unprompted by the first. Two independent threads converging on the same four-way split in one month is the kind of signal that's easy to miss if you're only watching for new tools, because neither source shipped one — they just named a distinction that the tooling hasn't caught up to.

That tooling gap is real, not assumed. The mature, widely-used memory frameworks — mem0, Letta/MemGPT, and a handful of others — already tier memory by recency, scope, or archival-vs-working status. What none of them do is treat a static policy rule ("never commit directly to main") as a structurally different *class* of record from a learned preference ("user prefers terse commit messages"). Today both live in the same kind of entry, differing only by tier, which means a relevance-scored eviction or a careless write from one layer can clobber the other — silently, because nothing is watching for it.

## The Project

Rule Keeper is a thin enforcement layer that sits in front of an existing memory backend — mem0, Letta, or a flat file store — and classifies every record into one of four typed buckets at write time. **Policy** entries, parsed from CLAUDE.md/AGENTS.md, are immutable except by a human editing the source file directly; the agent itself can never write to this bucket. **Preference** and **fact** entries stay mutable and agent-writable, with facts carrying provenance tags. **Trace** entries are append-only and the only ones eligible for eviction or summarization.

The centerpiece isn't the taxonomy — it's the write-path guard. Any agent-initiated write or automatic compaction pass that targets the policy bucket gets rejected outright. Any read-path context assembly that would let a preference quietly override a policy rule gets flagged before it ever reaches the prompt. The rest is adapter work: a classifier that tags incoming writes by source (file-parsed vs. agent-generated) and target bucket, and a context-assembly step that places policy entries last-written to defeat recency bias, checking preference/fact entries against them for conflicts.

Because this wraps mem0's and Letta's existing, mature APIs rather than replacing them, teams don't have to rip out infrastructure they already trust — they bolt on a guardrail.

## Tangible Impact

**Population**: Teams already running production agent memory on mem0 or Letta/MemGPT — both are production-used, widely-adopted frameworks per the underlying research — who also maintain a static CLAUDE.md/AGENTS.md rules file alongside that memory store. This is the specific, growing overlap of "has a tiered memory backend" and "has static rules," not either population alone.

**Mechanism**: Today a static rule and a learned preference are stored and evicted by the same relevance/recency logic, so a policy constraint can be summarized away during compaction or quietly outranked by a more-recently-reinforced preference. A structurally separate, write-protected policy bucket means the rule is never a candidate for eviction and never loses a merge conflict to a preference — turning a silent policy violation into an impossible write.

**Measure**: (1) Count of "agent violated a documented rule it had previously followed" incidents per long session, before vs. after. (2) Rate of policy-bucket writes rejected by the guard — confirming the failure mode is real and actually being caught, not just theorized. (3) Context-assembly latency overhead of the classification/guard step versus unguarded memory assembly.

## Why Now

Two independent "context ≠ memory" essays converged on the same four-layer split within a single month, and mem0/Letta are already production infrastructure teams have no appetite to replace. That combination is what makes a thin compatibility-layer wrapper — rather than a new memory store built from scratch — the first viable version of this idea, rather than a research exercise.

## The Honest Risks

This idea earns a PARTIAL maturity verdict, not OPEN, and it's worth being direct about why. The conceptual essays behind it are opinion pieces, not measured failure data — the project's own MVP audit step is the first real test of whether policy-layer leakage happens often enough in practice to justify building a guard for it at all. It's entirely possible mem0 or Letta ships a native "immutable policy tier" feature directly, which would absorb this wrapper's entire reason to exist. And parsing CLAUDE.md/AGENTS.md into discrete, checkable policy rules — rather than free-text prose — is itself a non-trivial step that could introduce its own false-positive "policy" classifications. None of these sink the idea, but anyone building this should treat the audit phase as a real kill switch, not a formality.

---

Surfaced from `research/2026-11-20-context-engineering-memory.md`, pattern `P1`.
