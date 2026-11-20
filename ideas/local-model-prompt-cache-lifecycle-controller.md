# Cache Clock: A Single-Controller Prompt-Cache Lifecycle Manager for Local Model Serving

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: Small & local models
- **Source**: research/2026-11-20-small-local-models.md · P7
- **Maturity verdict**: PARTIAL — WebSearch found only scattered point-solutions covering individual stages: `prompt-cache-keepalive` (Python) and a Go `eyrie` CacheWarmer both just "touch" a cache to keep it warm; `pi-fabric` documents a lease/hold model with compaction triggers but is tied to one ecosystem; `dirge-agent` (Rust) implements TTL-tier selection only. No standalone library unifies warm→compact→offload→expire under one clock as a reusable controller — the pattern exists only inside one project's PR (`NousResearch/hermes-agent` #156455), unextracted.
- **Format**: BOTH — the controller is runtime infrastructure that must stay running inside the serving process; a one-time "given your traffic pattern and hardware, here are the right threshold values" recommendation is a separable advisory judgment.
- **Data Sources**: CONNECTED — wraps the team's existing local-model serving runtime's own cache primitives directly (vLLM's prefix caching, llama.cpp's slot save/restore, Ollama's keep-alive) — all three are mature, documented APIs today. No external data is pasted or uploaded; the library instruments calls the serving stack is already making.

## The Gap
A GitHub PR on `NousResearch/hermes-agent` ("Prompt cache kept warm while it pays, then the idle chat compacts or offloads," 7 reactions, 19 comments) implemented a unified state-machine controller — one clock driving warm → compact → expire — for a local model's prompt cache. A reviewer explicitly asked for the controller's constants to be exposed as reusable config, calling the single-controller design "worth generalizing beyond this one project." It never was: it stayed inside that one agent's codebase, and the closest public alternatives each only cover one stage of the lifecycle.

## The Project
A small library wrapping a local-model serving runtime's existing cache primitives behind one state machine per session: **WARM** (actively billed/served, stays fully resident), **COMPACT** (idle past threshold one — reduced-footprint, fast-restore state, e.g. offloaded to CPU/disk), **EXPIRE** (idle past threshold two — fully evicted). One configurable clock drives all three transitions per session, replacing the hand-rolled TTL/eviction logic every team currently re-derives.

Components: a cache-state adapter per backend (vLLM/llama.cpp/Ollama); the single-clock controller with exposed, per-deployment-configurable constants; a metrics hook reporting GPU-memory-hours and cold-restore latency; an optional cost-accounting hook that counts the unload against usage, matching the digest's own cited evidence of teams wanting exactly that.

## Tangible Impact
**Population**: Solo developers and small teams self-hosting local/open models for their own agent products or internal tools — the kind of deployment Ollama's own reported ~8.9 million monthly active developers (TechCrunch, July 2026) represent a meaningful share of — who run variable, bursty traffic (busy during work hours, idle overnight/weekends) and today either keep every session's cache fully warm (wasting GPU memory on idle sessions) or hand-roll their own TTL/eviction code per project, exactly as the digest's own cited point-solutions (`prompt-cache-keepalive`, `eyrie`, `pi-fabric`, `dirge-agent`) show teams already doing separately.
**Mechanism**: Gives this population a drop-in controller instead of a rewrite — wraps their existing vLLM/llama.cpp/Ollama cache calls so idle sessions automatically compact or evict on one configurable clock instead of staying fully resident or needing bespoke TTL code, freeing GPU memory for other sessions/models without a surprise cold-start latency hit when a session returns.
**Measure**: (1) GPU-memory-hours reclaimed vs. an always-warm baseline on a real bursty traffic trace; (2) p50/p95 "returning session" cold-restore latency after a COMPACT-tier reload vs. a full cold start; (3) lines of custom eviction/TTL code a pilot team removes after adopting the library, self-reported before/after.

## Why Now
Local model serving (vLLM, llama.cpp, Ollama) has matured enough over the last year that prefix-caching and slot save/restore are now standard features across all three major runtimes — the raw primitives this controller needs already exist and are stable. What's missing is the single-clock orchestration layer on top of them, which the hermes-agent PR just demonstrated works inside one codebase without anyone extracting it.

## Skill Angle
Trigger: a developer already running local-model serving wants threshold recommendations before wiring in the controller. Inputs: a description of their traffic pattern (peak concurrent sessions, typical idle-gap length, GPU VRAM budget) and which backend they use. Output: recommended WARM/COMPACT/EXPIRE threshold values and the specific backend API calls to wire them to (e.g., the exact vLLM prefix-cache or llama.cpp slot-save invocation) — a one-time config recommendation, separate from running the controller itself.

## MVP Sketch
A Python library implementing the three-state clock as a decorator/middleware around an existing vLLM or Ollama client, with configurable thresholds and a pluggable backend-adapter interface (ship vLLM support first, since its prefix-caching API is the most mature). Experiment: replay a real bursty traffic trace against an always-warm baseline and the controller, and confirm it reclaims a measurable share of GPU-memory-hours at an acceptable cold-restore latency penalty. 2-4 weeks, 1-2 people.

## Risks & Open Questions
- vLLM, llama.cpp, and Ollama expose meaningfully different cache primitives; a thin unifying adapter may not generalize as cleanly as the hermes-agent PR's single-codebase version did.
- COMPACT-tier restore latency could be bad enough on some hardware (slow disk, no NVMe) that the memory savings aren't worth the user-facing delay — needs real measurement, not an assumption.
- The hermes-agent PR's reviewer comment is the only direct evidence this is wanted outside one project; worth validating demand with a couple of other serving-stack maintainers before building the full three-backend version.
- As vLLM keeps adding native cache-management features, this library's addressable surface could shrink into "just use the runtime's own built-in policy" — worth checking its roadmap before investing heavily.
