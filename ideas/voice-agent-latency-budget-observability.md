# True P95: A Vendor-Neutral Latency Budget Observability Tool for Production Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-14-voice-multimodal-agents.md · P8
- **Maturity verdict**: PARTIAL — vendor-specific tooling exists and is non-trivial (LiveKit Agent Observability, Dasha's Call Inspector, a documented Prometheus/Grafana stack for LiveKit agents), but each is locked to its own framework, and Dasha's own guide flags that summing per-stage p95s does not produce a true end-to-end p95 — the measurement-methodology gap a production builder complained about (6 months running a voice agent, "latency math is way harder than the demos suggest," per r/AI_Agents) remains real even with this tooling. No neutral, cross-vendor tool surfaced.
- **Format**: BOTH
- **Data Sources**: CONNECTED — ingests OpenTelemetry trace exports from the team's existing voice-agent stack (LiveKit Agents, Pipecat, or any framework emitting OTel spans for STT/LLM/TTS/network stages); OTel is a mature, already-broadly-adopted standard and several voice frameworks already emit it, so this reads real telemetry rather than requiring the user to hand-describe their pipeline.

## The Gap
A practitioner who spent six months running a production voice agent for service businesses reports that end-to-end latency math — STT + LLM + TTS + network, under real call conditions — is significantly harder to reason about than demo videos suggest (r/AI_Agents, reported via aggregator in this run). The tooling that exists is vendor-locked (LiveKit's own observability, Dasha's Call Inspector) and, by Dasha's own documentation, methodologically flawed in the common case: naively summing each stage's p95 overstates or understates the true end-to-end p95 depending on correlation between stages, and no neutral tool computes the real joint distribution.

## The Project
An open-source, framework-agnostic latency-observability library that ingests OTel traces from any voice-agent stack and computes true end-to-end percentile latency from the actual joint per-call distribution — not a sum of per-stage percentiles — alongside a stage-attribution breakdown (how much of a slow call's total time came from STT, LLM time-to-first-token, TTS, or network) so a team can see both the honest number and where to look when it's bad. Ships as a library plus a lightweight dashboard, designed to sit next to whatever vendor dashboard a team already has rather than replace it, specifically for teams who've outgrown trusting one vendor's framing of their own latency.

## Tangible Impact
**Population**: small-to-mid-size teams running production voice agents for real call volume (service-business appointment booking, order intake, support lines) who are past the demo stage and hitting real latency-tuning decisions with money and caller experience on the line — the same population the source Reddit complaint comes from, explicitly distinct from teams still in the demo/pilot phase.
**Mechanism**: a team gets an honest, correctly-computed end-to-end p95 instead of a vendor-dashboard number that may be computed the methodologically-wrong way (summed per-stage percentiles), letting them correctly prioritize which stage to optimize instead of chasing a stage that looks slow in isolation but isn't actually driving the tail.
**Measure**: delta between the tool's computed true end-to-end p95 and the naive sum-of-stage-p95s on the same real call data (quantifying how wrong the common shortcut actually is); time-to-diagnose a latency regression (from alert to identified root stage) before/after adoption; number of distinct voice-agent frameworks the OTel ingestion adapter supports within 90 days.

## Why Now
OpenTelemetry instrumentation is now the de facto standard several voice-agent frameworks already emit by default, which is exactly what makes a neutral cross-vendor tool buildable today — the raw trace data exists, it's just that nobody has built the correct joint-distribution computation and stage-attribution layer on top of it yet.

## Skill Angle
A one-shot latency-audit skill: given a team's exported OTel trace file (or a pasted summary of their per-stage latency numbers), the skill computes the true end-to-end percentile from the raw traces, flags whether their existing dashboard is using the flawed sum-of-percentiles method, and produces a plain-language stage-attribution report. The skill is the one-time audit a team runs to sanity-check their current setup; the project is the always-running library/dashboard a team adopts to keep getting this continuously.

## MVP Sketch
Scope: a Python library that parses OTel trace exports into per-call stage timings, computes the true joint end-to-end percentile (via bootstrap resampling of actual call-level totals, not stage-level aggregation), and a stage-attribution breakdown for the slowest decile of calls. Validate against a synthetic dataset with known injected correlation between stages (to prove the naive sum method is measurably wrong) plus one real trace export from a volunteer team's LiveKit deployment. Target: 2-3 weeks for one person with observability/stats background.

## Risks & Open Questions
- If most teams' stage latencies turn out to be close to independent in practice, the "naive sum is wrong" framing may be a smaller real-world problem than the Dasha documentation and the Reddit complaint suggest — worth validating the actual correlation magnitude on real data before over-claiming the fix matters.
- OTel adoption, while growing, is still inconsistent across voice-agent frameworks — some teams may not emit the stage-level spans this tool needs, requiring either an instrumentation SDK contribution or accepting a smaller initial addressable set of frameworks.
- A sufficiently motivated vendor (LiveKit, Dasha) could fix their own percentile-computation methodology directly, which would close this specific angle of the gap for their customers while leaving only the cross-vendor neutrality argument standing.
- The underlying practitioner complaint is a single aggregator-summarized Reddit post, not independently verified in this run — worth finding and reading the original thread before investing further, to confirm the complaint is about measurement methodology and not something this tool wouldn't actually fix (e.g. genuinely slow vendor APIs).
