# Shadow Check: A Compounding False-Positive Rate Harness for Guardrail Stacks

- **Status**: EXPLORING (promoted 2026-11-13 cycle 59: evidence density — ≥2 independent threads, the humanbound-firewall#55 eval-gap issue and the separately-sourced shadow-mode/FPR-measurement advisory content (P9) both name the same unmeasured compounding-FPR gap)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-and-guardrails-in-production.md · P1 (corroborated by P9)
- **Maturity verdict**: PARTIAL — `gh search repos` for "guardrail false positive stack" / "guardrail evaluation pipeline false positive" returned zero matches; WebSearch found only illustrative blog math on compounding FPR (tianpan.co, premai.io, gmicloud.ai), no tool measuring it on real traffic. Adjacent general-purpose guardrail-eval tooling exists (promptfoo red-team suite, Splunk's evals-to-guardrails loop, NeMo evals) but none is purpose-built for this. Corroborated by P9: shadow/monitor-mode rollout is described everywhere as manual discipline (Netskope's "AI Guardrails Dashboard," Kyverno policy reports) with no integrated, LLM-guardrail-specific shadow-mode FPR workflow.
- **Format**: BOTH
- **Data Sources**: CONNECTED (project) — reads guardrail decision logs directly from each guard's own call site (NeMo Guardrails/Guardrails AI/LLM Guard hooks, or an API gateway like Kong/Portkey/LiteLLM sitting in front of the LLM calls); no standard log schema exists across these yet, so a thin per-platform adapter is part of the build, not a from-scratch connector. MANUAL (skill) — team pastes/exports a CSV/JSON sample of per-guard verdicts (input, which guard fired, block/pass, ground-truth benign/malicious label where known) for a one-shot FPR audit.

## The Gap
`humanbound/humanbound-firewall#55` is an unresolved issue, opened by the maintainer of a dedicated guardrail-firewall project, admitting the repo has "no evals for the firewall's decisions" — it ships without measuring whether chained checks let normal users through. WebSearch corroborates this is a recognized, unsolved practitioner pain: illustrative math shows "stack five 90%-accurate guards and you'll hit false positives 40% of the time," and a separate guide describes the real-world failure mode directly: "teams add aggressive guardrails early, generate a 15% false positive rate, train users to route around them." Multiple sources separately recommend running a new guardrail in shadow/monitor mode for 1-2 weeks before enforcing (P9), but every description frames this as manual discipline, never a built tool.

## The Project
A proxy that sits in front of a team's existing multi-guard pipeline (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom classifier stack), runs every real request through all configured guards in shadow mode — logging what each guard would have decided without blocking anything — and computes the actual blended false-positive rate across the full stack on real traffic, with per-guard attribution of which check is driving the compounding effect. Once a team flips to enforcement, the same harness keeps running continuously, so a later guard addition or input-pattern shift gets re-measured before it silently repeats the 15%-FPR "users route around it" failure mode. The centerpiece is the blended-FPR measurement and attribution, not another classifier.

## Tangible Impact
**Population**: engineering and trust-safety teams chaining 3+ independent guardrail classifiers (PII, jailbreak, content-policy, tone) in front of a customer-facing LLM product — a proxy for scale is the combined ~18k GitHub stars across NeMo Guardrails, Guardrails AI, and LLM Guard, implying thousands of teams already composing multiple checks by hand without measuring the compounded result.
**Mechanism**: today teams validate each guard in isolation against adversarial benchmarks, then enable blocking in production without ever measuring the *stack's* real-traffic FPR; per the cited math, five 90%-accurate guards can blend to ~40% FPR. A shadow-mode harness surfaces that blended number, and which guard is driving it, before enforcement goes live — turning a reactive discovery (support tickets after launch) into a pre-launch gate.
**Measure**: (1) blended FPR measured in shadow mode before enforcement vs. the FPR a team would otherwise discover post-launch via support tickets; (2) reduction in benign-user complaints attributable to guardrail false positives after adopting a measured rollout, vs. the team's prior ungated rollout baseline; (3) time from a guardrail-stack change to a trustworthy blended-FPR estimate (target: days of shadow traffic, not weeks of user complaints).

## Why Now
`humanbound-firewall#55` is a live, open ask from a maintained guardrail-firewall project itself this month, and the adjacent eval tooling needed to build this (promptfoo's adaptive red-team suite, NeMo evals, cheap reference-judge models for ground-truth labeling) is now mature and commodity-cheap — the integration, not any missing primitive, is the gap.

## Skill Angle
Trigger: a team hands over a pasted/exported sample of per-guard verdict logs (input, which guard fired, pass/block, and a ground-truth benign/malicious label where they have one). The skill computes today's blended FPR across the sample, attributes it per guard, and flags whether the stack looks safe to enforce — a one-shot pre-launch gate check before committing to the always-on shadow-mode proxy. The project is the live, continuously-running harness; the skill is the one-time sanity check that precedes adopting it.

## MVP Sketch
A lightweight reverse proxy in front of 3 guard checks of a team's choosing, logging real and would-be verdicts without blocking for 1-2 weeks against real traffic, computing blended FPR with per-guard attribution via a confusion-matrix report, using a labeled-benign sample (e.g., previously support-cleared traffic) as ground truth. Single experiment: replay a known traffic sample through naive "block on any flag" logic vs. the instrumented shadow-mode harness and surface the blended FPR number the team would not otherwise have discovered until live. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- Requires a labeled-benign ground-truth sample to compute real FPR; many teams won't have one ready and need to bootstrap from support-cleared history.
- A guardrail vendor could ship this shadow-mode dashboard directly (Netskope already ships an adjacent monitoring-only view).
- The digest's compounding-FPR math is illustrative blog arithmetic, not an independently validated dataset — the MVP backtest is explicitly designed to confirm or kill that premise on real traffic.
- Shadow mode can become a permanent excuse to never enforce; the tool needs a clear readiness threshold, not just a measurement, to avoid becoming shelfware.
