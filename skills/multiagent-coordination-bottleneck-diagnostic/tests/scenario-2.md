# Scenario 2: Hierarchical, parallel content pipeline at 15 agents (expect LOW-MODERATE, not a false HIGH)

## Input

A team describes their setup:

> We run a content-production pipeline with 15 agents total: 1 top-level coordinator, 3 team leads (blog, social, newsletter), and each lead manages 4 worker agents (a writer, an SEO/format checker, an image-prompt generator, and a tone/brand reviewer). Workers only ever talk to their own team lead, never to workers on other teams or to the top coordinator directly. The coordinator only talks to the 3 leads, never directly to workers. Each week we get a batch of unrelated content requests (a blog post, a few social captions, a newsletter section) — these are independent of each other; the blog post doesn't depend on what the social captions say, and vice versa, so each team just runs its own 4-worker pipeline on its own batch of unrelated items in parallel. We're not seeing quality problems right now, but we've heard about this "coordination cliff" thing and want to check before we add a 4th team (video scripts) next quarter.

## Expected output characteristics (pass/fail checklist)

- [ ] Correctly identifies N = 15 and topology = hierarchical (coordinator -> 3 leads -> 4 workers each, workers never cross-talk), not full mesh.
- [ ] Computes edges using the hierarchical approximation (coordinator-to-lead edges + lead-to-worker edges within each sub-team), explicitly showing this is roughly linear in N rather than applying N(N-1)/2 = 105 — correctly rejects the mesh formula for this topology.
- [ ] Correctly identifies task type as parallelizable/independent (unrelated content items processed independently, not a sequential-reasoning chain) and explicitly states that the cited study's ~10-agent/39-70%-degradation threshold was measured on sequential-reasoning tasks and does not transfer directly here.
- [ ] Gives a reduced-confidence, qualitative read rather than mechanically applying the numeric threshold — flags **Risk: LOW-MODERATE** (not HIGH, since both the topology and task type are favorable) rather than falsely flagging HIGH just because N=15 > 10.
- [ ] Explains the two separate reasons risk is lower here: (1) hierarchical topology keeps edges roughly linear rather than quadratic, and (2) independent/parallel task type means the study's sequential-reasoning calibration doesn't apply directly.
- [ ] Addresses the planned 4th team (video scripts) explicitly: notes that adding a 4th sub-team under the same hierarchical pattern keeps the structure linear and is unlikely to meaningfully change the risk position, as opposed to if they were adding the new team's agents into a shared mesh.
- [ ] Still recommends the user run their own lightweight before/after benchmark if this is a high-stakes decision, given the lower confidence for non-sequential-reasoning task types.
- [ ] Does not invent a structural fix where none is needed — says plainly that the current hierarchical structure doesn't require restructuring at this size/shape.
- [ ] Includes the same confidence/scope note as scenario 1 (single study, estimate not measurement).

## Fails if

- It mechanically flags HIGH risk purely because N=15 exceeds 10, ignoring both topology and task-type caveats.
- It applies N(N-1)/2 to a topology explicitly described as hierarchical with no cross-talk.
- It invents an unnecessary restructuring recommendation despite the architecture being well-suited to its task.
- It fails to distinguish this scenario's task type (parallel/independent) from scenario 1's (sequential-reasoning), treating both identically.
