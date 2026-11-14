# Offline RAG Gatekeeper: Sub-1B CPU Decision Models for Air-Gapped Retrieval

- **Status**: EXPLORING
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P7
- **Maturity verdict**: PARTIAL — WebSearch found adjacent but not identical work (shipped Pleias-RAG-350M/1B CPU-optimized generation models with citations; a NeurIPS 2026 listing and a LogRocket article on sub-1B query classifiers/routers as research/blog guidance). No dedicated, adopted "tiny decision model for RAG pipeline checks" product found; the specific gating use case remains narrowly served.
- **Format**: PROJECT

## The Gap

Hacker News's "Show HN: Arc-decide – an MIT 0.4B decision model for RAG checks that runs on CPU" (2026-10-26, 3 pts) and r/Rag's "haiku.rag cracks top 20 on ERBench using local inference" (2026-11-09) both name the same constraint: "Most RAG systems on ERB utilize frontier models — which are off the table if you operate in air-gapped, DDIL, or privacy-first environments." Both are individual, low-engagement, one-off projects — early signal of a real constraint with only scattered, unendorsed point-solutions so far.

## The Project

A family of open, distilled sub-1B-parameter decision models — trained using a frontier model as the labeling teacher — that run on commodity CPU hardware to perform RAG pipeline gating tasks (chunk-relevance scoring, retrieval-sufficiency checks, re-rank decisions) without GPU access or network connectivity. Shipped as downloadable checkpoints plus a thin CPU inference wrapper (ONNX/GGUF) that any RAG stack can call in place of a frontier-model API for these specific gating decisions, letting disconnected deployments run a genuinely usable RAG assistant instead of none at all.

## Tangible Impact

**Population**: Field-deployed teams operating in disconnected/intermittent/limited-bandwidth (DDIL) environments where frontier-model APIs are categorically unavailable — disaster-response and humanitarian-logistics teams working from mobile command posts, maritime vessels, and field clinics in low-connectivity regions, plus defense/intelligence units on air-gapped networks and on-prem healthcare/legal deployments barred by policy from calling external APIs. These are the exact use cases named in both source posts.
**Mechanism**: Replacing a frontier-model gating call with a small, locally-runnable distilled model lets these teams run a usable RAG assistant entirely offline — instead of having no AI-assisted document retrieval at all, or relying on unreliable, unvalidated one-off hacks like the two cited projects.
**Measure**: gating accuracy versus a frontier-model judge on a held-out eval set; inference latency/throughput on representative low-power CPU hardware (e.g., a laptop-class device with no GPU); task success rate (correct document found) in a pilot offline deployment such as a field-clinic document lookup.

## Why Now

Distillation and quantization techniques for producing accurate sub-1B models from frontier-model labels have matured enough through 2025–2026 that a narrowly-scoped gating task (not general generation) is now a realistic target for commodity-CPU deployment, and the two independent November 2026 posts show practitioners are already attempting this without a shared, validated toolkit.

## MVP Sketch

2–4 weeks, 1–2 people: pick one gating task (chunk-relevance scoring) as the first target, generate a labeled training set by sampling queries/chunks and labeling them with a frontier-model judge, fine-tune/distill a sub-1B base model, quantize to GGUF, and benchmark accuracy-vs-frontier-judge and CPU latency against the two cited projects (Arc-decide, haiku.rag) as baselines.

## Risks & Open Questions

- A sub-1B model distilled from one teacher's judgments may not generalize across corpora or domains without re-training per deployment, adding setup cost exactly where low-resource teams can least afford it.
- The two existing projects (Arc-decide, haiku.rag) may already cover enough of this ground that the real gap is adoption/packaging, not a new model.
- DDIL/air-gapped buyers (defense, humanitarian orgs) often have long, slow procurement cycles — validating real demand before a multi-week build is worth a direct outreach check.
- Benchmarking "accuracy versus frontier judge" assumes the frontier judge itself is reliable ground truth, which may not hold for ambiguous relevance calls.
