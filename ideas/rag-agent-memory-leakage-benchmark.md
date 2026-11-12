# MemLeak Bench: Separating Retrieval Leakage from Agent-Memory Leakage

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P8
- **Maturity verdict**: PARTIAL — `gh repo view harishbalasubramanian/sentinel-eval` confirms only 2 stars, pushed 2026-11-09, a brand-new narrow implementation. WebSearch found academic papers treating agent-memory leakage alone (PersistBench, CIPL, Entity-Collision, MEMPROBE) but explicitly found no single benchmark evaluating both RAG-retrieval and agent-memory leakage together.
- **Format**: BOTH

## The Gap

Hacker News's "Show HN: Raw RAG leaks 0%, but agent memory leaks 67%" (2026-11-09, 3 pts, github.com/harishbalasubramanian/sentinel-eval) demonstrated the two failure classes behave completely differently in practice, yet almost no tooling treats them as distinct — the single new repo introducing the split has only 2 stars, and existing agent-memory-leakage research doesn't pair with RAG-retrieval leakage in one evaluation.

## The Project

An open benchmark plus a lightweight instrumentation library that separately measures two leakage classes in agent systems that combine document RAG with persisted agent memory: (1) retrieval leakage — a document chunk the querying user shouldn't have access to gets retrieved, and (2) memory leakage — information written to the agent's own memory store (from a different user or session) resurfaces inappropriately. Each class gets its own test harness, its own metric, and its own remediation guidance, so teams fix the layer that's actually broken instead of patching retrieval access control when the real leak is in memory writes (or vice versa).

## Tangible Impact

**Population**: Developers of consumer and enterprise AI products with persistent cross-session memory — AI companion/assistant apps and enterprise copilots that remember prior conversations across sessions or users — who must demonstrate to privacy auditors, enterprise security reviewers, or regulators (under GDPR/CCPA-style data-isolation requirements) that one user's private information cannot surface in another user's session via the memory layer. The source benchmark's own finding (0% vs. 67% leakage) shows this is a live, not hypothetical, risk for exactly this population.
**Mechanism**: Correctly attributing a leak to retrieval vs. memory lets a team apply the right fix (access-control-aware chunking vs. memory-write isolation/scoping) on the first try, instead of misdiagnosing a memory leak as a retrieval problem and leaving the real hole open.
**Measure**: leakage rate broken out by failure class on the benchmark, before and after a targeted remediation; number of previously-misclassified leak incidents correctly re-attributed in a case study; adoption as a pre-release or CI gate (number of projects integrating the harness).

## Why Now

Persistent agent memory has gone from a research curiosity to a shipped feature in mainstream consumer and enterprise AI products through 2025–2026, and the first public measurement showing memory leakage running two orders of magnitude higher than retrieval leakage (67% vs. 0%) is new, specific evidence that this distinction matters right now, not as a future concern.

## Skill Angle

A "Leakage Classification" skill: given a set of agent conversation logs plus the contents of the memory store at the time, it classifies observed leakage incidents as retrieval-layer or memory-layer and recommends the matching fix — usable as a one-off incident-response or pre-audit check without integrating the full benchmark harness into CI.

## MVP Sketch

2–4 weeks, 1–2 people: build the two test harnesses (a multi-tenant RAG corpus with access-control labels for retrieval leakage; a multi-user memory store with cross-session probes for memory leakage), replicate the source repo's 0%/67% finding as a sanity check, then extend to 2–3 memory architectures (summarized-history, vector-memory, structured-fact-store) to see whether the leakage rate is architecture-dependent.

## Risks & Open Questions

- The 67% figure comes from one 2-star, days-old repo — needs independent replication before treating it as representative rather than an artifact of one specific memory implementation.
- Memory architectures vary widely (summarization, vector stores, structured facts); a benchmark tuned to one may not transfer to others, risking a narrow tool that doesn't generalize.
- Academic papers on agent-memory leakage alone (PersistBench, CIPL, MEMPROBE) may already cover enough ground that the real gap is just pairing them with a RAG-retrieval harness, a smaller lift than building both from scratch.
- Low HN engagement (3 points) means demand signal here is thinner than other patterns in this digest; worth validating interest with potential adopters before a full build.
