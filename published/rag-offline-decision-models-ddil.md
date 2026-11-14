# Offline RAG Gatekeeper: Sub-1B CPU Decision Models for Air-Gapped Retrieval

Every RAG pipeline leans on a frontier model for the small, constant stream of judgment calls underneath the headline answer — is this chunk actually relevant, is retrieval sufficient, should this result be re-ranked. That's fine until the network isn't there. For teams working from a disaster-response command post, a field clinic with no reliable uplink, or an air-gapped government network, "call the frontier model" isn't a latency problem, it's a non-starter — and right now the answer for them isn't a lighter-weight RAG system, it's no RAG system at all.

## The Gap

The signal for this is thin but pointed: a Show HN post, "Arc-decide – an MIT 0.4B decision model for RAG checks that runs on CPU" (2026-10-26, 3 points), and an r/Rag thread about haiku.rag cracking the top 20 on ERBench using local inference (2026-11-09), which states the constraint plainly — "Most RAG systems on ERB utilize frontier models — which are off the table if you operate in air-gapped, DDIL, or privacy-first environments." Both are individual, low-engagement, one-off projects, which is itself the tell: this is early signal of a real constraint with only scattered, unendorsed point-solutions attempting to answer it.

A broader search turned up adjacent work, not a match. Pleias has shipped CPU-optimized sub-1B-to-1B RAG *generation* models with citations — but generation isn't the bottleneck here, the pipeline's internal gating decisions are. A NeurIPS 2026 listing and a LogRocket article describe sub-1B models used as query classifiers or routers, which is closer, but both are presented as research or blog guidance rather than a maintained, adopted tool. Nobody has shipped a dedicated "tiny decision model for RAG pipeline checks" that a disconnected deployment could just drop in. The narrow use case — chunk relevance scoring, retrieval-sufficiency checks, re-rank decisions — remains served only by Arc-decide and haiku.rag's own one-off implementations.

## The Project

The idea is a family of open, distilled sub-1B-parameter decision models — trained using a frontier model as the labeling teacher — purpose-built to run RAG pipeline gating tasks on commodity CPU hardware with no GPU and no network connection. Not a smaller version of the chat model, a model that only ever has to answer narrow questions like "is this chunk relevant" or "is this retrieval good enough to answer with." Shipped as downloadable checkpoints plus a thin CPU inference wrapper (ONNX or GGUF), any existing RAG stack could swap a frontier-model API call for a local call on these specific gating decisions — turning "no AI-assisted retrieval at all" into a genuinely usable, fully offline RAG assistant.

The path to building it mirrors what Arc-decide and haiku.rag already sketched out but didn't generalize: pick one gating task first (chunk-relevance scoring is the natural starting point), build a labeled set by sampling real queries and chunks and labeling them with a frontier-model judge, distill a sub-1B base model against those labels, quantize it down to GGUF, and benchmark it — both for accuracy against the frontier judge and for raw latency on representative low-power CPU hardware — against those same two projects as the baseline to beat.

## Tangible Impact

**Population**: Field-deployed teams operating in disconnected/intermittent/limited-bandwidth (DDIL) environments where frontier-model APIs are categorically unavailable — disaster-response and humanitarian-logistics teams working from mobile command posts, maritime vessels, and field clinics in low-connectivity regions, plus defense/intelligence units on air-gapped networks and on-prem healthcare/legal deployments barred by policy from calling external APIs. These are the exact use cases named in both source posts.
**Mechanism**: Replacing a frontier-model gating call with a small, locally-runnable distilled model lets these teams run a usable RAG assistant entirely offline — instead of having no AI-assisted document retrieval at all, or relying on unreliable, unvalidated one-off hacks like the two cited projects.
**Measure**: gating accuracy versus a frontier-model judge on a held-out eval set; inference latency/throughput on representative low-power CPU hardware (e.g., a laptop-class device with no GPU); task success rate (correct document found) in a pilot offline deployment such as a field-clinic document lookup.

## The Honest Risks

Two things could already quietly undercut this before a line of code is written. First, a model distilled from one teacher's judgments on one corpus may not generalize to a different domain's documents without a fresh round of retraining — which adds exactly the setup cost that low-resource, disconnected teams can least afford. Second, and more bluntly: the two existing projects, Arc-decide and haiku.rag, might already cover enough of the real ground that what's actually missing isn't a better model, it's adoption and packaging of what already exists. There's also a quieter assumption baked into the whole evaluation plan — benchmarking "accuracy versus the frontier judge" only means something if the frontier judge itself is reliable ground truth, which doesn't obviously hold on the ambiguous relevance calls that matter most. And DDIL buyers like defense and humanitarian orgs tend to run on long, slow procurement cycles, so validating real demand with direct outreach is worth doing before committing multiple weeks to a build.

The smallest version that tests whether any of this holds up is a 2–4 week, 1–2 person build: one gating task, one labeled set, one distilled and quantized model, benchmarked head-to-head against Arc-decide and haiku.rag on both accuracy and CPU latency.

---

Surfaced from `research/2026-11-11-rag-techniques.md`, pattern `P7`.
