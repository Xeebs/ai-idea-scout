# Cache Guard: A Poisoning-Resistant, Self-Tuning Semantic Cache for RAG

Every team running a customer-facing RAG chatbot at real volume eventually reaches for semantic caching to cut the bill — and every team then discovers the same thing: the vendor numbers lied to them by omission, and nobody mentioned the attack surface they just opened up.

## The Gap

Semantic caching sounds like a free lunch: instead of re-running retrieval and generation for every query, you cache responses keyed by embedding similarity, so a question that's close enough to one you've already answered gets served from cache instead of the full pipeline. The pitch is 40-80% cost savings. The reality, according to independent 2026 practitioner and vendor writeups — tianpan.co's "Semantic Caching for LLMs," a Percona piece, a DEV Community post, and a cited AWS evaluation run across 63,796 real chatbot queries — is a lot messier. Actual hit rates land anywhere from 18% to 60% depending on the workload, nowhere near the "95%" figures vendors advertise, because that 95% describes match *accuracy* on the queries that do hit the cache, not how often the cache gets hit in the first place. Threshold tuning — how similar is "similar enough" to serve a cached answer — turns out to be workload-specific and brittle, and teams are left to work it out by trial and error, alone, every time.

That's the annoying half of the problem. The alarming half is that an NDSS 2026 paper (Wu et al.) demonstrated a 75% poisoned-hit rate against GPTCache — the most widely adopted open-source semantic cache (8.2k GitHub stars, integrated into both LangChain and llama_index) — under realistic similarity thresholds. An attacker who can influence what gets cached can get a poisoned answer served to every subsequent user whose query lands close enough in embedding space. The paper's own cited defenses, LaCache and SAFE-CACHE, are brand-new academic proposals, not shipped, evaluated products. So the most popular semantic-caching layer in the ecosystem has a demonstrated hole in it, and as of today there is nothing production-ready plugging that hole.

Put together: semantic caching is a DIY tuning exercise per team, with an unaddressed security gap sitting underneath the whole exercise.

## The Project

Cache Guard isn't a new caching mechanism — basic semantic caching is already saturated as a technology, between GPTCache and codefuse-ai's ModelCache (933 stars). Reinventing the storage and similarity-matching core would be pointless. Instead, it's a layer built on top of that mature core that adds the two things no shipped product currently provides together.

The first is continuous, per-workload threshold auto-tuning: instead of a fixed similarity cutoff set once and left alone, the system observes the live query stream and adjusts the threshold to match the actual traffic pattern, while reporting *true* hit rate separately from match accuracy — so a team can finally see, in real numbers, whether caching is pulling its weight for their specific workload instead of trusting a vendor slide.

The second is a lightweight poisoning-resistant verification step: before a cache hit gets served, the system re-validates that the cached answer's underlying retrieved-source citations still match the incoming query's actual retrieved context. If they don't line up, the cache hit gets rejected and the query falls through to a full retrieval — closing exactly the attack surface the NDSS paper demonstrated, rather than hoping a brand-new academic defense holds up unverified.

Three components make up the system: a traffic-observing threshold tuner, a cache-hit verification check, and an observability dashboard reporting true hit rate, realized cost savings, and blocked-poisoning-attempt counts — so a team can see the thing is actually working instead of flying blind.

## Tangible Impact

**Population**: Engineering/DevOps teams operating customer-facing RAG chatbots at meaningful query volume (tens of thousands of queries/day and up — the same scale the cited AWS evaluation's 63,796-query sample represents) who want the cited cost savings from semantic caching but are either avoiding caching due to poisoning risk, or running it with an un-tuned, vendor-default threshold and no visibility into whether it's actually working.
**Mechanism**: Replaces a fixed, workload-blind similarity threshold and an unaddressed poisoning hole with continuously-tuned thresholds matched to the team's actual traffic and a verification step that catches a poisoned-hit attempt before it's served to the next user, so teams get the cited cost savings without inheriting the demonstrated attack risk.
**Measure**: true cache hit rate achieved vs. vendor-claimed match accuracy (closing the gap the digest identifies); realized cost savings (%) vs. no-cache baseline; poisoned-query attack success rate in a red-team eval replicating the NDSS methodology (target: near-zero vs. GPTCache's demonstrated 75%).

## Try It

There's no packaged skill for this one yet — it's filed as a PROJECT, not a SKILL, because the core value is a runtime layer (the tuner and the verification check have to sit in the live request path), not a one-shot task a prompt can hand back. If that changes, a companion skill will show up at `skills/rag-poisoning-resistant-semantic-cache/` and get linked here.

In the meantime, the idea file at `ideas/rag-poisoning-resistant-semantic-cache.md` has the full MVP sketch: a 2-4 week build wrapping GPTCache's existing storage/similarity-matching core with the auto-tuning layer and the citation-verification check, validated against a synthetic workload and a reproduction of the NDSS paper's own poisoning attack.

Worth knowing before you build on this: the verification check adds overhead on every cache hit, which could eat into the latency savings caching exists to provide in the first place — that's the first thing an MVP needs to measure, not assume away. And if your workload has a low query-repetition rate, the digest's own cited 18-60% hit-rate spread suggests semantic caching may not be worth the complexity for you regardless of how well it's tuned — this isn't a universal fix, and no honest version of this pitch should claim otherwise.

Surfaced from `research/2026-11-12-rag-techniques-iii.md`, pattern `P4`.
