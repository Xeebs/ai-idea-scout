# Fail Closed Check: A Chaos-Tested Resilience Layer for Guardrail Detector Outages

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-guardrails-production.md · P2
- **Maturity verdict**: PARTIAL — WebSearch found extensive practitioner guidance (Splunk's "AI Guardrails" guide, a gateway doc describing a `fail_open` flag defaulting to fail-closed, multiple blogs recommending fail-closed for toxicity/PII/injection and fail-open only for advisory checks) but no evidence of a general, tested, cross-framework pattern or checklist — the guidance is prose advice per-vendor, and the NeMo Guardrails bug fix (merged 2026-11-10) shows even the flagship open-source implementation only just closed this gap in one specific detector path. Real but inconsistent coverage, not a solved problem.
- **Format**: BOTH
- **Data Sources**: MANUAL — the team pastes/links the source code (or a diff) of each guardrail call site showing how a detector-service exception, timeout, or non-200 response is currently handled, plus which categories are meant to be fail-closed vs. fail-open. A CONNECTED upgrade (pulling real timeout/exception traces for guardrail calls from an OTel/APM backend like Datadog or Honeycomb) is a plausible v2, but no mature connector exists today purpose-built for "guardrail detector health specifically," so MANUAL is the honest classification for the MVP.

## The Gap
NeMo Guardrails — the most prominent open-source guardrails framework — merged a fix on 2026-11-10 for a jailbreak detector that silently failed *open* (allowed everything through) when the detector service itself was unreachable. If the flagship reference implementation only just closed this in one code path, smaller and custom guardrail stacks almost certainly have the same latent bug elsewhere, and the digest's research found only per-vendor prose advice ("fail closed for safety checks") — no general, testable pattern or checklist a team can run against their own stack to prove it actually fails closed under a real outage.

## The Project
A fault-injection test harness plus a thin runtime circuit breaker that wraps any guardrail detector call (classifier API, judge LLM call, rules engine). The harness deliberately kills, times out, or 500s each configured detector one at a time and asserts the declared behavior (fail-closed categories must block; fail-open categories must log-and-continue) actually happens — catching exactly the class of bug the NeMo fix patched, before it ships. The circuit breaker component enforces a declared default (fail-closed unless explicitly marked fail-open) at the call boundary itself, so a team doesn't have to get the exception handling right in every call site by hand, and emits a structured alert every time a detector-unavailable fail-open actually fires in production — so "the guardrail silently passed everything through for six minutes" is a logged, alertable event, not a postmortem discovery.

## Tangible Impact
**Population**: engineering teams running production LLM agents on top of layered guardrail stacks (NeMo Guardrails, Guardrails AI, LLM Guard, or custom gateway middleware) — a proxy for scale is the combined ~18k GitHub stars across those three toolkits, implying thousands of teams with hand-rolled exception handling around detector calls today.
**Mechanism**: without a tested default, a detector outage (crash, deploy, network partition) silently converts a "safety-checked" pipeline into an unchecked one for the outage's duration, exactly as the NeMo bug did — end users get unfiltered model output with no record that protection was off. A chaos-tested circuit breaker turns an invisible failure mode into a declared, alerted, and pre-verified one.
**Measure**: percentage of a team's detector call sites that pass the fault-injection suite (correctly fail-closed/open per declaration) before vs. after adoption; count and duration of real production fail-open events captured by the alert (versus zero visibility today); time-to-detect a silent fail-open incident (target: seconds via alert, not discovered days later via a user report).

## Why Now
The NeMo Guardrails fix merged 2026-11-10 is live, dated proof that this gap exists in the most-used open framework right now, and chaos/fault-injection tooling (toxiproxy, Chaos Mesh patterns) is mature enough to adapt directly to this narrower guardrail-specific use case.

## Skill Angle
Trigger: a team pastes the call-site code for each guardrail detector integration (or a diff of a new one being added) along with which categories are supposed to be fail-closed vs. fail-open. The skill reviews the exception/timeout handling in that code, flags any path that would silently fail open on an unhandled exception or timeout against the stated policy, and drafts the corrected handling. This is a one-shot code-review judgment distinct from the project, which is the always-on circuit breaker and chaos-test suite that keeps enforcing and verifying that judgment over time.

## MVP Sketch
A small Python decorator/middleware (`@guarded(default="closed")`) that wraps a detector call, catches exceptions/timeouts, enforces the declared default, and emits a structured log event on every fallback. Pair it with a pytest-based fault-injection suite that monkeypatches 2-3 real detector integrations (one classifier API, one LLM-judge call) to raise/timeout and asserts the decorator's behavior. Single experiment: run the suite against an unmodified guardrail call site (no decorator) and show it fails open on an injected timeout; show the decorated version fails closed on the same injected fault.

## Risks & Open Questions
- A guardrail gateway vendor (TrueFoundry, agentgateway.dev) could add a native "fail-closed by default" flag quickly once this is named, narrowing the gap to just the testing/chaos-harness half.
- Teams may already have reasonable fail-closed defaults and just lack the testing/alerting half — validating real prevalence of the bug (beyond the one NeMo case) needs a small audit of other OSS guardrail repos' exception handling.
- A circuit breaker that's too aggressive (fails closed on transient blips) could itself become an availability problem for the product, trading a safety risk for a reliability one.
- This is adjacent to the published Tier Gate (severity-tiered composition) and Soft Landing (latency-degradation) ideas; the differentiator kept narrow here is a hard-outage/exception fault, not a severity policy or a latency-budget tradeoff — risks blending into either if scope creeps.
