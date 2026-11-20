# Fix Once: A Persistent Correction-Memory Layer for RAG Retrieval Mistakes

- **Status**: PUBLISHED (promoted 2026-11-20 cycle 286: evidence density — ≥2 independent threads; published, synced cycle 308)
- **Date**: 2026-11-20
- **Topic**: RAG techniques
- **Source**: research/2026-11-20-rag-techniques.md · P9
- **Maturity verdict**: PARTIAL — WebSearch found academic research prototypes addressing this — RFM-RAG (arXiv 2508.17862, persistent evidence pool + completeness evaluator), SEGMEM-RAG (AAAI, feedback-evaluator that tunes source selection), GAM-RAG (arXiv 2603.01783, code at an anonymous 4open.science link, explicitly warns naive memory updates "accumulate spurious correlations") — plus isolated one-off GitHub repos (Emmimal/memory-leak-rag) and practitioner blog posts. None is a mainstream, maintained, shipped product; this is scattered research-stage work, so the community complaint about no learning loop remains substantively unaddressed.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the RAG application's own query/feedback log (thumbs-up/down plus any correction text a user or support agent enters), captured via a lightweight logging SDK this project ships as part of itself. No mature third-party connector exists today for "retrieval correction history" specifically — that is exactly the gap — so this idea builds the capture layer, while the SDK plugs into whatever chat UI the team already has via a single event-emit call rather than requiring a new chat surface.

## The Gap

A freeCodeCamp piece argues RAG systems don't learn; a discuss.huggingface.co thread titled "Why does RAG still feel clunky in 2025?" and a community.openai.com thread titled "RAG is not really a solution" raise the same complaint from two separate practitioner communities — that RAG treats every query independently with no mechanism to remember that a past retrieval picked the wrong chunk and was corrected, the way a human analyst would carry that correction forward. All three are discussion threads with no product named as having solved persistent cross-query learning; the research prototypes that exist (RFM-RAG, SEGMEM-RAG, GAM-RAG) are scattered and unshipped.

## The Project

A correction-memory layer that captures a human's fix (right chunk or right answer instead of what the system retrieved) and feeds it forward as a boosted retrieval signal for recognizably similar future queries, so the second and later instances of the same mistake get the corrected answer automatically instead of a human re-fixing the identical wrong retrieval every time it recurs. Components: a correction-logging SDK, a near-duplicate-query lookup that checks the correction log before falling back to normal retrieval, and a decay/re-confirmation rule guarding against GAM-RAG's own warning that naive memory updates accumulate spurious correlations.

## Tangible Impact

**Population**: Support/IT-helpdesk teams (small-to-mid, 2–20 agents) running a RAG chatbot over product or policy documentation, who today re-correct the same wrong-chunk answer by hand every time a near-duplicate question recurs, because nothing persists the fix from one query to the next — the same "RAG doesn't learn" complaint raised independently on HuggingFace and OpenAI's own community forums.
**Mechanism**: Capturing a correction and propagating it forward as a preferred retrieval signal for similar future queries turns each fix into a permanent gain instead of a one-off patch an agent has to repeat; an explicit decay/completeness check prevents stale corrections from calcifying into new errors as the underlying documents change.
**Measure**: % of repeat near-duplicate queries that get the corrected answer without a second human correction; number of manual re-corrections avoided per week post-deployment vs. a pre-deployment baseline; rate of "spurious" correction propagation caught by the decay/completeness check (a correction wrongly applied to a dissimilar query).

## Why Now

RAG chatbots have been live long enough in support/helpdesk settings for teams to have accumulated real correction histories worth learning from, and the main technical risk flagged by the research — naive memory updates "accumulating spurious correlations," per GAM-RAG — is now explicitly named and guardable-against rather than undiscovered, meaning the pattern can be built defensively instead of blind.

## Skill Angle

A "Correction Pattern Review" skill: given a pasted batch of a team's own recent correction-log entries (wrong answer, right answer, the query that triggered it), groups them into recurring failure patterns and drafts which are safe to auto-propagate vs. which look like one-off edge cases that shouldn't generalize — a human-reviewed gate before trusting the full automated feedback loop.

## MVP Sketch

2–4 weeks, 1–2 people: build the logging SDK (emit a correction event: query, wrong-retrieved-chunk, corrected-chunk-or-answer), a similarity-based lookup checking new queries against the correction log before normal retrieval, and a basic decay rule (a correction expires or must be re-confirmed after N uses). Validate by replaying a hand-built set of near-duplicate query pairs through a test corpus, confirming the second occurrence of each correctable mistake resolves correctly without a second manual fix.

## Risks & Open Questions

- GAM-RAG's own warning that naive memory updates accumulate spurious correlations is a real failure mode this project must design against from day one, not discover in production.
- "Near-duplicate query" detection is itself an unsolved precision problem; too loose a similarity match could apply a correction to a genuinely different question.
- A sufficiently motivated team could get most of the value from a simpler, manual FAQ-override list rather than adopting a learning layer — this project needs to clearly beat that baseline on volume/maintenance cost.
- Scattered research prototypes (RFM-RAG, SEGMEM-RAG) could converge into a shipped library before this project ships; worth a quick re-check before committing engineering time.
