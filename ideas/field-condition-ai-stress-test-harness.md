# FieldCheck: A Low-Bandwidth and Field-Condition Stress-Test Harness for AI Tools

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P6
- **Maturity verdict**: OPEN — GitHub search for an AI-specific low-bandwidth/field-condition test harness returned nothing; WebSearch surfaced only generic non-AI network-degradation tooling (Linux tc/netem, wondershaper, NectoProxy, Chrome DevTools, Facebook's Augmented Traffic Control, BrowserStack/AWS Device Farm throttling) — commodity building blocks, never assembled into an "evaluate AI tool degradation under rural bandwidth/device constraints" harness or checklist.
- **Format**: BOTH

## The Gap
An HLTH industry article states plainly: there is no requirement or incentive for developers to test AI tools in rural settings, include rural data in training sets, or design for low-bandwidth environments. Separately, the ICTworks data cited in P3 (only 34% of CHW-facing AI pilots scale beyond the pilot stage) is consistent with tools that were never actually stress-tested against the field conditions they were deployed into. Every piece of the underlying infrastructure to simulate bad network/device conditions already exists (tc/netem, Augmented Traffic Control, device-farm throttling) — what's missing is an assembled tool that applies those primitives specifically to AI-tool behavior (does the model time out mid-inference, does a chat UI silently drop a half-received response, does an on-device model's battery/thermal profile make it unusable after 20 minutes on a $60 Android phone) rather than generic page-load performance.

## The Project
A stress-test harness, distributed as a CLI and a hosted test-runner, that wraps an AI tool's actual request/response flow (API calls, chat UI, or on-device inference binary) in a configurable field-condition profile — a named preset like "rural 2G, intermittent drops, mid-tier Android, thermal throttling after 15 min" built from real connectivity data (ITU/GSMA connectivity reports) rather than guesswork — and reports where the tool breaks: silent response truncation, timeout-without-retry, unhandled reconnect state, unacceptable latency, or on-device memory/battery exhaustion. The output is a pass/fail checklist report a team can attach to a release, plus a library of realistic presets (by region/connectivity-tier) other teams can reuse instead of inventing their own.

## Tangible Impact
**Population**: End users of AI-for-good tools who live in low-connectivity, low-end-device conditions — the direct beneficiaries are the ~2.6 billion people the ITU estimates remain offline or on severely constrained connections globally, who currently bear the cost when an AI tool built and tested only on a developer's fast urban connection silently fails in their actual conditions.
**Mechanism**: Today, "field-ready" is an assumption, not a tested property — the HLTH piece names this directly as a structural incentive gap. A harness that makes field-condition testing a concrete, runnable, reportable step removes the excuse and the cost barrier: a team can catch a silent-truncation or reconnect bug in CI before it reaches a CHW's phone in the field, rather than discovering it as an abandoned pilot statistic.
**Measure**: (1) number of distinct failure modes (silent truncation, dropped reconnects, unacceptable latency, device resource exhaustion) the harness surfaces in a tool that previously claimed to be "field-ready" but was never actually tested under realistic conditions; (2) adoption — number of independent AI-for-good projects integrating the harness into their release process within a year; (3) correlation (even anecdotal, via case studies) between harness-caught issues and the 34%-scaling-rate pilots that previously failed silently in the field.

## Why Now
This is purely an assembly problem on top of mature, stable primitives (netem, ATC, device-farm throttling have existed for years), and the ICTworks 34%-scaling-rate and HLTH "no incentive to test" findings both landed in the last 30 days as explicit, named articulations of the gap — the pattern is ready to build and the motivating evidence is freshly documented.

## Skill Angle
A Claude Code skill version: given a description of an AI tool's architecture (API-based chat, on-device inference, WhatsApp bot, etc.) and its target deployment region, the skill produces a tailored field-condition test plan — which presets to run (e.g., "rural 2G with drops" for a WhatsApp bot vs. "mid-tier Android thermal throttling" for an on-device app), what specific failure modes to check for given that architecture, and a checklist a team can work through even before the full harness is built or integrated. This is the planning/audit task a team runs once before a release; the project is the actual runnable harness and preset library that executes the test and produces the pass/fail report.

## MVP Sketch
Scope to one failure category first (connectivity-drop and timeout handling, since that's the most universally applicable across on-device and API-based tools) and one or two realistic presets (e.g., "rural 2G with 5% packet loss and periodic full drops," built from published GSMA connectivity-tier data). Stack: a CLI wrapping tc/netem (Linux) for network-condition injection, a thin request-proxy that can also inject response-truncation and timeout scenarios, and a report generator. The validating experiment: run the harness against 2-3 of the real tools already named in this digest (e.g., a public demo of one of the CHW chatbots) and confirm it surfaces at least one genuine failure mode the tool's own team wasn't aware of.

## Risks & Open Questions
- Device-level conditions (battery/thermal throttling on real low-end Android hardware) are much harder to simulate accurately than network conditions — the MVP may need to scope device-level testing out initially or rely on physical device labs.
- Adoption is the real risk, not feasibility: the HLTH article's point is that there's no *incentive* to test this way — the harness needs to be cheap and fast enough (ideally a CI step) that teams actually add it rather than skip it under deadline pressure.
- Risk that BrowserStack/AWS Device Farm's existing throttling features, combined with a documented preset library (even without new code), already closes most of this gap — worth prototyping the thinnest possible version (just presets + a how-to, no new harness code) before building custom tooling.
- Realistic connectivity presets need real data (ITU/GSMA reports) rather than guesses, or the harness risks testing against conditions that don't match actual field reality.
