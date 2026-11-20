# Fix Once: A Persistent Correction-Memory Layer for RAG Retrieval Mistakes

Every RAG chatbot has the same quiet failure mode: it gets a retrieval wrong, a human fixes it by hand, and then — because nothing in the stack remembers that fix — it makes the exact same mistake the next time someone asks a near-identical question. A human analyst would never do that twice. Most production RAG systems do it indefinitely, because they treat every query as if it had no past.

## The Gap

This isn't a hunch — it's the same complaint surfacing independently across separate practitioner communities in the last 30 days. A freeCodeCamp piece argues plainly that RAG systems don't learn. A discuss.huggingface.co thread titled "Why does RAG still feel clunky in 2025?" and a community.openai.com thread titled "RAG is not really a solution" raise the identical frustration from two different forums: retrieval is corrected once, and then re-breaks on the next near-duplicate question, because there's no mechanism to carry that correction forward.

The honest caveat here is that this gap isn't undiscovered — it's underbuilt. Research prototypes already exist: RFM-RAG (arXiv 2508.17862) maintains a persistent evidence pool with a completeness evaluator; SEGMEM-RAG uses a feedback-evaluator to tune source selection; GAM-RAG (arXiv 2603.01783) goes further and explicitly warns that naive memory updates "accumulate spurious correlations" — a real failure mode its own authors flag. There are also scattered one-off GitHub repos and practitioner blog posts poking at the idea. None of this has converged into a mainstream, maintained, shipped product. It's research-stage and fragmented, which is exactly why the "RAG doesn't learn" complaint is still being raised on two separate forums instead of being answered by a link to an existing tool.

## The Project

The core idea is a correction-memory layer that sits in front of normal retrieval: when a human fixes a wrong answer — pointing to the right chunk or supplying the right answer directly — that fix gets logged and then checked against future queries. If a new query looks like a near-duplicate of a previously-corrected one, the system serves the corrected answer instead of repeating the original mistake. The second and every later instance of the same recurring error gets handled automatically; only genuinely new mistakes need a human.

Three components make up the loop: a lightweight correction-logging SDK that any team can wire into their existing chat UI with a single event-emit call (no new chat surface required), a near-duplicate-query lookup that checks the correction log before falling back to normal retrieval, and — taking GAM-RAG's own warning seriously — a decay/re-confirmation rule so that a correction doesn't quietly calcify into a new error once the underlying documents change. The novel pattern here is the persistent, cross-query memory of a correction itself, not a generic RAG feature bolted on afterward.

## Tangible Impact

**Population**: Support/IT-helpdesk teams (small-to-mid, 2–20 agents) running a RAG chatbot over product or policy documentation, who today re-correct the same wrong-chunk answer by hand every time a near-duplicate question recurs, because nothing persists the fix from one query to the next — the same "RAG doesn't learn" complaint raised independently on HuggingFace and OpenAI's own community forums.
**Mechanism**: Capturing a correction and propagating it forward as a preferred retrieval signal for similar future queries turns each fix into a permanent gain instead of a one-off patch an agent has to repeat; an explicit decay/completeness check prevents stale corrections from calcifying into new errors as the underlying documents change.
**Measure**: % of repeat near-duplicate queries that get the corrected answer without a second human correction; number of manual re-corrections avoided per week post-deployment vs. a pre-deployment baseline; rate of "spurious" correction propagation caught by the decay/completeness check (a correction wrongly applied to a dissimilar query).

## Try It

No companion skill has been built for this idea yet — it's currently a project-only writeup (the idea file's `Skill Angle` section sketches a "Correction Pattern Review" skill for grouping a team's own correction-log entries into safe-to-auto-propagate vs. one-off patterns, but no `skills/rag-persistent-correction-memory/` directory exists yet to try). Check back, or watch `ideas/rag-persistent-correction-memory.md` for when that lands.

Worth flagging before you build on this: a sufficiently motivated team could get most of the practical value from a much simpler manual FAQ-override list instead of a learning layer, and the scattered research prototypes (RFM-RAG, SEGMEM-RAG) could converge into a shipped library before anyone finishes building this — both are reasons this gap might close on its own, and both are worth a quick re-check before sinking real engineering time in.

---

Surfaced from `research/2026-11-20-rag-techniques.md`, pattern `P9`.
